"""The app's Fluent .msh for the rectangular domain.

The six blocks and the Edge Sizing plan are those of the C-grid; only the side of each front block
opposite the airfoil front is a chain instead of an arc: half of the inlet edge (``g_inlet``) and the
front segment of the top / bottom boundary (``g_top_front``), meeting at the inlet corner (the
"Side" vertex of the Ansys Face Meshing note).
"""
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic import library as lib
from airfoilmatic.blockmesh import INLET, OUTLET, WALL, build_cgrid, mesh_family, quality, read_fluent_msh, to_fluent_msh
from airfoilmatic.geometry import close_small_te_gap, naca, parse_airfoil_file, split_at
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.topology import RECT, build_domain

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def make(af, kind=RECT, **kw):
    d = build_domain(af, kind, r_inlet=15.0, l_wake=20.0, l_top=15.0, l_bottom=15.0, **kw)
    plan = plan_mesh(d, af, 2.0e6)
    return d, plan, build_cgrid(d, af, plan)


@pytest.mark.parametrize("code, blunt", [("4412", False), ("0012", False), ("0012", True)])
def test_rectangle_mesh_has_the_planned_cells_and_good_quality(code, blunt):
    d, plan, m = make(split_at(naca(code, blunt_te=blunt)))
    assert m.n_cells == plan.cells
    skew, oq = quality(m)
    assert skew.max() < 0.6 and oq.min() > 0.6       # worst: the inlet corners (90 degrees split in two)


def test_rectangle_boundaries():
    d, _, m = make(split_at(naca("4412")))
    f = m.faces
    mid = 0.5 * (m.nodes[f[:, 0]] + m.nodes[f[:, 1]])
    inlet, outlet = mid[m.face_zone == INLET], mid[m.face_zone == OUTLET]
    x0, x1, yt, yb = d.x_inlet, d.x_exit, d.y_top, -d.y_bottom
    # inlet: the left edge and the whole top and bottom boundary
    on_left = np.isclose(inlet[:, 0], x0)
    on_tb = np.isclose(inlet[:, 1], yt) | np.isclose(inlet[:, 1], yb)
    assert np.all(on_left | on_tb) and on_left.any() and on_tb.any()
    assert inlet[on_tb, 0].min() < x0 + 1.0 and inlet[on_tb, 0].max() > x1 - 1.0   # face centres; the last wake face is 1.8c long
    assert np.allclose(outlet[:, 0], x1)
    # the four domain corners are mesh nodes
    for c in ((x0, yt), (x0, yb), (x1, yt), (x1, yb)):
        assert np.any(np.all(np.isclose(m.nodes, c), axis=1)), c
    # the same wall as on the C-grid
    _, _, mc = make(split_at(naca("4412")), kind="c_grid")
    assert (m.face_zone == WALL).sum() == (mc.face_zone == WALL).sum()


def test_rectangle_msh_reads_back():
    _, _, m = make(split_at(naca("0012")))
    nodes, faces, zones = read_fluent_msh(to_fluent_msh(m))
    assert len(nodes) == len(m.nodes)
    assert {z[1] for z in zones.values()} >= {"inlet", "outlet", "wall"}


def test_rectangle_family():
    af = split_at(naca("4412"))
    d = build_domain(af, RECT, r_inlet=15.0, l_wake=20.0, l_top=15.0, l_bottom=15.0)
    fam = mesh_family(d, af, 2.0e6)
    assert [f.label for f in fam] == ["coarse", "medium", "fine"]
    assert all(quality(f.mesh)[1].min() > 0.5 for f in fam)


def test_rectangle_with_other_sizes_and_the_whole_library(library_sweep):
    af = split_at(naca("4412"))
    d = build_domain(af, RECT, r_inlet=5.0, l_wake=10.0, l_top=8.0, l_bottom=12.0)
    m = build_cgrid(d, af, plan_mesh(d, af, 2.0e6))
    assert quality(m)[1].min() > 0.3
    bad = [(r["id"], round(r["oq_min"], 3)) for r in library_sweep(RECT, 2.0e6, 0.5) if r["oq_min"] < 0.15]
    assert not bad, bad


def test_app_offers_the_rectangle_mesh():
    at = AppTest.from_file(APP, default_timeout=240).run()
    [w for w in at.selectbox if w.key == "domain_kind"][0].set_value(RECT)
    at = at.run()
    mode = [w for w in at.radio if w.key == "mesh_mode"][0]
    mode.set_value(mode.options[1])
    at = at.run()
    assert not at.exception and not at.error
    assert any(el.proto.id.endswith("msh_download") for el in at.get("download_button"))


@pytest.mark.parametrize("name, words", [
    ("CHANGELOG.md", ("Fluent mesh file for the rectangular domain", "Dikdörtgen domain için Fluent mesh dosyası")),
    ("README.md", ("C-Grid ya da dikdörtgen",)), ("README.en.md", ("C-grid or rectangular",))])
def test_docs_describe_the_rectangle_mesh(name, words):
    text = (Path(__file__).resolve().parents[1] / name).read_text(encoding="utf-8")
    assert "The rectangular domain is not covered yet" not in text
    for w in words:
        assert w in text, w


@pytest.mark.parametrize("lang, word", [("tr", "dikdörtgen"), ("en", "rectangular")])
def test_mesh_note_covers_the_rectangle(lang, word):
    from airfoilmatic.i18n import tr
    assert word in tr("msh_note", lang)


def test_orthogonal_quality_matches_fluent_on_the_rectangle():
    """Fluent 2024 R2, Domain > Mesh > Quality on the NACA 4412 rectangle file (2026-11-27):
    minimum orthogonal quality 0.667662 at (-1.01791, -1.16829)."""
    from airfoilmatic.geometry import DEFAULT_SPLIT
    _, _, m = make(split_at(close_small_te_gap(naca("4412")), DEFAULT_SPLIT))
    oq = quality(m)[1]
    assert oq.min() == pytest.approx(0.667662, abs=2e-4)
    assert np.allclose(m.nodes[m.cells[np.argmin(oq)]].mean(0), (-1.018, -1.168), atol=5e-3)


@pytest.mark.parametrize("name, words", [("CHANGELOG.md", ("0.667662", "1.22537")), ("README.md", ("1.22537",)),
                                          ("README.en.md", ("1.22537",))])
def test_docs_say_the_rectangle_was_tried(name, words):
    text = (Path(__file__).resolve().parents[1] / name).read_text(encoding="utf-8")
    assert "dikdörtgen Fluent'te henüz denenmedi" not in text and "the rectangle is not tried in Fluent yet" not in text
    for w in words:
        assert w in text, w


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_mesh_note_says_the_rectangle_was_tried(lang):
    from airfoilmatic.i18n import tr
    text = tr("msh_note", lang)
    assert "1.22537" in text
