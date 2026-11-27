"""Far-field cells above and below the rear part of the airfoil (app's .msh).

The top / bottom edge of each rear block (split line -> TE line, at y = +-15c) used the same
arc-length fractions as the airfoil surface. On a strongly cambered section the surface falls
steeply towards the trailing edge, so its cells are shorter in x than those of the far edge and
the cells in between became slightly trapezoidal. At the far boundary they are 0.0009c wide and
1.36c high, and a 6 % taper moved the centroid enough for Fluent's orthogonal quality to read 0.06
(NACA 9940). The far edge now takes the x positions of the surface nodes: vertical columns.
"""
import numpy as np
import pytest

from airfoilmatic import library as lib
from airfoilmatic.blockmesh import _top_from_wall, build_cgrid, quality
from airfoilmatic.geometry import close_small_te_gap, naca, parse_airfoil_file, split_at
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.topology import build_domain


def section(sid):
    if sid.startswith("naca"):
        return split_at(naca(sid[4:]))
    s = [x for x in lib.library() if x.id == sid][0]
    return split_at(close_small_te_gap(parse_airfoil_file(s.data)))


def make(af, refine=1.0):
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    plan = plan_mesh(d, af, 2.0e6, refine=refine)
    return d, plan, build_cgrid(d, af, plan)


def far(m):
    return np.abs(m.nodes[m.cells].mean(1)[:, 1]) > 1.0


@pytest.mark.parametrize("sid, before", [("naca9940", 0.06), ("s9104", 0.08), ("fx73cl2152", 0.12),
                                         ("s1223", 0.20)])
def test_far_field_cells_of_cambered_sections(sid, before):
    _, _, m = make(section(sid))
    _, oq = quality(m)
    assert oq[far(m)].min() > 0.25 > before


@pytest.mark.parametrize("sid", ["naca4412", "s9104", "naca9940"])
def test_far_edge_follows_the_surface_x(sid):
    af = section(sid)
    d, _, m = make(af)
    x_te = d.get("wake_axis").x[0]
    for y_far in (d.y_top, -d.y_bottom):
        top = m.nodes[(np.abs(m.nodes[:, 1] - y_far) < 1e-9) & (m.nodes[:, 0] > d.x_split - 1e-9)
                      & (m.nodes[:, 0] < x_te + 1e-9)]
        poly = af.upper_rear if y_far > 0 else af.lower_rear
        xs = np.sort(top[:, 0])
        # the far nodes lie above / below wall nodes (same x), so the columns are vertical
        wall_x = np.asarray(poly[0], float)
        assert len(xs) > 10
        assert np.all(np.diff(xs) > 0)
        near_wall = m.nodes[np.isclose(m.nodes[:, 0], xs[len(xs) // 2], atol=1e-12)]
        assert len(near_wall) > 2      # a whole column shares this x
        assert wall_x.min() - 1e-9 <= xs[len(xs) // 2] <= wall_x.max() + 1e-9


def test_non_monotonic_surface_falls_back_to_the_fractions():
    t = np.linspace(0.0, 1.0, 6)
    wall = np.array([[0.3, 0.1], [0.5, 0.1], [0.7, 0.1], [0.69, 0.05], [0.9, 0.02], [1.0, 0.0]])
    top = _top_from_wall(wall, np.array([0.3, 15.0]), np.array([1.0, 15.0]), t)
    assert np.allclose(top[:, 0], 0.3 + 0.7 * t) and np.allclose(top[:, 1], 15.0)
    ok = _top_from_wall(wall[[0, 1, 2, 4, 5]], np.array([0.3, 15.0]), np.array([1.0, 15.0]), t[:5])
    assert np.allclose(ok[:, 0], [0.3, 0.5, 0.7, 0.9, 1.0])


def test_whole_library_has_no_poor_far_field_cell(library_sweep):
    bad = [(r["id"], round(r["far_oq"], 3)) for r in library_sweep("c_grid", 2.0e6, 0.5) if r["far_oq"] < 0.3]
    assert not bad, bad


@pytest.mark.parametrize("name, words", [("CHANGELOG.md", ("vertical columns", "dikey sütun", "0.06", "NACA 9940")),
                                          ("README.md", ("dikey sütun",)), ("README.en.md", ("vertical columns",))])
def test_docs_mention_the_far_field_columns(name, words):
    from pathlib import Path
    text = (Path(__file__).resolve().parents[1] / name).read_text(encoding="utf-8")
    for w in words:
        assert w in text, w
