"""Leading-edge corner of the app's .msh at high Reynolds numbers (review 2026-11-27, group 3).

The front axis (the block edge from the leading edge to the inlet) was a straight horizontal line,
tilted from the wall normal at the leading edge (NACA 4412: about 11 degrees, the camber-line slope).
Near it the grid lines turned from the wall normal into the axis direction, so the first-cell
height measured normal to the wall changed from column to column; on cells 10^4 times longer than
high this alone dropped the orthogonal quality (NACA 4412 at Re 3e7: 0.24; E63: 0.004, below
Fluent's 0.01). Now the front axis leaves the leading edge along the wall normal and bends to
horizontal within one chord, and the first-cell heights come from the planned distribution of the
side edges instead of each interpolated line's own length.
"""
import numpy as np
import pytest

from airfoilmatic import library as lib
from airfoilmatic.blockmesh import build_cgrid, quality
from airfoilmatic.geometry import close_small_te_gap, naca, parse_airfoil_file, split_at
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.topology import build_domain
from _docs import doc_text


def section(sid):
    if sid.startswith("naca"):
        return split_at(naca(sid[4:]))
    s = [x for x in lib.library() if x.id == sid][0]
    return split_at(close_small_te_gap(parse_airfoil_file(s.data)))


def mesh(af, re, refine=1.0, **kw):
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    return d, build_cgrid(d, af, plan_mesh(d, af, re, refine=refine), **kw)


@pytest.mark.parametrize("sid, re, before, now", [
    ("naca4412", 3e7, 0.24, 0.5),
    ("naca4412", 1e8, 0.08, 0.2),
    ("e63", 2e6, 0.08, 0.25),
    ("s6063", 2e6, 0.20, 0.4),
])
def test_leading_edge_quality(sid, re, before, now):
    _, m = mesh(section(sid), re)
    assert quality(m)[1].min() > now > before


def test_front_axis_leaves_along_the_wall_normal():
    af = section("naca4412")
    d, m = mesh(af, 2e6)
    le = np.array(af.le)
    i0 = np.flatnonzero(np.all(np.isclose(m.nodes, le), axis=1))[0]
    # the node next to the LE on the front axis: shares a face with the LE node and lies ahead of it
    nb = [f[1] if f[0] == i0 else f[0] for f in m.faces if i0 in f[:2]]
    ahead = [j for j in nb if m.nodes[j, 0] < le[0]]
    v = m.nodes[ahead[0]] - le
    angle = np.degrees(np.arctan2(v[1], -v[0]))
    assert angle == pytest.approx(-11.3, abs=1.5)          # camber-line slope at the LE: 2m/p^2 * p
    # far from the airfoil the axis is horizontal again and ends at the inlet point
    p_in = np.array([d.get("front_axis").x[0], d.get("front_axis").y[0]])
    assert np.any(np.all(np.isclose(m.nodes, p_in), axis=1))


def test_symmetric_section_unchanged():
    af = section("naca0012")
    _, a = mesh(af, 2e6)
    _, b = mesh(af, 2e6, axis_bend=False)
    on_axis = np.abs(a.nodes[:, 1]) < 1e-12
    assert np.allclose(np.sort(a.nodes[on_axis, 0]), np.sort(b.nodes[np.abs(b.nodes[:, 1]) < 1e-12, 0]))


@pytest.mark.parametrize("re, floor", [(2e6, 0.15), (3e7, 0.01)])
def test_whole_library(re, floor, library_sweep):
    """Re 2e6: lowest orthogonal quality 0.051 before (E63); Re 3e7: 0.004 before, below Fluent's
    0.01. No turned-over cell anywhere."""
    bad = [(r["id"], round(r["oq_min"], 3)) for r in library_sweep("c_grid", re, 0.5) if r["oq_min"] < floor]
    assert not bad, bad


@pytest.mark.parametrize("name, words", [
    ("CHANGELOG.md", ("Front axis along the wall normal", "Ön eksen duvar normaliyle", "0.24 → 0.59", "0.004")),
    ("README.md", ("ön eksen", "1.22288")),
    ("README.en.md", ("front axis", "1.22288"))])
def test_docs_describe_the_bent_axis(name, words):
    from pathlib import Path
    text = doc_text(name)
    assert "bükülme Fluent'te henüz denenmedi" not in text and "bend is not tried in Fluent yet" not in text
    for w in words:
        assert w in text, w


@pytest.mark.parametrize("lang, words", [("tr", ("Ön eksen", "0.895", "1.22288")),
                                         ("en", ("front axis", "0.895", "1.22288"))])
def test_mesh_note_mentions_the_bent_axis(lang, words):
    from airfoilmatic.i18n import tr
    assert "denenmedi" not in tr("msh_note", lang).split("C-Grid ve dikdörtgen")[-1]
    text = doc_text("README.md" if lang == "tr" else "README.en.md")
    assert "bükülme Fluent'te henüz denenmedi" not in text and "bend is not tried" not in text
    for w in words:
        assert w in text or w.lower() in text, w


def test_orthogonal_quality_matches_fluent_on_the_bent_axis_mesh():
    """Fluent 2024 R2, Domain > Mesh > Quality on the bent-axis NACA 4412 file (2026-11-27):
    minimum orthogonal quality 0.894628 at (-0.0247458, -0.102386)."""
    from airfoilmatic.geometry import DEFAULT_SPLIT
    af = split_at(close_small_te_gap(naca("4412")), DEFAULT_SPLIT)
    _, m = mesh(af, 2.0e6)
    oq = quality(m)[1]
    assert oq.min() == pytest.approx(0.894628, abs=2e-4)
    assert np.allclose(m.nodes[m.cells[np.argmin(oq)]].mean(0), (-0.02475, -0.10239), atol=2e-3)
