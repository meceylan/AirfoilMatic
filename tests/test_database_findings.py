"""Problems found by running the whole UIUC coordinate database (1665 files) through the app.

Eleven of the files let the upper and the lower surface overlap by 0.001 to 0.05 % of the chord,
mostly at a cusped trailing edge. Nine of them were exported without a warning, with curves that
cross each other (DesignModeler cannot build a face from those), two were refused with a message
that did not say why. The files below are written from a known outline with the same defects.
"""
import numpy as np
import pytest

from airfoilmatic.geometry import (AirfoilError, close_small_te_gap, naca, parse_airfoil_file, split_at)
from airfoilmatic.topology import C_GRID, RECT, build_domain


def crossings(domain):
    """Places where two different curves cross (touching at a shared end point does not count)."""
    segs, owner = [], []
    for i, c in enumerate(domain.curves):
        p = np.column_stack([c.x, c.y])
        segs.append(np.hstack([p[:-1], p[1:]]))
        owner += [i] * (len(p) - 1)
    s, o = np.vstack(segs), np.array(owner)
    a, b, c, e = s[:, None, :2], s[:, None, 2:], s[None, :, :2], s[None, :, 2:]

    def cross(u, v):
        return u[..., 0] * v[..., 1] - u[..., 1] * v[..., 0]

    hit = ((cross(b - a, c - a) * cross(b - a, e - a) < -1e-12)
           & (cross(e - c, a - c) * cross(e - c, b - c) < -1e-12) & (o[:, None] != o[None, :]))
    return int(hit.sum()) // 2


def selig(xu, yu, xl, yl):
    x, y = np.concatenate([xu[::-1], xl[1:]]), np.concatenate([yu[::-1], yl[1:]])
    return "\n".join(f"{a:.7f} {b:.7f}" for a, b in zip(x, y)).encode()


def exported_crossings(af):
    sp = split_at(close_small_te_gap(af))
    return [crossings(build_domain(sp, k, r_inlet=10, l_wake=20, l_top=10, l_bottom=10)) for k in (C_GRID, RECT)]


def thickness(af, n=4000):
    xs = np.linspace(0.0005, 0.9995, n)
    return np.interp(xs, af.xu, af.yu) - np.interp(xs, af.xl, af.yl)


def cusped(inversion):
    """Cambered section whose rear 3 % is a cusp; the lower surface ends ``inversion`` above the upper
    one (rounded coordinates of a cusped trailing edge, as in Wortmann FX 62-K-131)."""
    a = naca("2412", n_points=60)
    xu, yu, xl, yl = a.xu.copy(), a.yu.copy(), a.xl.copy(), a.yl.copy()
    rear = xu > 0.97
    k = (xu[rear] - 0.97) / 0.03                       # 0 -> 1 towards the trailing edge
    yl[rear] = yu[rear] + inversion * np.sin(np.pi * k) - 1e-5 * (1 - k)
    yl[-1] = yu[-1] = 0.0
    g = np.linspace(0.9, 0.9999, 4000)
    return xu, yu, xl, yl, float((np.interp(g, xl, yl) - np.interp(g, xu, yu)).max())


@pytest.mark.parametrize("inversion", [1e-4, 3e-4, 8e-4])
def test_overlapping_cusped_trailing_edge_is_repaired(inversion):
    xu, yu, xl, yl, found = cusped(inversion)
    assert found > 0.3 * inversion
    af = parse_airfoil_file(selig(xu, yu, xl, yl))
    assert af.overlap == pytest.approx(found, rel=0.05)
    assert thickness(af).min() > 0
    assert exported_crossings(af) == [0, 0]
    # The shape moved by no more than the overlap.
    assert np.max(np.abs(np.interp(xu, af.xu, af.yu) - yu)) <= af.overlap * 1.05
    assert np.max(np.abs(np.interp(xl, af.xl, af.yl) - yl)) <= af.overlap * 1.05


def test_the_unrepaired_file_really_exports_crossing_curves():
    """The reason for the repair: without it the exported domain intersects itself."""
    from airfoilmatic.geometry import Airfoil
    xu, yu, xl, yl, _ = cusped(3e-4)
    raw = Airfoil(xu, yu, xl, yl, 1.0, "raw")
    assert sum(exported_crossings(raw)) > 0


def test_overlap_beyond_one_thousandth_is_refused():
    with pytest.raises(AirfoilError, match="cross each other"):
        parse_airfoil_file(selig(*cusped(3e-3)[:4]))


def test_clean_file_is_not_touched():
    a = naca("0012", n_points=80)
    af = parse_airfoil_file(selig(a.xu, a.yu, a.xl, a.yl))
    assert af.overlap == 0.0
    for got, want in ((af.xu, a.xu), (af.yu, a.yu), (af.xl, a.xl), (af.yl, a.yl)):
        assert np.allclose(got, want, atol=2e-7)   # the file has 7 decimals


def test_repair_leaves_the_rest_of_the_outline_alone():
    xu, yu, xl, yl, _ = cusped(3e-4)
    af = parse_airfoil_file(selig(xu, yu, xl, yl))
    front = xu < 0.9
    assert np.allclose(np.interp(xu[front], af.xu, af.yu), yu[front], atol=2e-7)   # file has 7 decimals
    assert np.allclose(np.interp(xl[front], af.xl, af.yl), yl[front], atol=2e-7)


def test_lower_surface_that_stops_short_of_the_upper_one():
    """Eppler STE 871-514 style, with the real trailing-edge numbers of that file: the upper surface
    ends at x = 1, the lower one 0.4 % earlier and a little higher, so the upper tip sticks out."""
    a = naca("0010", n_points=40)
    body_u, body_l = a.xu < 0.97, a.xl < 0.97
    xu = np.concatenate([a.xu[body_u], [0.98562, 0.99626, 1.0]])
    yu = np.concatenate([a.yu[body_u], [0.00412, 0.00095, 0.0]])
    xl = np.concatenate([a.xl[body_l], [0.98437, 0.9961]])
    yl = np.concatenate([a.yl[body_l], [0.00165, 0.0005]])
    af = parse_airfoil_file(selig(xu, yu, xl, yl))
    assert 5e-5 < af.overlap < 5e-4
    assert af.xu[-1] == pytest.approx(af.xl[-1])          # both end at the same x
    assert af.xu[-1] == pytest.approx(1.0)               # the chord did not shrink
    assert thickness(af).min() > 0
    assert exported_crossings(af) == [0, 0]


def test_thin_section_with_noise_crossing_in_the_middle():
    """Eppler 378 style: a 1 % thick section whose rounded coordinates cross at mid-chord."""
    x = np.linspace(0, 1, 60) ** 1.5
    yt = 0.005 * np.sin(np.pi * x)
    yu, yl = yt.copy(), -yt
    yu[30], yl[30] = -0.00006, 0.00006                    # the surfaces swap places at one point
    af = parse_airfoil_file(selig(x, yu, x, yl))
    assert af.overlap == pytest.approx(1.2e-4, rel=0.2)
    assert thickness(af).min() > 0
    assert exported_crossings(af) == [0, 0]


def test_tiny_rounding_overlap_is_repaired_silently():
    a = naca("0012", n_points=60)
    yl = a.yl.copy()
    yl[-3] = a.yu[-3] + 1e-6                              # one value rounded across the other surface
    af = parse_airfoil_file(selig(a.xu, a.yu, a.xl, yl))
    assert 0 < af.overlap < 1e-5
    assert thickness(af).min() > 0
