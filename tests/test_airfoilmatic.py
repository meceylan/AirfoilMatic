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
    assert line_warnings(["wake_axis", "te_up", "te_low"]) == [("wake_without_front", "wake_axis")]

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


# ------------------------------------------------------------------ ui (V0.4.2)

def test_css_has_no_unfilled_placeholders():
    import re as _re
    from airfoilmatic import ui
    out = ui.css()
    assert out.startswith("<style>") and out.endswith("</style>")
    assert "CRYSTAL" not in out and "MOBILEpx" not in out and '"FONT"' not in out
    # every var() used is defined in the .stApp block
    used = set(_re.findall(r"var\((--am-[a-z0-9-]+)\)", out))
    defined = set(_re.findall(r"(--am-[a-z0-9-]+):", out))
    assert used <= defined, used - defined


def test_ui_html_is_escaped():
    from airfoilmatic import ui
    assert "<script>" not in ui.cards_html([("<script>", "1 mm", "x", True)])
    assert "am-crystal" in ui.cards_html([("a", "1", "", True)])
    assert "<b>Beta</b>" in ui.note_html("Beta\nbody")


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_footer_has_developer_links(lang):
    from airfoilmatic import ui
    html = ui.footer_html(lang, "Dev")
    assert ui.DEVELOPER["linkedin"] in html and ui.DEVELOPER["github"] in html
    assert ui.DEVELOPER["university"][lang] in html


def test_tables_html():
    from airfoilmatic import ui
    rows = [{"Ayar": "First Layer Height", "Değer": "1e-05 m <b>"}]
    html = ui.table_html(rows)
    assert "<table" in html and "&lt;b&gt;" in html
    cards = ui.row_cards_html([{"A": "g1", "B": 1, "C": 2}], ["A", "C"])
    assert "g1" in cards and ">C<" in cards and ">B<" not in cards
    assert ui.table_html([]) == "" and ui.row_cards_html([]) == ""


# ------------------------------------------------------------------ second review: sizing

def _edge(plan, group):
    return [e for e in plan.edges if e.group == group][0]


def test_small_end_label_points_at_the_smallest_element():
    """The table tells the user where to put the small elements (bias direction).
    When the TE element is larger than the split-line element (inflation mode keeps the
    TE element >= 1.5x the last layer), the small end of the rear edge is the split line."""
    s = split_at(naca4("0012"))
    d = build_domain(s)
    normal = plan_mesh(d, s, 2e6, ds_te=0.003, ds_split=0.01)
    assert _edge(normal, "g_af_rear").small_end == "end_te"
    assert _edge(normal, "g_af_front").small_end == "end_le"

    flipped = plan_mesh(d, s, 2e6, ds_te=0.012, ds_split=0.01)   # e.g. Re 1e5, growth 1.15
    rear = _edge(flipped, "g_af_rear")
    assert rear.ds_min == pytest.approx(0.01, rel=0.02) and rear.ds_max == pytest.approx(0.012, rel=0.02)
    assert rear.small_end == "end_split"
    assert _edge(flipped, "g_top_mid").small_end == "end_split"

    le_big = plan_mesh(d, s, 2e6, ds_le=0.02, ds_split=0.01)
    assert _edge(le_big, "g_af_front").small_end == "end_split"


def test_small_end_label_low_reynolds_inflation_defaults():
    """App defaults (growth 1.15, coverage 1.5) at Re = 1e5: the last inflation layer is
    ~8 mm, so the TE element (12 mm) is larger than the split element (10 mm)."""
    from airfoilmatic.mesh import plan_inflation
    s = split_at(naca4("0012"))
    d = build_domain(s, r_inlet=15)
    infl = plan_inflation(1e5, 1.0, growth=1.15, coverage=1.5)
    ds_te = max(0.001, 0.003, 1.5 * infl.last_layer)
    assert ds_te > 0.01
    p = plan_mesh(d, s, 1e5, max_wake_cell=0.5, ds_te=ds_te, growth=1.15)
    assert _edge(p, "g_af_rear").small_end == "end_split"
    assert _edge(p, "g_wake").small_end == "end_te"


def test_small_end_keys_are_translated():
    s = split_at(naca4("0012"))
    d = build_domain(s)
    p = plan_mesh(d, s, 2e6, ds_te=0.012, ds_le=0.02, ds_split=0.01)
    missing = [e.small_end for e in p.edges if e.small_end not in STRINGS]
    assert not missing, missing


def test_first_cell_longer_than_an_edge_is_rejected():
    """Rectangle with a 1 m inlet distance, c = 1.9 m, Re = 1e3, y+ = 65: the first cell
    (1.2 m) is longer than the front axis. The plan used to show Bias Factor = 1e+48."""
    s = split_at(naca4("4412", chord=1.9))
    d = build_domain(s, RECT, r_inlet=1.0, l_wake=20, l_top=15, l_bottom=15)
    with pytest.raises(ValueError):
        plan_mesh(d, s, 1e3, y_plus=65.0)
    with pytest.raises(ValueError):
        ratio_for(1.0, 1.2, 9)


def test_capped_wake_does_not_depend_on_wake_growth():
    """With the far-field cap (inflation mode) first cell, last cell and length fix the
    progression, so the wake growth input cannot change it; the app hides the input."""
    s = split_at(naca4("0012"))
    d = build_domain(s, r_inlet=15)
    plans = [plan_mesh(d, s, 2e6, max_wake_cell=0.5, ds_te=0.0065, wake_growth=g) for g in (1.05, 1.1, 1.3)]
    assert len({(_edge(p, "g_wake").n, round(_edge(p, "g_wake").bias, 6)) for p in plans}) == 1


# ------------------------------------------------------------------ second review: files

def _loop(af):
    """Selig order: TE -> upper -> LE -> lower -> TE."""
    return np.concatenate([af.xu[::-1], af.xl[1:]]), np.concatenate([af.yu[::-1], af.yl[1:]])


def _same_airfoil(af, ref, tol=1e-4):
    assert af.te_gap == pytest.approx(ref.te_gap, abs=tol)
    assert len(af.xu) == len(ref.xu) and len(af.xl) == len(ref.xl)
    for x in (0.1, 0.5, 0.9):
        assert np.interp(x, af.xu, af.yu) == pytest.approx(np.interp(x, ref.xu, ref.yu), abs=tol)
        assert np.interp(x, af.xl, af.yl) == pytest.approx(np.interp(x, ref.xl, ref.yl), abs=tol)


def test_parse_utf8_bom_keeps_first_point():
    """A header-less file saved as 'UTF-8 with BOM' lost its first point (the upper TE),
    which opened the trailing edge by 0.16% c."""
    ref = close_small_te_gap(naca4("2412", n_points=41))
    x, y = _loop(ref)
    body = "\n".join(f"{a:.6f} {b:.6f}" for a, b in zip(x, y))
    af = parse_airfoil_file(("﻿" + body).encode("utf-8"))
    _same_airfoil(af, ref)


def test_parse_utf16_file():
    ref = close_small_te_gap(naca4("2412", n_points=41))
    x, y = _loop(ref)
    body = "TEST\n" + "\n".join(f"{a:.6f} {b:.6f}" for a, b in zip(x, y))
    _same_airfoil(parse_airfoil_file(body.encode("utf-16")), ref)


@pytest.mark.parametrize("scale,fmt", [(1000.0, "{:.3f} {:.3f}"), (1000.0, "{:.0f} {:.0f}"), (100.0, "{:.4f} {:.4f}")])
def test_parse_physical_units_keeps_first_point(scale, fmt):
    """Coordinates in mm (or percent) with the TE above y = 1.5: the first row looked like
    a numeric title line and was dropped."""
    ref = close_small_te_gap(naca4("2412", n_points=41))
    x, y = _loop(ref)
    body = "\n".join(fmt.format(a * scale, b * scale + 3.0) for a, b in zip(x, y))
    af = parse_airfoil_file(body)
    assert len(af.xu) == len(ref.xu)
    assert af.te_gap == pytest.approx(0.0, abs=2e-3 if "0f" in fmt else 1e-5)
    assert af.xu[-1] == pytest.approx(1.0)


def test_parse_lednicer_in_mm_still_detected():
    ref = close_small_te_gap(naca4("2412", n_points=41))
    lines = ["TEST", f"{len(ref.xu)} {len(ref.xl)}"]
    lines += [f"{a * 1000:.3f} {b * 1000:.3f}" for a, b in zip(ref.xu, ref.yu)]
    lines += [f"{a * 1000:.3f} {b * 1000:.3f}" for a, b in zip(ref.xl, ref.yl)]
    _same_airfoil(parse_airfoil_file("\n".join(lines)), ref)


@pytest.mark.parametrize("sep", ["\t", ";", "  "])
def test_parse_decimal_comma(sep):
    """Excel in a Turkish/European locale writes 0,500000 instead of 0.500000."""
    ref = close_small_te_gap(naca4("2412", n_points=41))
    x, y = _loop(ref)
    body = "\n".join(f"{a:.6f}{sep}{b:.6f}".replace(".", ",") for a, b in zip(x, y))
    _same_airfoil(parse_airfoil_file(body), ref)


@pytest.mark.parametrize("sep", [";", ",", ", ", " ; "])
def test_parse_other_separators(sep):
    ref = close_small_te_gap(naca4("2412", n_points=41))
    x, y = _loop(ref)
    body = "\n".join(f"{a:.6f}{sep}{b:.6f}" for a, b in zip(x, y))
    _same_airfoil(parse_airfoil_file(body), ref)


@pytest.mark.parametrize("order", ["blocks", "loop"])
def test_parse_files_that_start_at_the_leading_edge(order):
    """LE -> TE upper then LE -> TE lower (Lednicer without the count line), or one loop
    LE -> upper -> TE -> lower -> LE."""
    ref = close_small_te_gap(naca4("2412", n_points=41))
    if order == "blocks":
        x, y = np.concatenate([ref.xu, ref.xl]), np.concatenate([ref.yu, ref.yl])
    else:
        x, y = np.concatenate([ref.xu, ref.xl[::-1][1:]]), np.concatenate([ref.yu, ref.yl[::-1][1:]])
    body = "\n".join(f"{a:.6f} {b:.6f}" for a, b in zip(x, y))
    _same_airfoil(parse_airfoil_file(body), ref)


# ------------------------------------------------------------------ second review: topology

def _proper_crossings(domain):
    """Number of places where two different curves cross each other (touching at a
    shared end point, or an end point lying on a straight boundary, does not count)."""
    segs, owner = [], []
    for i, c in enumerate(domain.curves):
        p = np.column_stack([c.x, c.y])
        segs.append(np.hstack([p[:-1], p[1:]]))
        owner += [i] * (len(p) - 1)
    s, o = np.vstack(segs), np.array(owner)
    a, b, c, e = s[:, None, :2], s[:, None, 2:], s[None, :, :2], s[None, :, 2:]

    def cross(u, v):
        return u[..., 0] * v[..., 1] - u[..., 1] * v[..., 0]

    eps = 1e-12
    hit = ((cross(b - a, c - a) * cross(b - a, e - a) < -eps)
           & (cross(e - c, a - c) * cross(e - c, b - c) < -eps) & (o[:, None] != o[None, :]))
    return int(hit.sum()) // 2


@pytest.mark.parametrize("kind", [C_GRID, RECT])
@pytest.mark.parametrize("code", ["0012", "4412", "9112", "2140", "23012", "0040"])
def test_no_curve_crosses_another(kind, code):
    """Strongly cambered sections bulge to x < 0 above the leading edge; the front axis,
    the split lines and the boundaries must still meet the airfoil only at their ends."""
    d = build_domain(split_at(close_small_te_gap(naca(code))), kind, r_inlet=15, l_wake=20, l_top=15, l_bottom=12)
    assert _proper_crossings(d) == 0


def test_crossing_detector_finds_a_crossing():
    d = build_domain(split_at(naca4("0012")), C_GRID, r_inlet=15)
    wake = d.get("wake_axis")
    wake.y = wake.y + np.linspace(0.0, 30.0, len(wake.y))   # push the wake axis through the top boundary
    assert _proper_crossings(d) > 0
