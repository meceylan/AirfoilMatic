"""Grid lines leave the airfoil at right angles on the front blocks (leading edge -> split line).

Plain transfinite interpolation joins each wall node to the far arc by a straight blend; behind
the nose of a strongly cambered section (S9104, 14 % camber, concave lower surface near the LE)
the lines left the wall almost along it: skewness 0.90, orthogonal quality 0.05 in the first cells.
"""
import numpy as np
import pytest

from airfoilmatic import library as lib
from airfoilmatic.blockmesh import WALL, build_cgrid, mesh_family, quality
from airfoilmatic.geometry import close_small_te_gap, naca, parse_airfoil_file, split_at
from airfoilmatic.mesh import plan_mesh, reynolds
from airfoilmatic.topology import build_domain
from _docs import doc_text

RE = reynolds(51.04, 1.225, 3.126e-5, 1.0)


def section(sid):
    s = [x for x in lib.library() if x.id == sid][0]
    return split_at(close_small_te_gap(parse_airfoil_file(s.data)))


def make(af, refine=1.0):
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    plan = plan_mesh(d, af, RE, refine=refine)
    return d, plan, build_cgrid(d, af, plan)


def nose(m):
    return m.nodes[m.cells].mean(1)[:, 0] < 0.1


def test_s9104_nose_cells_are_good():
    _, _, m = make(section("s9104"))
    skew, oq = quality(m)
    sel = nose(m)
    assert skew[sel].max() < 0.7 and oq[sel].min() > 0.5        # before: 0.90 / 0.05


def test_naca4412_quality_improves():
    """Before: max skewness 0.515, min orthogonal quality 0.493 (behind the nose, lower side)."""
    _, _, m = make(split_at(naca("4412")))
    skew, oq = quality(m)
    assert skew.max() < 0.4 and oq.min() > 0.8


@pytest.mark.parametrize("code", ["9940", "0040", "8412", "23012", "2412", "0006"])
def test_naca_noses_stay_good(code):
    """NACA 9940: the camber line rises 11 degrees at the LE, so the wall normals just above it point
    below the horizontal front axis; without a guard the lines crossed it (cells turned over)."""
    _, _, m = make(split_at(naca(code)))
    skew, oq = quality(m)
    sel = nose(m)
    assert oq.min() > 0 and skew[sel].max() < 0.6 and oq[sel].min() > 0.5


@pytest.mark.parametrize("code", ["4412", "0012", "6412"])
def test_first_lines_leave_the_front_wall_at_right_angles(code):
    """Within 6 degrees: where the wall normal leans back past the vertical split line (NACA 6412's
    lower surface rises 5 degrees before x = 0.3c) the line starts along the split line instead."""
    af = split_at(naca(code))
    _, _, m = make(af)
    xy = m.nodes
    worst = 0.0
    # angle between each front wall face and the cell side that leaves it
    for f in m.faces[m.face_zone == WALL]:
        quad = list(m.cells[f[2]])
        a, b = f[0], f[1]
        ia = quad.index(a)
        nb = quad[(ia + 1) % 4] if quad[(ia + 1) % 4] != b else quad[(ia - 1) % 4]
        p, q, r = xy[a], xy[b], xy[nb]
        if not 0.005 < p[0] < 0.25:
            continue
        t, n = q - p, r - p
        ang = np.degrees(np.arccos(abs(t @ n) / np.linalg.norm(t) / np.linalg.norm(n)))
        worst = max(worst, 90.0 - ang)
    assert worst < 6.0


def test_family_meshes_valid_for_s9104():
    af = section("s9104")
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    for f in mesh_family(d, af, RE):
        skew, oq = quality(f.mesh)
        assert oq.min() > 0 and oq[nose(f.mesh)].min() > 0.2


def test_no_cell_turns_over_on_any_library_section(library_sweep):
    """Every section of the library meshes without a turned-over cell, and no nose reaches the
    skewness of the worst noses before the change (E377 0.97, E63 0.91, S9104 0.90)."""
    bad = [(r["id"], r["nose_skew"], r["oq_min"]) for r in library_sweep("c_grid", 2.0e6, 0.5)
           if r["oq_min"] <= 0 or r["nose_skew"] > 0.82]      # a turned-over cell has orthogonal quality <= 0
    assert not bad, bad


def test_orthogonal_quality_matches_fluent_on_the_new_mesh():
    """Fluent 2024 R2, Domain > Mesh > Quality on the new NACA 4412 file (2026-11-27):
    minimum orthogonal quality 0.844962 at (-0.0381265, -0.0860586)."""
    from airfoilmatic.geometry import DEFAULT_SPLIT
    af = split_at(close_small_te_gap(naca("4412")), DEFAULT_SPLIT)
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    m = build_cgrid(d, af, plan_mesh(d, af, 2.0e6), axis_bend=False)   # the file Fluent measured
    _, oq = quality(m)
    assert oq.min() == pytest.approx(0.844962, abs=2e-4)
    assert np.allclose(m.nodes[m.cells[np.argmin(oq)]].mean(0), (-0.03813, -0.08606), atol=2e-3)


@pytest.mark.parametrize("lang, words", [("tr", ("duvardan dik", "denendi", "0.37", "0.84", "1.22287")),
                                          ("en", ("right angles", "tried", "0.37", "0.84", "1.22287"))])
def test_mesh_note_tells_the_new_start_was_tried(lang, words):
    text = doc_text("README.md" if lang == "tr" else "README.en.md")
    for w in words:
        assert w in text or w.capitalize() in text, w


@pytest.mark.parametrize("name, words", [("README.md", ("duvardan dik", "0.37", "1.22287")),
                                          ("README.en.md", ("right angles", "0.37", "1.22287")),
                                          ("CHANGELOG.md", ("right angles", "duvardan dik", "S9104", "0.844962"))])
def test_docs_describe_the_wall_orthogonal_start(name, words):
    from pathlib import Path
    text = doc_text(name)
    # the paragraphs about the start at right angles (CHANGELOG: EN and TR entries)
    paras = [p for p in text.splitlines() if "right angles" in p or "duvardan dik" in p]
    assert paras
    joined = " ".join(paras)
    for w in words:
        assert w in joined, w
