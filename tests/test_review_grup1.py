"""Findings of the independent review of 2026-11-27, group 1 (wrong results, crashes, memory)."""
import math
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.blockmesh import MAX_CELLS, WALL, BlockMesh, build_cgrid, mesh_family, quality
from airfoilmatic.gci import gci
from airfoilmatic.geometry import naca, split_at
from airfoilmatic.i18n import ERRORS_TR
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.polar import merge_reports, polar, read_report
from airfoilmatic.topology import build_domain

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")


# ---------------------------------------------------------------- 1. chordwise spacing of the .msh
def wall_cells(m, upper=True):
    """(x of the face centre, face length) of the wall faces on one side, LE first."""
    w = m.faces[m.face_zone == WALL]
    p0, p1 = m.nodes[w[:, 0]], m.nodes[w[:, 1]]
    mid = 0.5 * (p0 + p1)
    sel = (mid[:, 1] > 0) if upper else (mid[:, 1] < 0)
    x, L = mid[sel, 0], np.hypot(*(p1 - p0)[sel].T)
    o = np.argsort(x)
    return x[o], L[o]


@pytest.mark.parametrize("kw, at_le, at_split, at_te", [
    (dict(ds_le=0.02, ds_split=0.005), 0.02, 0.005, None),       # LE coarser than the split line
    (dict(ds_te=0.02), None, 0.01, 0.02),                        # TE coarser than the split line
    (dict(), 0.001, 0.01, 0.001),                                # defaults (unchanged)
])
def test_chordwise_spacing_ends_where_asked(kw, at_le, at_split, at_te):
    af = split_at(naca("0012"))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    m = build_cgrid(d, af, plan_mesh(d, af, 2.0e6, **kw))
    x, L = wall_cells(m)
    if at_le is not None:
        assert L[0] == pytest.approx(at_le, rel=0.1)
    if at_te is not None:
        assert L[-1] == pytest.approx(at_te, rel=0.1)
    before = L[x < d.x_split][-1]
    after = L[x > d.x_split][0]
    assert before == pytest.approx(at_split, rel=0.15) and after == pytest.approx(at_split, rel=0.15)


# ---------------------------------------------------------------- 2-3. GCI order of convergence
@pytest.mark.parametrize("cells, values", [
    ([100000, 80000, 20000], [0.5, 0.499, 0.49]),       # OverflowError before
    ([120000, 60000, 15000], [1.0, 1.002, 1.006]),      # ZeroDivisionError before
    ([100000, 70000, 20000], [0.6, 0.598, 0.59]),       # wrong p (0.127) before
])
def test_gci_never_raises_an_arithmetic_error(cells, values):
    try:
        g = gci(cells, values)
    except ValueError as e:
        assert str(e) in ERRORS_TR
        return
    assert math.isfinite(g.p) and g.p > 0
    # the returned p solves Celik's equation
    h = [1 / math.sqrt(n) for n in sorted(cells, reverse=True)]
    f = [v for _, v in sorted(zip(cells, values), key=lambda t: -t[0])]
    r21, r32 = h[1] / h[0], h[2] / h[1]
    e21, e32 = f[1] - f[0], f[2] - f[1]
    s = math.copysign(1.0, e32 / e21)
    rhs = abs(math.log(abs(e32 / e21)) + math.log((r21 ** g.p - s) / (r32 ** g.p - s))) / math.log(r21)
    assert g.p == pytest.approx(rhs, rel=1e-6)


def test_gci_takes_the_smaller_order_when_two_solve_it():
    """Roots near 0.32 and 1.80: the smaller order gives the larger (safer) uncertainty."""
    g = gci([100000, 70000, 20000], [0.6, 0.598, 0.59])
    assert g.p == pytest.approx(0.319, abs=0.01)


def test_celik_example_unchanged():
    g = gci([18000, 8000, 4500], [6.063, 5.972, 5.863])
    assert g.p == pytest.approx(1.53, abs=0.01) and 100 * g.gci_fine == pytest.approx(2.2, abs=0.05)
    assert g.monotonic and not g.diverging


def test_monotonic_divergence_is_flagged():
    """Stern et al. 2001: the difference grows as the mesh is refined (|e21| > |e32|)."""
    g = gci([40000, 10000, 2500], [1.30, 1.10, 1.00])
    assert g.diverging


def test_app_shows_divergence_instead_of_a_gci():
    at = AppTest.from_file(APP, default_timeout=240).run()
    for k, v in dict(gci_n1=40000, gci_n2=10000, gci_n3=2500, gci_cl1=1.30, gci_cl2=1.10, gci_cl3=1.00).items():
        [w for w in at.number_input if w.key == k][0].set_value(v)
    at = at.run()
    assert not at.exception
    from airfoilmatic.i18n import tr
    text = " ".join(d.value.to_string() for d in at.dataframe)
    assert tr("gci_div", "tr")[:12] in text


def test_gci_errors_reach_the_user_as_messages():
    at = AppTest.from_file(APP, default_timeout=240).run()
    for k, v in dict(gci_n1=100000, gci_n2=80000, gci_n3=20000, gci_cl1=0.5, gci_cl2=0.499, gci_cl3=0.49).items():
        [w for w in at.number_input if w.key == k][0].set_value(v)
    at = at.run()
    assert not at.exception


# ---------------------------------------------------------------- 4. continued sweep
def report(rows):
    head = '"r"\n"Iteration" "x"\n("Iteration" "alpha" "cd" "cl")\n'
    return read_report(head + "\n".join(f"{i} {a} 0.01 {c}" for i, a, c in rows))


def test_rows_of_the_abandoned_run_are_dropped():
    d8, d12, d14 = (math.radians(a) for a in (8, 12, 14))
    old = report([(i, d8, 0.9) for i in range(1, 101)] + [(i, d12, 9.0) for i in range(101, 301)])
    new = report([(i, d12, 1.2) for i in range(101, 181)] + [(i, d14, 1.3) for i in range(181, 251)])
    for files in ([old, new], [new, old]):            # upload order does not matter
        rows = {round(r.aoa): r for r in polar(merge_reports(files), "alpha", "cl", "cd")}
        assert rows[12].cl == pytest.approx(1.2) and rows[12].last == 180
        assert rows[14].cl == pytest.approx(1.3)


def test_restart_inside_one_file_drops_the_abandoned_rows():
    d12, d14 = math.radians(12), math.radians(14)
    rep = report([(i, d12, 9.0) for i in range(101, 301)] + [(i, d12, 1.2) for i in range(101, 181)]
                 + [(i, d14, 1.3) for i in range(181, 251)])
    rows = {round(r.aoa): r for r in polar(rep, "alpha", "cl", "cd")}
    assert rows[12].cl == pytest.approx(1.2)


# ---------------------------------------------------------------- 5. cell cap
def test_cell_cap_refuses_a_huge_mesh():
    af = split_at(naca("4412"))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    plan = plan_mesh(d, af, 2.0e6, y_plus=0.05, growth=1.01, ds_split=0.002)
    assert plan.cells > MAX_CELLS == 1_000_000
    with pytest.raises(ValueError) as e:
        build_cgrid(d, af, plan)
    assert str(e.value) in ERRORS_TR


def test_family_refused_before_building_when_the_fine_mesh_is_too_big():
    af = split_at(naca("4412"))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    kw = dict(y_plus=0.05, growth=1.01)               # medium 860 430, fine 1 721 664 cells
    assert plan_mesh(d, af, 2.0e6, **kw).cells < MAX_CELLS < plan_mesh(d, af, 2.0e6, refine=2 ** 0.5, **kw).cells
    with pytest.raises(ValueError):
        mesh_family(d, af, 2.0e6, **kw)


def test_app_says_the_mesh_is_too_big():
    at = AppTest.from_file(APP, default_timeout=240).run()
    mode = [w for w in at.radio if w.key == "mesh_mode"][0]
    mode.set_value(mode.options[1])
    at = at.run()
    for k, v in (("ds_split", 0.0001), ("ds_le", 0.0001), ("ds_te", 0.0001)):    # 2.6 M cells
        [w for w in at.number_input if w.key == k][0].set_value(v)
    at = at.run()
    assert not at.exception
    assert not any(el.proto.id.endswith("msh_download") for el in at.get("download_button"))
    assert any(ERRORS_TR["The mesh file is limited to 1 000 000 cells"][:20] in e.value for e in at.error)


# ---------------------------------------------------------------- 6. upload limit
def test_upload_limit_fits_long_report_files():
    text = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    line = [l for l in text.splitlines() if l.startswith("maxUploadSize")][0]
    assert int(line.split("=")[1]) >= 50


# ---------------------------------------------------------------- 7. inputs kept while hidden
def test_journal_inputs_survive_an_empty_sweep():
    at = AppTest.from_file(APP, default_timeout=240).run()
    [w for w in at.text_input if w.key == "jou_folder"][0].set_value("C:/runs")
    [w for w in at.number_input if w.key == "jou_iter"][0].set_value(500)
    at = at.run()
    [w for w in at.radio if w.key == "sweep_mode"][0].set_value("list")
    at = at.run()                                     # empty list: the journal is hidden
    [w for w in at.text_input if w.key == "sweep_list"][0].set_value("1, 2")
    at = at.run()
    assert not at.exception
    assert [w for w in at.text_input if w.key == "jou_folder"][0].value == "C:/runs"
    assert [w for w in at.number_input if w.key == "jou_iter"][0].value == 500


# ---------------------------------------------------------------- 8. orthogonal quality precision
def test_orthogonal_quality_does_not_change_when_the_mesh_moves():
    af = split_at(naca("4412"))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    m = build_cgrid(d, af, plan_mesh(d, af, 3.0e7))
    moved = BlockMesh(m.nodes + np.array([20.0, -7.0]), m.cells, m.faces, m.face_zone)
    assert quality(moved)[1].min() == pytest.approx(quality(m)[1].min(), abs=1e-4)


@pytest.mark.parametrize("name, words", [
    ("CHANGELOG.md", ("1 000 000", "Stern", "bisect", "abandoned run", "50 MB", "ıraksıyor", "yarıda bırakılan")),
    ("README.md", ("1 000 000",)), ("README.en.md", ("1 000 000",))])
def test_docs_describe_the_group1_fixes(name, words):
    text = (ROOT / name).read_text(encoding="utf-8")
    for w in words:
        assert w in text, w
