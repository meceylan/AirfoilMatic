import math

import numpy as np
import pytest

trapezoid = getattr(np, "trapezoid", None) or np.trapz  # numpy 1.x / 2.x

from airfoilmatic.geometry import (AirfoilError, close_small_te_gap, naca, naca4, naca5,
                                   parse_airfoil_file, split_at)
from airfoilmatic.topology import C_GRID, RECT, build_domain
from airfoilmatic.export import to_ansys_txt
from airfoilmatic.mesh import (first_cell_height, n_for_growth, plan_mesh, ratio_for,
                               two_end_spacing, geometric_length)
from airfoilmatic.gci import compute_gci
from airfoilmatic.i18n import STRINGS


# ------------------------------------------------------------------ geometry

def test_naca0012_thickness_and_closed_te():
    af = naca4("0012")
    xs = np.linspace(0.05, 0.95, 400)
    thick = np.interp(xs, af.xu, af.yu) - np.interp(xs, af.xl, af.yl)
    assert thick.max() == pytest.approx(0.12, abs=5e-4)
    assert xs[thick.argmax()] == pytest.approx(0.30, abs=0.01)
    assert af.te_gap < 1e-12
    assert af.xu[0] == af.xl[0] == 0.0


def test_naca4412_camber():
    af = naca4("4412")
    mid = 0.5 * (np.interp(0.4, af.xu, af.yu) + np.interp(0.4, af.xl, af.yl))
    assert mid == pytest.approx(0.04, abs=2e-3)


def test_naca23012_max_camber_position():
    af = naca5("23012")
    xs = np.linspace(0.05, 0.6, 500)
    camber = 0.5 * (np.interp(xs, af.xu, af.yu) + np.interp(xs, af.xl, af.yl))
    assert xs[camber.argmax()] == pytest.approx(0.15, abs=0.02)


def test_chord_scaling():
    af = naca("0012", chord=2.5)
    assert max(af.xu.max(), af.xl.max()) == pytest.approx(2.5)


@pytest.mark.parametrize("code", ["", "12", "123456", "abcd", "23112", "0000"])
def test_invalid_codes(code):
    with pytest.raises(AirfoilError):
        naca(code)


def test_cosine_spacing_clusters_at_both_ends():
    af = naca4("0012")
    dx = np.diff(af.xu)
    assert dx[0] < dx[len(dx) // 2] / 50
    assert dx[-1] < dx[len(dx) // 2] / 50


def test_split_at_03c():
    s = split_at(naca4("2412"))
    assert s.x_split == pytest.approx(0.3)
    assert s.upper_front[0][-1] == pytest.approx(0.3)
    assert s.upper_rear[0][0] == pytest.approx(0.3)
    assert s.split_upper[1] == pytest.approx(s.upper_front[1][-1])
    # no sliver segment next to the split
    assert np.diff(s.upper_rear[0])[0] > 1e-3
    assert np.diff(s.upper_front[0])[-1] > 1e-3


def _selig_text(af, header="TEST AIRFOIL"):
    xs = np.concatenate([af.xu[::-1], af.xl[1:]])
    ys = np.concatenate([af.yu[::-1], af.yl[1:]])
    return header + "\n" + "\n".join(f"  {x:.6f}  {y:.6f}" for x, y in zip(xs, ys))


def _lednicer_text(af):
    lines = ["TEST LEDNICER", f"{len(af.xu)}.  {len(af.xl)}.", ""]
    lines += [f"{x:.6f} {y:.6f}" for x, y in zip(af.xu, af.yu)]
    lines.append("")
    lines += [f"{x:.6f} {y:.6f}" for x, y in zip(af.xl, af.yl)]
    return "\n".join(lines)


@pytest.mark.parametrize("fmt", ["selig", "lednicer"])
def test_parse_files_roundtrip(fmt):
    ref = naca4("4412", n_points=81)
    text = _selig_text(ref) if fmt == "selig" else _lednicer_text(ref)
    af = parse_airfoil_file(text.encode(), chord=1.0)
    assert np.interp(0.5, af.xu, af.yu) == pytest.approx(np.interp(0.5, ref.xu, ref.yu), abs=1e-4)
    assert np.interp(0.5, af.xl, af.yl) == pytest.approx(np.interp(0.5, ref.xl, ref.yl), abs=1e-4)
    assert af.xu[0] == af.xl[0]


def test_parse_blunt_te_keeps_surfaces_separate():
    # Standard NACA 0012 (blunt TE, -0.1015 coefficient), Selig order
    x = 0.5 * (1 - np.cos(np.linspace(0, np.pi, 61)))
    yt = 0.6 * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    text = "\n".join(f"{a:.6f} {b:.6f}" for a, b in
                     zip(np.concatenate([x[::-1], x[1:]]), np.concatenate([yt[::-1], -yt[1:]])))
    af = parse_airfoil_file(text)
    assert af.yu[-1] == pytest.approx(yt[-1], abs=1e-6)
    assert af.yl[-1] == pytest.approx(-yt[-1], abs=1e-6)
    d = build_domain(split_at(af))
    assert d.blunt_te
    assert "te_closure" in [c.key for c in d.curves]


def test_tiny_te_gap_is_closed():
    af = naca4("0012")
    af.yu[-1] += 2e-5
    af = close_small_te_gap(af)
    assert af.te_gap == 0


# ------------------------------------------------------------------ topology / export

@pytest.mark.parametrize("kind", [C_GRID, RECT])
def test_domain_endpoints_connect(kind):
    s = split_at(naca4("4412"))
    d = build_domain(s, kind)
    # every curve end must touch another curve (end or interior)
    for c in d.curves:
        for p in ((c.x[0], c.y[0]), (c.x[-1], c.y[-1])):
            # distance to nearest other-curve polyline vertex or segment
            dmin = _dist_to_curves(p, [o for o in d.curves if o is not c])
            assert dmin < 1e-6, (c.key, p, dmin)


def _dist_to_curves(p, curves):
    best = np.inf
    p = np.asarray(p)
    for c in curves:
        a = np.column_stack([c.x[:-1], c.y[:-1]])
        b = np.column_stack([c.x[1:], c.y[1:]])
        ab = b - a
        tt = np.clip(np.einsum("ij,ij->i", p - a, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-30), 0, 1)
        proj = a + ab * tt[:, None]
        best = min(best, np.min(np.hypot(*(proj - p).T)))
    return best


def test_cgrid_arc_ends_on_split_lines_without_extra_piece():
    """The arc must end exactly where the split lines meet the outer boundary,
    so no short straight piece appears in front of x = 0.3c after Projection."""
    s = split_at(naca4("4412"))
    d = build_domain(s, C_GRID, r_inlet=10)
    arc, top, bot = d.get("inlet"), d.get("top"), d.get("bottom")
    up, low = d.get("split_up"), d.get("split_low")
    assert (arc.x[0], arc.y[0]) == (top.x[0], top.y[0]) == (up.x[-1], up.y[-1])
    assert (arc.x[-1], arc.y[-1]) == (bot.x[0], bot.y[0]) == (low.x[-1], low.y[-1])
    # identical strings in the exported file
    rows = [l.split() for l in to_ansys_txt(d).splitlines() if l]
    groups = {}
    for r in rows:
        groups.setdefault(int(r[0]), []).append((r[2], r[3]))
    keys = [c.key for c in d.curves]
    g = lambda k: groups[keys.index(k) + 1]
    assert g("inlet")[0] == g("top")[0] == g("split_up")[-1]
    assert g("inlet")[-1] == g("bottom")[0] == g("split_low")[-1]
    p = plan_mesh(d, s, 2e6)
    assert "g_top_front" not in [e.group for e in p.edges]


def test_txt_format():
    d = build_domain(split_at(naca4("0012")))
    txt = to_ansys_txt(d)
    rows = [l.split() for l in txt.strip().splitlines()]
    assert all(len(r) == 5 for r in rows)
    groups = sorted({int(r[0]) for r in rows})
    assert groups == list(range(1, len(d.curves) + 1))
    # no consecutive duplicate points inside a group
    prev = None
    for r in rows:
        key = (r[0], r[2], r[3])
        assert key != prev
        prev = key


# ------------------------------------------------------------------ mesh sizing

def test_first_cell_height_reference():
    # Re = 2e6, y+ = 1 -> ~1.2e-5 c (widely used y+ calculators give 1.2-1.3e-5)
    assert first_cell_height(2e6, 1.0, 1.0) == pytest.approx(1.23e-5, rel=0.03)


def test_geometric_helpers():
    r = ratio_for(10.0, 1e-5, 120)
    assert geometric_length(1e-5, r, 120) == pytest.approx(10.0, rel=1e-9)
    n = n_for_growth(10.0, 1e-5, 1.1)
    assert geometric_length(1e-5, 1.1, n) >= 10.0
    assert geometric_length(1e-5, 1.1, n - 1) < 10.0
    n, r = two_end_spacing(0.7, 0.001, 0.01)
    assert r ** (n - 1) == pytest.approx(10.0)
    assert geometric_length(0.001, r, n) == pytest.approx(0.7, rel=0.02)


@pytest.mark.parametrize("kind", [C_GRID, RECT])
def test_plan_consistency(kind):
    s = split_at(naca4("4412"))
    d = build_domain(s, kind)
    p = plan_mesh(d, s, 2e6)
    by_group = {}
    for e in p.edges:
        by_group.setdefault(e.group, []).append(e)
    assert all(e.n == p.n_normal for e in by_group["g_normal"])
    assert by_group["g_af_front"][0].n == p.n_front
    n_tf = by_group["g_top_front"][0].n if "g_top_front" in by_group else 0
    assert by_group["g_inlet"][0].n + n_tf == p.n_front
    assert by_group["g_top_mid"][0].n == by_group["g_af_rear"][0].n == p.n_rear
    assert all(e.n == p.n_normal for e in by_group["g_outlet"])
    assert p.cells == 2 * p.n_normal * (p.n_front + p.n_rear + p.n_wake)
    for e in by_group["g_normal"]:
        assert e.ds_min == pytest.approx(p.dy1, rel=1e-6)
    assert p.max_growth <= 1.1 + 1e-9


def test_plan_blunt_te_outlet_counts():
    x = 0.5 * (1 - np.cos(np.linspace(0, np.pi, 61)))
    yt = 0.6 * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    text = "\n".join(f"{a:.6f} {b:.6f}" for a, b in
                     zip(np.concatenate([x[::-1], x[1:]]), np.concatenate([yt[::-1], -yt[1:]])))
    s = split_at(parse_airfoil_file(text))
    d = build_domain(s)
    p = plan_mesh(d, s, 2e6)
    out = [e for e in p.edges if e.group == "g_outlet"]
    assert all(e.n == p.n_normal + p.n_closure // 2 for e in out)


def test_refinement_family_scales_cells():
    s = split_at(naca4("0012"))
    d = build_domain(s)
    k = math.sqrt(2)
    cells = [plan_mesh(d, s, 2e6, refine=f).cells for f in (1 / k, 1.0, k)]
    assert cells[1] / cells[0] == pytest.approx(2.0, rel=0.1)
    assert cells[2] / cells[1] == pytest.approx(2.0, rel=0.1)


# ------------------------------------------------------------------ GCI

def test_gci_celik_example():
    # Celik et al. (2008), Table 1, phi = dimensionless reattachment length
    g = compute_gci(18000, 8000, 4500, 6.063, 5.972, 5.863)
    assert g.r21 == pytest.approx(1.5)
    assert g.r32 == pytest.approx(1.333, abs=1e-3)
    assert g.p == pytest.approx(1.53, abs=0.01)
    assert g.phi_ext == pytest.approx(6.1685, abs=1e-3)
    assert 100 * g.e_a21 == pytest.approx(1.5, abs=0.05)
    assert 100 * g.e_ext21 == pytest.approx(1.7, abs=0.05)
    assert 100 * g.gci_fine == pytest.approx(2.2, abs=0.05)
    assert not g.oscillatory


def test_gci_order_check():
    with pytest.raises(ValueError):
        compute_gci(1000, 2000, 500, 1, 1.1, 1.2)


# ------------------------------------------------------------------ i18n

def test_all_strings_have_both_languages():
    for key, entry in STRINGS.items():
        assert entry.get("tr") and entry.get("en"), key


def test_all_keys_used_by_domain_and_plan_are_translated():
    for kind in (C_GRID, RECT):
        s = split_at(naca4("4412"))
        d = build_domain(s, kind)
        p = plan_mesh(d, s, 2e6)
        keys = {c.key for c in d.curves}
        for e in p.edges:
            keys |= {e.group, e.small_end, *e.edges}
        missing = [k for k in keys if k not in STRINGS]
        assert not missing, missing


# ------------------------------------------------------------------ review fixes

@pytest.mark.parametrize("P", [10, 20, 30, 40, 50])
def test_naca5_table_gives_design_cl_03(P):
    """Each (m, k1) row must give ideal Cl = 0.3 (thin-airfoil theory, Cl_i = pi*A1)."""
    from airfoilmatic.geometry import NACA5_TABLE
    m, k1 = NACA5_TABLE[P]
    th = np.linspace(0, np.pi, 200001)
    x = 0.5 * (1 - np.cos(th))
    dyc = np.where(x <= m, k1 / 6 * (3 * x**2 - 6 * m * x + m**2 * (3 - m)), -k1 * m**3 / 6)
    cl_i = 2 * trapezoid(dyc * np.cos(th), th)
    assert cl_i == pytest.approx(0.3, abs=0.01)


def test_extreme_naca_rejected():
    with pytest.raises(AirfoilError):
        naca("9999")


def test_numeric_selig_header_not_taken_as_lednicer():
    ref = naca4("2412", n_points=61)
    af = parse_airfoil_file(_selig_text(ref, header="2412 15"))
    assert np.interp(0.5, af.xu, af.yu) == pytest.approx(np.interp(0.5, ref.xu, ref.yu), abs=1e-4)


def test_rect_domain_too_small_rejected():
    s = split_at(naca4("0012", chord=30))
    with pytest.raises(ValueError):
        build_domain(s, RECT, r_inlet=1, l_top=1, l_bottom=1)


def test_export_keeps_curve_end_points_small_chord():
    s = split_at(naca4("0012", chord=0.01))
    d = build_domain(s, C_GRID, r_inlet=0.2, l_wake=0.4)
    rows = [l.split() for l in to_ansys_txt(d).strip().splitlines()]
    for g, c in enumerate(d.curves, start=1):
        pts = [r for r in rows if int(r[0]) == g]
        assert float(pts[-1][2]) == pytest.approx(c.x[-1], abs=1e-9)
        assert float(pts[-1][3]) == pytest.approx(c.y[-1], abs=1e-9)


def test_low_reynolds_rejected():
    with pytest.raises(ValueError):
        first_cell_height(1.0, 1.0, 1.0)


def test_gci_flags_divergence_and_degenerate():
    g = compute_gci(1e6, 5e5, 2.5e5, 1.00, 1.04, 1.06)
    assert g.diverging
    with pytest.raises(ValueError):
        compute_gci(1e6, 5e5, 2.5e5, 1.0, 1.02, 1.04)


# ------------------------------------------------------------------ mesh quality

def test_quality_bands():
    from airfoilmatic.quality import rate_skewness, rate_orthogonal
    assert rate_skewness(0.016) == "q_excellent"
    assert rate_skewness(0.762) == "q_good"
    assert rate_skewness(0.90) == "q_acceptable"
    assert rate_skewness(0.99) == "q_unacceptable"
    assert rate_orthogonal(0.995) == "q_excellent"
    assert rate_orthogonal(0.027) == "q_bad"
    assert rate_orthogonal(0.18) == "q_acceptable"
    assert rate_orthogonal(0.0005) == "q_unacceptable"
    with pytest.raises(ValueError):
        rate_skewness(1.5)


def test_airfoil_edges_all_run_le_to_te():
    """Same direction on upper and lower edges -> one Edge Sizing bias works for both."""
    d = build_domain(split_at(naca4("4412")))
    for k in ("af_upper_front", "af_lower_front", "af_upper_rear", "af_lower_rear"):
        c = d.get(k)
        assert c.x[-1] > c.x[0], k


def test_wake_cap_limits_last_element():
    s = split_at(naca4("0012"))
    d = build_domain(s)
    p = plan_mesh(d, s, 2e6, max_wake_cell=0.5)
    w = [e for e in p.edges if e.group == "g_wake"][0]
    assert w.ds_max == pytest.approx(0.5, rel=0.05)
    assert w.ds_min == pytest.approx(0.001, rel=0.05)


def test_line_selection():
    from airfoilmatic.topology import select_lines, line_warnings, SPLIT_LINES
    s = split_at(naca4("4412"))
    d = build_domain(s)
    v = select_lines(d, ["front_axis", "wake_axis"])
    assert [c.key for c in v.by_kind("split")] == ["front_axis", "wake_axis"]
    assert len(d.by_kind("split")) == 6  # original untouched
    assert len(select_lines(d, []).by_kind("split")) == 0
    assert len(select_lines(d, SPLIT_LINES).by_kind("split")) == 6
    groups = {l.split()[0] for l in to_ansys_txt(v).splitlines() if l}
    assert len(groups) == 4 + 4 + 2
    assert line_warnings(["wake_axis"]) == [("single_line", "wake_axis")]
    assert line_warnings([]) == [] and line_warnings(["front_axis", "wake_axis"]) == []

def test_low_growth_family_does_not_overflow():
    import math as _m
    s = split_at(naca4("4412"))
    d = build_domain(s)
    for k in (1 / _m.sqrt(2), 1.0, _m.sqrt(2), 2.0):
        for re_ in (1e5, 2e6, 1e9):
            plan_mesh(d, s, re_, refine=k, growth=1.01, y_plus=0.05)


def test_error_messages_translated():
    from airfoilmatic.i18n import tr_error
    with pytest.raises(AirfoilError) as e:
        naca("9999")
    assert tr_error(e.value, "tr") != str(e.value)
    assert tr_error(e.value, "en") == str(e.value)


def test_blunt_te_option():
    sharp = naca4("0012")
    blunt = naca4("0012", blunt_te=True)
    assert sharp.te_gap < 1e-12
    assert blunt.te_gap == pytest.approx(2 * 0.6 * (0.2969 - 0.126 - 0.3516 + 0.2843 - 0.1015), rel=1e-6)
    d = build_domain(split_at(blunt))
    assert d.blunt_te and "te_closure" in [c.key for c in d.curves]
    p = plan_mesh(d, split_at(blunt), 2e6)
    assert any(e.group == "g_te_closure" for e in p.edges)
    from airfoilmatic.topology import select_lines
    keys = [c.key for c in select_lines(d, ["front_axis", "wake_axis"]).by_kind("split")]
    assert "te_closure" in keys and "wake_axis" in keys


# ------------------------------------------------------------------ Fluent helper

def test_freestream_components():
    from airfoilmatic.fluent import freestream, speed_for_reynolds
    fs = freestream(4.25, 40.0, 1.0)
    assert fs.ux == pytest.approx(40 * math.cos(math.radians(4.25)))
    assert fs.uy == pytest.approx(40 * math.sin(math.radians(4.25)))
    assert math.hypot(fs.ux, fs.uy) == pytest.approx(40.0)
    # drag along the free stream, lift perpendicular, both unit vectors
    assert fs.drag[0] * fs.ux + fs.drag[1] * fs.uy == pytest.approx(40.0)
    assert fs.lift[0] * fs.drag[0] + fs.lift[1] * fs.drag[1] == pytest.approx(0.0, abs=1e-12)
    assert math.hypot(*fs.lift) == pytest.approx(1.0)
    assert fs.lift[1] > 0  # lift points up at small positive AoA
    assert fs.reynolds == pytest.approx(1.225 * 40 / 1.7894e-5)
    assert speed_for_reynolds(fs.reynolds, 1.0) == pytest.approx(40.0)
    zero = freestream(0.0, 10.0, 1.0)
    assert zero.uy == 0 and abs(zero.lift[0]) == 0 and zero.lift[1] == 1
    with pytest.raises(ValueError):
        freestream(4, 0, 1)
