"""Hard coordinate files.

Every file below is written from a known outline, so the test can measure how far the
outline the app reads is from the true one, instead of only checking that nothing crashes.
"""
import math

import numpy as np
import pytest

from airfoilmatic.export import safe_file_stem, to_ansys_txt
from airfoilmatic.geometry import (AirfoilError, chord_line_angle, close_small_te_gap, looks_reversed,
                                   naca, parse_airfoil_file, split_at)
from airfoilmatic.i18n import tr_error
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.topology import C_GRID, RECT, build_domain

TOL = 3e-4   # fraction of the chord


def shape(code, n, blunt=False):
    a = naca(code, n_points=n, blunt_te=blunt)
    return a.xu.copy(), a.yu.copy(), a.xl.copy(), a.yl.copy()


def loop(s, lower_first=False):
    """Selig order: TE -> upper -> LE -> lower -> TE."""
    xu, yu, xl, yl = s
    if lower_first:
        return np.concatenate([xl[::-1], xu[1:]]), np.concatenate([yl[::-1], yu[1:]])
    return np.concatenate([xu[::-1], xl[1:]]), np.concatenate([yu[::-1], yl[1:]])


def rows(x, y, fmt="{:.6f} {:.6f}"):
    return "\n".join(fmt.format(a, b) for a, b in zip(x, y))


def same(x, y):
    return x, y


def moved(k, dx=0.0, dy=0.0):
    return lambda x, y: (x * k + dx, y * k + dy)


def rotated(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return lambda x, y: (x * c + y * s, -x * s + y * c)   # positive = nose up


A = shape("2412", 61)
B = shape("0012", 61, blunt=True)
X, Y = loop(A)
XB, YB = loop(B)
XU, YU, XL, YL = A
RNG = np.random.default_rng(3)
BASE = np.linspace(0, YB[0], 4)[1:-1]

# name -> (file content, outline it was written from, transform applied to that outline)
GOOD = {
    "selig": (rows(X, Y), A, same),
    "selig, title": ("NACA 2412\n" + rows(X, Y), A, same),
    "selig, CRLF": (("NACA 2412\r\n" + rows(X, Y).replace("\n", "\r\n")).encode(), A, same),
    "selig, CR only": (("NACA 2412\r" + rows(X, Y).replace("\n", "\r")).encode(), A, same),
    "selig, tabs": (rows(X, Y, "{:.6f}\t{:.6f}"), A, same),
    "selig, lower surface first": (rows(*loop(A, True)), A, same),
    "title 'NACA 63-215 MOD'": ("NACA 63-215 MOD\n" + rows(X, Y), A, same),
    "title '2412 15'": ("2412 15\n" + rows(X, Y), A, same),
    "parameter line '0.1200 0.4000'": ("MYFOIL\n 0.1200 0.4000\n" + rows(X, Y), A, same),
    "parameter line '12.0 40.0 2.0'": (" 12.0 40.0 2.0\n" + rows(X, Y), A, same),
    "title + date line": ("2412 15\n2024-05-12\n" + rows(X, Y), A, same),
    "column header and END": ("x/c y/c\n" + rows(X, Y) + "\nEND\n\n", A, same),
    "comment lines # ! %": ("# made by tool\n! chord = 1\n% no units\n" + rows(X, Y), A, same),
    "comment after each row": ("\n".join(f"{a:.6f} {b:.6f} ! pt {i}" for i, (a, b) in enumerate(zip(X, Y))), A, same),
    "blank line between rows": (rows(X, Y).replace("\n", "\n\n"), A, same),
    "first point repeated at the end": (rows(np.append(X, X[0]), np.append(Y, Y[0])), A, same),
    "lednicer '61. 61.'": ("NAME\n 61.  61.\n\n" + rows(XU, YU) + "\n\n" + rows(XL, YL), A, same),
    "lednicer, integer counts": ("NAME\n61 61\n" + rows(XU, YU) + "\n" + rows(XL, YL), A, same),
    "lednicer, counts too large": ("NAME\n62 62\n" + rows(XU, YU) + "\n" + rows(XL, YL), A, same),
    "lednicer, counts too small": ("NAME\n60 60\n" + rows(XU, YU) + "\n" + rows(XL, YL), A, same),
    "lednicer, lower block first": ("NAME\n61 61\n" + rows(XL, YL) + "\n" + rows(XU, YU), A, same),
    "lednicer, blocks TE -> LE": ("NAME\n61 61\n" + rows(XU[::-1], YU[::-1]) + "\n" + rows(XL[::-1], YL[::-1]), A, same),
    "two blocks, no counts": (rows(XU, YU) + "\n" + rows(XL, YL), A, same),
    "two blocks, lower one starts off the LE": (rows(XU, YU) + "\n" + rows(XL[1:], YL[1:]), A, same),
    "loop that starts at the LE": (rows(np.concatenate([XU, XL[::-1][1:]]), np.concatenate([YU, YL[::-1][1:]])), A, same),
    "LE point twice": (rows(np.concatenate([XU[::-1], XL]), np.concatenate([YU[::-1], YL])), A, same),
    "every point twice": (rows(np.repeat(X, 2), np.repeat(Y, 2)), A, same),
    "blunt TE, open": (rows(XB, YB), B, same),
    "blunt TE, closed through a mid point": (rows(np.concatenate([[1.0], XB, [1.0]]), np.concatenate([[0.0], YB, [0.0]])), B, same),
    "blunt TE, points along the base": (rows(np.concatenate([np.full(3, 1.0), XB, np.full(3, 1.0)]),
                                             np.concatenate([[0.0], BASE, YB, -BASE[::-1], [0.0]])), B, same),
    "blunt TE, lednicer": ("B\n61 61\n" + rows(B[0], B[1]) + "\n" + rows(B[2], B[3]), B, same),
    "9 points per surface": (rows(*loop(shape("2412", 9))), shape("2412", 9), same),
    "3 points per surface": (rows(*loop(shape("2412", 3))), shape("2412", 3), same),
    "millimetres": (rows(X * 1000, Y * 1000, "{:.3f} {:.3f}"), A, moved(1000)),
    "percent": (rows(X * 100, Y * 100, "{:.4f} {:.4f}"), A, moved(100)),
    "inches, 12 in chord": (rows(X * 12, Y * 12, "{:.5f} {:.5f}"), A, moved(12)),
    "LE at x = 5": (rows(X + 5, Y), A, moved(1, 5)),
    "chord centred on x = 0": (rows(X - 0.5, Y), A, moved(1, -0.5)),
    "2 chords above the x axis": (rows(X, Y + 2.0), A, moved(1, 0, 2.0)),
    "CAD section: mm, origin far away": (rows(X * 300 + 1500, Y * 300 + 800, "{:.3f} {:.3f}"), A, moved(300, 1500, 800)),
    "rotated +5 deg": (rows(*rotated(5)(X, Y)), A, rotated(5)),
    "rotated -10 deg": (rows(*rotated(-10)(X, Y)), A, rotated(-10)),
    "upside down": (rows(X, -Y), A, lambda x, y: (x, -y)),
    "exponent notation": (rows(X, Y, "{:.6E} {:.6E}"), A, same),
    "Fortran D exponent": (rows(X, Y, "{:.6E} {:.6E}").replace("E", "D"), A, same),
    "plus signs": (rows(X, Y, "{:+.6f} {:+.6f}"), A, same),
    "no leading zero": (rows(X, Y).replace(" 0.", " .").replace("-0.", "-.").replace("\n0.", "\n."), A, same),
    "columns touch (F8.5)": ("\n".join(f"{a:8.5f}{b:8.5f}" for a, b in zip(X, Y)), A, same),
    "columns touch (F9.6)": ("\n".join(f"{a:9.6f}{b:9.6f}" for a, b in zip(X, Y)), A, same),
    "point number column": ("\n".join(f"{i + 1} {a:.6f} {b:.6f}" for i, (a, b) in enumerate(zip(X, Y))), A, same),
    "x y z with z = 0": ("\n".join(f"{a:.6f} {b:.6f} 0.000000" for a, b in zip(X, Y)), A, same),
    "x 0 z (section in the XZ plane)": ("\n".join(f"{a:.6f} 0.000000 {b:.6f}" for a, b in zip(X, Y)), A, same),
    "span position, x, y": ("\n".join(f"250.000 {a:.6f} {b:.6f}" for a, b in zip(X, Y)), A, same),
    "latin-1 title": ("Kanat profili ölçüsü\n" + rows(X, Y)).encode("latin-1"),
    "UTF-16 without a byte-order mark": (rows(X, Y).encode("utf-16-le"), A, same),
    "digitised: x jitter": (rows(X + RNG.normal(0, 2e-5, len(X)), Y), A, same),
    "thin, strongly cambered (6409)": (rows(*loop(shape("6409", 81))), shape("6409", 81), same),
    "lower surface stops before the TE": (rows(X[:-1], Y[:-1]), A, same),
    "nan and inf rows inside": (rows(X, Y).replace("\n", "\nnan nan\n", 1).replace("\n", "\ninf 0.0\n", 1), A, same),
    "values of 1e300": (rows(X * 1e300, Y * 1e300, "{:.6e} {:.6e}"), A, same),
    "values of 1e-300": (rows(X * 1e-300, Y * 1e-300, "{:.6e} {:.6e}"), A, same),
}
GOOD["latin-1 title"] = (GOOD["latin-1 title"], A, same)

BAD = {
    "2 points per surface": rows(*loop(shape("2412", 2))),
    "surfaces cross near the TE": rows(X, np.where((X > 0.9) & (np.arange(len(X)) < 61), Y - 0.02, Y)),
    "two airfoils in one file": rows(X, Y) + "\n" + rows(X * 0.3 + 1.05, Y * 0.3 - 0.05),
    "flat plate without thickness": rows(X, np.zeros_like(X)),
    "only the upper surface": rows(XU[::-1], YU[::-1]),
    "empty": "",
    "title only": "NACA 0012\n",
    "random bytes": bytes(RNG.integers(0, 256, 4000, dtype=np.uint8)),
    "pdf": b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\nendobj\n" + bytes(RNG.integers(0, 256, 2000, dtype=np.uint8)),
    "html": "<html><body><table><tr><td>1.0</td><td>0.0</td></tr></table></body></html>",
    "time series csv": "t,value\n" + "\n".join(f"{i * 0.1:.1f},{math.sin(i * 0.3):.4f}" for i in range(200)),
    "polar (alpha CL CD)": "alpha CL CD\n" + "\n".join(f"{a:.2f} {0.1 * a:.4f} {0.006 + 1e-4 * a * a:.5f}" for a in np.arange(-5, 15, 0.5)),
    "one point repeated": rows(np.full(50, 0.5), np.full(50, 0.1)),
    "vertical line": rows(np.full(50, 0.5), np.linspace(0, 1, 50)),
}


def normalised(x, y):
    """The app's convention: leading edge (smallest x) at the origin, x extent = 1."""
    i = int(np.argmin(x))
    s = 1.0 / (x.max() - x.min())
    return np.column_stack([(x - x[i]) * s, (y - y[i]) * s])


def outline(af):
    return np.column_stack([np.concatenate([af.xu[::-1], af.xl[1:]]), np.concatenate([af.yu[::-1], af.yl[1:]])])


def farthest(points, polyline):
    """Largest distance from one of ``points`` to ``polyline``."""
    a, b = polyline[:-1], polyline[1:]
    ab = b - a
    l2 = np.maximum((ab ** 2).sum(1), 1e-300)
    worst = 0.0
    for p in points:
        t = np.clip(((p - a) * ab).sum(1) / l2, 0, 1)
        worst = max(worst, float(np.min(np.hypot(*(p - (a + t[:, None] * ab)).T))))
    return worst


def deviation(af, ref, transform):
    true = normalised(*transform(*loop(ref)))
    read = outline(af)
    return max(farthest(read, true), farthest(true, read))


@pytest.mark.parametrize("name", GOOD)
def test_good_file_gives_the_true_outline(name):
    content, ref, transform = GOOD[name]
    af = parse_airfoil_file(content, chord=1.0)
    assert np.all(np.isfinite(outline(af)))
    assert (af.xu[0], af.yu[0]) == (af.xl[0], af.yl[0]) == (0.0, 0.0)      # LE at the origin
    assert max(af.xu[-1], af.xl[-1]) == pytest.approx(1.0)                 # chord = x extent
    assert np.all(np.diff(af.xu) >= 0) and np.all(np.diff(af.xl) >= 0)
    assert np.interp(0.5, af.xu, af.yu) > np.interp(0.5, af.xl, af.yl)
    assert deviation(af, ref, transform) < TOL
    # the rest of the app must accept it too
    s = split_at(close_small_te_gap(af))
    for kind in (C_GRID, RECT):
        d = build_domain(s, kind, r_inlet=15, l_wake=20, l_top=15, l_bottom=15)
        assert to_ansys_txt(d)
        plan_mesh(d, s, 2e6)


@pytest.mark.parametrize("name", BAD)
def test_bad_file_is_rejected_with_a_translated_message(name):
    with pytest.raises(AirfoilError) as e:
        parse_airfoil_file(BAD[name])
    assert tr_error(e.value, "tr") != str(e.value)


def test_nose_that_wraps_around_x0_keeps_its_point_order():
    """Cambered NACA sections (as XFOIL writes them) have upper-surface points at x < 0.
    Written as two LE -> TE blocks, the nose came out as a zigzag: sorting by x mixed the
    points before and after the foremost one."""
    ref = shape("4412", 201)
    text = "T\n201 201\n" + rows(ref[0], ref[1], "{:.7f} {:.7f}") + "\n" + rows(ref[2], ref[3], "{:.7f} {:.7f}")
    af = parse_airfoil_file(text)
    assert deviation(af, ref, same) < 1e-5
    length = lambda p: float(np.hypot(*np.diff(p, axis=0).T).sum())
    assert length(outline(af)) == pytest.approx(length(normalised(*loop(ref))), rel=1e-4)


def test_file_without_a_nose_point_keeps_every_point():
    text = "N\n60 60\n" + rows(XU[1:], YU[1:]) + "\n" + rows(XL[1:], YL[1:])
    af = parse_airfoil_file(text)
    assert len(af.xu) + len(af.xl) == 60 + 60 + 1          # the foremost point is shared
    true = normalised(np.concatenate([XU[1:][::-1], XL[1:]]), np.concatenate([YU[1:][::-1], YL[1:]]))
    assert farthest(true, outline(af)) < 1e-6 and farthest(outline(af), true) < 1e-6
    # symmetric section: both first points straight above each other
    sym = shape("0012", 41)
    af = parse_airfoil_file("S\n40 40\n" + rows(sym[0][1:], sym[1][1:]) + "\n" + rows(sym[2][1:], sym[3][1:]))
    assert len(af.xu) + len(af.xl) == 40 + 40 + 1


@pytest.mark.parametrize("code", ["0012", "2412", "6409", "0030", "23012"])
def test_reversed_file_is_recognised_and_mirrored(code):
    ref = shape(code, 81)
    x, y = loop(ref)
    forward = parse_airfoil_file(rows(x, y))
    assert not looks_reversed(forward)
    backward = parse_airfoil_file(rows(1.0 - x, y))          # leading edge at the right
    assert looks_reversed(backward)
    fixed = parse_airfoil_file(rows(1.0 - x, y), mirror=True)
    assert not looks_reversed(fixed)
    assert deviation(fixed, ref, same) < TOL


def test_flat_back_section_is_not_taken_as_reversed():
    """Wind-turbine root sections have a base nearly as thick as the nose region."""
    x = 0.5 * (1 - np.cos(np.linspace(0, np.pi, 61)))
    half = shape("0030", 61)[1] + 0.05 * x                    # NACA 0030 with a 10% thick base
    text = rows(np.concatenate([x[::-1], x[1:]]), np.concatenate([half[::-1], -half[1:]]))
    assert not looks_reversed(parse_airfoil_file(text))


def test_chord_line_angle():
    assert chord_line_angle(parse_airfoil_file(rows(X, Y))) == pytest.approx(0.0, abs=0.2)
    for deg in (5, -10):
        af = parse_airfoil_file(rows(*rotated(deg)(X, Y)))
        assert chord_line_angle(af) == pytest.approx(deg, abs=0.3)


@pytest.mark.parametrize("name,stem", [
    ("naca 2412 (v2).final.dat", "naca_2412_v2_.final"), ("Ölçü kanadı.DAT", "Olcu_kanadi"),
    ("ÇĞİÖŞÜ çğıöşü.txt", "CGIOSU_cgiosu"), ("日本.dat", "custom"), ("noext", "noext"), ("..dat", "custom"),
    ("a/b\\c:d*e?.csv", "a_b_c_d_e"),
])
def test_safe_file_stem(name, stem):
    assert safe_file_stem(name) == stem


def test_large_file_is_read_quickly():
    import time
    big = rows(*loop(shape("2412", 20000)))            # 0.7 MB, 40 000 points
    t0 = time.perf_counter()
    af = parse_airfoil_file(big)
    assert len(af.xu) > 19000 and time.perf_counter() - t0 < 2.0
