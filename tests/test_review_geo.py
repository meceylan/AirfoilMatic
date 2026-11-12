"""Regression tests for bugs found in the geometry / library review."""
import numpy as np

from airfoilmatic import library as lib
from airfoilmatic.geometry import naca4, parse_airfoil_file


def test_overlap_repair_next_to_the_nose_keeps_a_common_leading_edge():
    """A small overlap at the first points behind the nose used to move the shared LE
    point apart (upper +1e-5c, lower -1e-5c), leaving the outline open at the nose."""
    ref = naca4("0003", n_points=41)
    xs = np.concatenate([ref.xu[::-1], ref.xl[1:]])
    ys = np.concatenate([ref.yu[::-1], ref.yl[1:]])
    n = len(ref.xu)
    ys[n - 2], ys[n] = -0.00002, 0.00003   # first upper point below the first lower point
    af = parse_airfoil_file("\n".join(f"{x:.6f} {y:.6f}" for x, y in zip(xs, ys)))
    assert af.overlap > 0
    assert (af.xl[0], af.yl[0]) == (af.xu[0], af.yu[0])
    grid = np.linspace(0, 1, 2001)
    assert np.min(np.interp(grid, af.xu, af.yu) - np.interp(grid, af.xl, af.yl)) >= -1e-12


def test_uiuc_style_n_prefix_names_the_naca_section():
    """"n0012" (UIUC file name of NACA 0012) used to give SC(2)-0012 first; "n4412" nothing."""
    assert lib.search("n0012")[0].id == "naca0012"
    assert lib.search("N4412")[0].id == "naca4412"
    assert lib.search("n23012")[0].id == "naca23012"


def test_six_series_dash_name_is_not_drawn_as_a_5_digit_section():
    """"64-012" is a symmetric 6-series section; it used to come out as a cambered
    NACA 64012 5-digit section (design Cl 0.9) drawn from the equations."""
    assert lib.naca_section("NACA 64-012") is None
    assert lib.search("64-012") == []
    assert lib.search("63-010")[0].id == "n63010a"
    assert lib.search("NACA 63-215")[0].id == "n63215"
