"""Airfoil-only export for DesignModeler and SolidWorks."""
import io
import zipfile

import numpy as np
import pytest

from airfoilmatic import library as lib
from airfoilmatic.export import profile_dm_txt, profile_solidworks_files, profile_solidworks_zip
from airfoilmatic.geometry import close_small_te_gap, naca


def rows(text):
    return [line.split() for line in text.strip().splitlines()]


def test_dm_file_has_two_groups_for_a_sharp_section():
    af = close_small_te_gap(naca("4412", 1.0))
    r = rows(profile_dm_txt(af))
    assert {int(x[0]) for x in r} == {1, 2}
    g1 = [x for x in r if x[0] == "1"]
    g2 = [x for x in r if x[0] == "2"]
    assert [int(x[1]) for x in g1] == list(range(1, len(g1) + 1))
    assert g1[0][2:4] == g2[0][2:4] == ["0.0000000", "0.0000000"]      # both start at the leading edge
    assert g1[-1][2:4] == g2[-1][2:4]                                   # and meet at the sharp trailing edge
    assert float(g1[5][3]) > 0 > float(g2[5][3])                        # upper above, lower below
    assert all(x[4] == "0.0" for x in r)


def test_dm_file_closes_a_blunt_trailing_edge_with_a_third_group():
    s = lib.library()[0]
    for s in lib.library():
        af = s.airfoil()
        if af.te_gap > 1e-3:
            break
    r = rows(profile_dm_txt(close_small_te_gap(af)))
    g3 = [x for x in r if x[0] == "3"]
    assert len(g3) == 2


def test_units_scale_the_numbers_and_the_chord_ends_at_the_chosen_unit():
    af = close_small_te_gap(naca("0012", 0.5))
    m = rows(profile_dm_txt(af, "m"))
    mm = rows(profile_dm_txt(af, "mm"))
    assert max(float(x[2]) for x in m) == pytest.approx(0.5)
    assert max(float(x[2]) for x in mm) == pytest.approx(500.0)
    with pytest.raises(ValueError):
        profile_dm_txt(af, "inch")


def test_solidworks_files_are_tab_separated_xyz_without_header():
    af = close_small_te_gap(naca("2412", 1.0))
    f = profile_solidworks_files(af, "mm")
    assert set(f) == {"upper", "lower"}
    for text in f.values():
        for line in text.splitlines():
            a, b, c = line.split("\t")
            float(a), float(b)
            assert c == "0"
    up = [float(l.split("\t")[1]) for l in f["upper"].splitlines()]
    lo = [float(l.split("\t")[1]) for l in f["lower"].splitlines()]
    assert max(up) > 0 > min(lo)
    assert f["upper"].splitlines()[0] == f["lower"].splitlines()[0]    # same leading-edge point
    assert f["upper"].splitlines()[-1] == f["lower"].splitlines()[-1]  # same sharp trailing edge


def test_solidworks_zip_holds_two_named_files():
    af = close_small_te_gap(naca("4412", 1.0))
    z = zipfile.ZipFile(io.BytesIO(profile_solidworks_zip(af, "AirfoilMatic_NACA4412", "mm")))
    assert sorted(z.namelist()) == ["AirfoilMatic_NACA4412_lower.txt", "AirfoilMatic_NACA4412_upper.txt"]


@pytest.mark.parametrize("s", lib.library()[::7], ids=lambda s: s.id)
def test_no_repeated_points_in_library_sections(s):
    af = close_small_te_gap(s.airfoil())
    for text in profile_solidworks_files(af, "mm").values():
        pts = [tuple(map(float, l.split("\t")[:2])) for l in text.splitlines()]
        assert all(a != b for a, b in zip(pts, pts[1:]))
        assert not np.isnan(np.array(pts)).any()


def test_page_offers_the_profile_downloads_in_both_units():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=120).run()
    assert not at.exception and not at.error
    units = [r for r in at.radio if r.key == "out_unit"][0]
    assert units.value == "m" and units.options == ["m", "mm"]
    units.set_value("mm")
    at = at.run()
    assert not at.exception and not at.error


def test_spaceclaim_file_has_the_header_and_separate_curves():
    from airfoilmatic.export import profile_spaceclaim_txt
    af = close_small_te_gap(naca("4412", 1.0))
    text = profile_spaceclaim_txt(af, "mm")
    lines = text.split("\n")
    assert lines[:3] == ["3d=true", "polyline=false", "fit=false"]
    blocks = [b for b in text.split("\n\n") if b.strip()]
    assert len(blocks) == 2                               # sharp trailing edge: upper and lower only
    first = blocks[0].split("\n", 3)[3].split("\n")
    for row in first:
        z, x, y = row.split()
        assert z == "0"
        float(x), float(y)
    assert max(float(r.split()[1]) for r in first) == pytest.approx(1000.0)
    assert not text.endswith("\n\n")


def test_spaceclaim_file_adds_the_trailing_edge_line_for_a_blunt_section():
    from airfoilmatic.export import profile_spaceclaim_txt
    for s in lib.library():
        af = close_small_te_gap(s.airfoil())
        if af.te_gap > 1e-3:
            break
    blocks = [b for b in profile_spaceclaim_txt(af).split("\n\n") if b.strip()]
    assert len(blocks) == 3 and len(blocks[2].strip().split("\n")) == 2


def test_spaceclaim_domain_file_has_one_curve_per_domain_curve():
    from airfoilmatic.export import to_ansys_txt, to_spaceclaim_txt
    from airfoilmatic.geometry import split_at
    from airfoilmatic.topology import C_GRID, build_domain
    d = build_domain(split_at(close_small_te_gap(naca("4412", 1.0))), C_GRID, r_inlet=15, l_wake=20)
    sc = to_spaceclaim_txt(d)
    assert sc.startswith("3d=true\npolyline=false\nfit=false\n")
    blocks = [b for b in sc.split("\n\n") if b.strip()]
    assert len(blocks) == len(d.curves)
    ans = [l.split() for l in to_ansys_txt(d).strip().splitlines()]
    pts_sc = [r.split()[1:] for b in blocks for r in b.strip().splitlines() if r.startswith("0 ")]
    assert pts_sc == [a[2:4] for a in ans]        # the same points as the Ansys file, in the same order


def test_domain_files_scale_with_the_unit_and_keep_the_same_points():
    from airfoilmatic.export import to_ansys_txt, to_spaceclaim_txt
    from airfoilmatic.geometry import split_at
    from airfoilmatic.topology import C_GRID, build_domain
    d = build_domain(split_at(close_small_te_gap(naca("4412", 1.0))), C_GRID, r_inlet=15, l_wake=20)
    m = [l.split() for l in to_ansys_txt(d).strip().splitlines()]
    mm = [l.split() for l in to_ansys_txt(d, scale=1000.0).strip().splitlines()]
    assert len(m) == len(mm)
    assert max(float(r[2]) for r in mm) == pytest.approx(1000.0 * max(float(r[2]) for r in m), rel=1e-6)
    assert max(float(r[2]) for r in mm) == pytest.approx(20000.0 + 1000.0, rel=1e-3)   # wake end at 20 c + chord
    assert to_ansys_txt(d, scale=1.0) == to_ansys_txt(d)
    assert "3d=true" in to_spaceclaim_txt(d, scale=1000.0)


def test_page_runs_with_the_output_unit_set_to_mm():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=120).run()
    [r for r in at.radio if r.key == "out_unit"][0].set_value("mm")
    at = at.run()
    assert not at.exception and not at.error
