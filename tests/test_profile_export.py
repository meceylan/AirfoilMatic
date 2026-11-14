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
    units = [r for r in at.radio if r.key == "profile_unit"][0]
    assert units.value == "m" and units.options == ["m", "mm"]
    units.set_value("mm")
    at = at.run()
    assert not at.exception and not at.error
