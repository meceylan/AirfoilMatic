"""Section search, the UIUC selection shipped with the app, and random picks."""
import re

import numpy as np
import pytest

from airfoilmatic import library as lib
from airfoilmatic.export import to_ansys_txt
from airfoilmatic.geometry import chord_line_angle, close_small_te_gap, looks_reversed, naca, split_at
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.topology import C_GRID, RECT, build_domain
from test_database_findings import crossings

SECTIONS = lib.library()


def test_selection_has_200_distinct_sections_with_a_source():
    assert len(SECTIONS) == 200
    assert len({s.id for s in SECTIONS}) == 200
    assert all(s.source == lib.UIUC and s.data and s.title and s.family_name for s in SECTIONS)
    assert len(lib.families()) >= 10


def test_no_naca_4_or_5_digit_file_in_the_selection():
    """Those are drawn from the NACA equations; a 18-point database copy must not compete."""
    for s in SECTIONS:
        m = re.fullmatch(r"(?:naca|n)(\d{4,5})", s.id)
        assert m is None or lib.naca_section(m.group(1)) is None, s.id


@pytest.mark.parametrize("s", SECTIONS, ids=[s.id for s in SECTIONS])
def test_every_section_builds_a_clean_domain(s):
    af = s.airfoil()
    assert min(len(af.xu), len(af.xl)) >= 25
    assert af.overlap < 1e-5 and not looks_reversed(af) and abs(chord_line_angle(af)) < 1.0
    xs = np.linspace(0, 1, 1001)
    t = np.interp(xs, af.xu, af.yu) - np.interp(xs, af.xl, af.yl)
    assert t.max() == pytest.approx(s.t, abs=1e-3)       # the numbers shown on the page are right
    assert t.min() >= -1e-9
    sp = split_at(close_small_te_gap(af))
    for kind in (C_GRID, RECT):
        d = build_domain(sp, kind, r_inlet=15, l_wake=20, l_top=15, l_bottom=15)
        assert crossings(d) == 0
        assert "nan" not in to_ansys_txt(d)
    plan_mesh(d, sp, 1e6)


@pytest.mark.parametrize("query, first", [
    ("4412", "naca4412"), ("NACA 23012", "naca23012"), ("naca-0012", "naca0012"), (" 0012 ", "naca0012"),
    ("63-215", "n63215"), ("n63215", "n63215"), ("NACA 63-215", "n63215"), ("64(2)-415", "naca642415"),
    ("clark y", "clarky"), ("Clark-Y", "clarky"), ("e387", "e387"), ("E 387", "e387"), ("S1223", "s1223"),
    ("sd7003", "sd7003"), ("rae 2822", "rae2822"), ("SC(2)-0714", "sc20714"), ("fx 63-137", "fx63137"),
    ("mh32", "mh32"), ("AG25", "ag25"), ("16009", "naca16009"),
])
def test_search_finds_the_section(query, first):
    assert lib.search(query)[0].id == first


def test_naca_code_is_drawn_from_the_equations():
    s = lib.search("4412")[0]
    assert s.source == lib.NACA_FORMULA
    af = s.airfoil(chord=0.5)
    ref = naca("4412", 0.5)
    assert np.allclose(af.xu, ref.xu) and np.allclose(af.yu, ref.yu)
    assert s.t == pytest.approx(0.12, abs=0.002)


@pytest.mark.parametrize("query", ["xyz", "9999", "naca 12345678", "", "   ", "s99999"])
def test_unknown_name_is_not_found(query):
    """Nothing is invented: a name that is neither a NACA code nor in the selection gives no result."""
    assert lib.search(query) == []


def test_section_ids_find_themselves():
    """The dice and the history put the file name in the search box; it must come out on top."""
    for s in SECTIONS:
        assert lib.search(s.id)[0].id == s.id


def test_random_pick_respects_the_filters():
    rng = np.random.default_rng(7)
    for _ in range(50):
        s = lib.random_section(rng, t_range=(0.10, 0.14), camber=lib.CAMBER_CAMBERED, family_keys={"eppler", "selig"})
        assert 0.10 <= s.t <= 0.14 and abs(s.camber) >= lib.SYMMETRIC_TOL and s.family in ("eppler", "selig")
    sym = lib.pool(camber=lib.CAMBER_SYMMETRIC)
    assert sym and all(abs(s.camber) < lib.SYMMETRIC_TOL for s in sym)


def test_random_pick_avoids_the_current_section_and_reports_an_empty_pool():
    rng = np.random.default_rng(1)
    du = lib.pool(family_keys={"du"})
    assert len(du) >= 2
    for _ in range(20):
        assert lib.random_section(rng, avoid=du[0].id, family_keys={"du"}).id != du[0].id
    assert lib.random_section(rng, t_range=(0.0, 0.01)) is None


def test_random_pick_reaches_every_family():
    rng = np.random.default_rng(3)
    seen = {lib.random_section(rng).family for _ in range(2000)}
    assert seen == {k for k, _ in lib.families()}


def test_thickness_slider_covers_the_whole_selection():
    import ast
    src = open(__file__.replace("tests/test_library.py", "app.py")).read()
    top = next(n.value.value for n in ast.parse(src).body
               if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "MAX_T_PERCENT")
    assert max(s.t for s in SECTIONS) * 100 <= top
    assert len(lib.pool(t_range=(0.0, top / 100))) == len(SECTIONS)
