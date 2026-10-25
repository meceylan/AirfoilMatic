"""Airfoil geometry: NACA 4/5-digit generation and custom .dat parsing.

Every airfoil is returned as an ``Airfoil`` object holding the upper and lower
surfaces ordered from leading edge (LE) to trailing edge (TE), already scaled
to the requested chord. ``split_at`` cuts both surfaces at a given x so the
domain topology can attach vertical split lines there.
"""
from dataclasses import dataclass

import numpy as np

# Default chordwise split location (fraction of chord). See README:
# "Why X = 0.3c?"
DEFAULT_SPLIT = 0.3

# NACA 5-digit standard (non-reflexed) mean-line constants: P -> (m, k1)
NACA5_TABLE = {
    10: (0.0580, 361.400),
    20: (0.1260, 51.640),
    30: (0.2025, 15.957),
    40: (0.2900, 6.643),
    50: (0.3910, 3.230),
}

# Thickness polynomial; the last coefficient -0.1036 (instead of the
# original -0.1015) gives a closed, sharp trailing edge.
_THICK = (0.2969, -0.1260, -0.3516, 0.2843, -0.1036)


class AirfoilError(ValueError):
    """Raised for invalid airfoil input (bad NACA code, unreadable file...)."""


@dataclass
class Airfoil:
    xu: np.ndarray  # upper surface, LE -> TE
    yu: np.ndarray
    xl: np.ndarray  # lower surface, LE -> TE
    yl: np.ndarray
    chord: float
    name: str

    @property
    def te_gap(self):
        return float(np.hypot(self.xu[-1] - self.xl[-1], self.yu[-1] - self.yl[-1]))

    @property
    def le(self):
        return float(self.xu[0]), float(self.yu[0])


@dataclass
class SplitAirfoil:
    """Airfoil cut into the four segments written to the Ansys file."""
    upper_front: tuple  # (x, y) LE -> split
    upper_rear: tuple   # split -> TE
    lower_front: tuple  # LE -> split
    lower_rear: tuple   # split -> TE
    x_split: float
    chord: float
    name: str

    @property
    def le(self):
        return float(self.upper_front[0][0]), float(self.upper_front[1][0])

    @property
    def te_upper(self):
        return float(self.upper_rear[0][-1]), float(self.upper_rear[1][-1])

    @property
    def te_lower(self):
        return float(self.lower_rear[0][-1]), float(self.lower_rear[1][-1])

    @property
    def split_upper(self):
        return float(self.upper_rear[0][0]), float(self.upper_rear[1][0])

    @property
    def split_lower(self):
        return float(self.lower_rear[0][0]), float(self.lower_rear[1][0])

    @property
    def te_gap(self):
        (xu, yu), (xl, yl) = self.te_upper, self.te_lower
        return float(np.hypot(xu - xl, yu - yl))


def cosine_spacing(n_points):
    """Full-cosine x/c distribution: clustered at both LE and TE."""
    beta = np.linspace(0.0, np.pi, n_points)
    return 0.5 * (1.0 - np.cos(beta))


# Original NACA last coefficient: open (blunt) trailing edge, about 0.021*t
# (2.1% of the thickness) thick at x = c (e.g. 0.25% c for a 12% airfoil).
A4_BLUNT = -0.1015


def _thickness(xc, t, blunt_te=False):
    a0, a1, a2, a3, a4 = _THICK
    if blunt_te:
        a4 = A4_BLUNT
    return 5.0 * t * (a0 * np.sqrt(xc) + a1 * xc + a2 * xc**2 + a3 * xc**3 + a4 * xc**4)


def _surfaces(xc, yt, yc, dyc):
    theta = np.arctan(dyc)
    xu = xc - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = xc + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)
    return xu, yu, xl, yl


def naca4(code, chord=1.0, n_points=201, blunt_te=False):
    if len(code) != 4 or not code.isdigit():
        raise AirfoilError("NACA 4-digit code must be 4 digits")
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:4]) / 100.0
    if not 0 < t <= 0.40:
        raise AirfoilError("Thickness must be between 1% and 40%")
    if m > 0 and p == 0:
        raise AirfoilError("Cambered NACA 4-digit needs a camber position (2nd digit) > 0")

    xc = cosine_spacing(n_points)
    yt = _thickness(xc, t, blunt_te)
    yc = np.zeros_like(xc)
    dyc = np.zeros_like(xc)
    if m > 0:
        front = xc <= p
        rear = ~front
        yc[front] = m / p**2 * (2 * p * xc[front] - xc[front] ** 2)
        dyc[front] = 2 * m / p**2 * (p - xc[front])
        yc[rear] = m / (1 - p) ** 2 * (1 - 2 * p + 2 * p * xc[rear] - xc[rear] ** 2)
        dyc[rear] = 2 * m / (1 - p) ** 2 * (p - xc[rear])
    xu, yu, xl, yl = _surfaces(xc, yt, yc, dyc)
    _check_surfaces(xu, xl)
    return Airfoil(xu * chord, yu * chord, xl * chord, yl * chord, chord, f"NACA {code}")


def _check_surfaces(xu, xl):
    """Reject extreme profiles whose surfaces run past the trailing edge."""
    # A blunt, cambered TE legitimately ends a fraction of a percent past x = 1.
    if max(xu.max(), xl.max()) > 1.01:
        raise AirfoilError("Surface extends past the trailing edge (camber/thickness too large)")


def naca5(code, chord=1.0, n_points=201, blunt_te=False):
    if len(code) != 5 or not code.isdigit():
        raise AirfoilError("NACA 5-digit code must be 5 digits")
    L = int(code[0])
    P = int(code[1:3])
    t = int(code[3:5]) / 100.0
    if P not in NACA5_TABLE:
        raise AirfoilError(
            "Unsupported NACA 5-digit camber position (only standard, non-reflexed "
            "series: 2nd-3rd digits 10, 20, 30, 40, 50)"
        )
    if not 0 < t <= 0.40:
        raise AirfoilError("Thickness must be between 1% and 40%")
    m, k1 = NACA5_TABLE[P]
    scale = (L * 0.15) / 0.3  # table is tabulated for design Cl = 0.3

    xc = cosine_spacing(n_points)
    yt = _thickness(xc, t, blunt_te)
    front = xc <= m
    rear = ~front
    yc = np.empty_like(xc)
    dyc = np.empty_like(xc)
    yc[front] = k1 / 6.0 * (xc[front] ** 3 - 3 * m * xc[front] ** 2 + m**2 * (3 - m) * xc[front])
    dyc[front] = k1 / 6.0 * (3 * xc[front] ** 2 - 6 * m * xc[front] + m**2 * (3 - m))
    yc[rear] = k1 * m**3 / 6.0 * (1 - xc[rear])
    dyc[rear] = -k1 * m**3 / 6.0
    yc *= scale
    dyc *= scale
    xu, yu, xl, yl = _surfaces(xc, yt, yc, dyc)
    _check_surfaces(xu, xl)
    return Airfoil(xu * chord, yu * chord, xl * chord, yl * chord, chord, f"NACA {code}")


def naca(code, chord=1.0, n_points=201, blunt_te=False):
    code = code.strip()
    if len(code) == 4:
        return naca4(code, chord, n_points, blunt_te)
    if len(code) == 5:
        return naca5(code, chord, n_points, blunt_te)
    raise AirfoilError("NACA code must have 4 or 5 digits")


# --------------------------------------------------------------------------
# Custom coordinate files (Selig or Lednicer)
# --------------------------------------------------------------------------

def _numeric_rows(text):
    rows = []
    for line in text.splitlines():
        parts = line.replace(",", " ").split()
        if len(parts) < 2:
            continue
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    arr = np.array(rows, dtype=float).reshape(-1, 2)
    return arr[np.all(np.isfinite(arr), axis=1)]  # drop NaN / inf rows


def _clean_surface(x, y):
    """Order LE -> TE by x and drop duplicate x values."""
    order = np.argsort(x, kind="stable")
    x, y = x[order], y[order]
    x, idx = np.unique(x, return_index=True)
    return x, y[idx]


def parse_airfoil_file(content, chord=1.0, name="Custom"):
    """Parse a Selig or Lednicer coordinate file into an ``Airfoil``.

    Coordinates are normalised so the LE is at x=0 and the chord is 1, then
    scaled to ``chord``.
    """
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="ignore")
    rows = _numeric_rows(content)
    if len(rows) < 3:
        raise AirfoilError("File does not contain enough coordinate rows")

    # Lednicer: first numeric row holds the two point counts. Only accept it
    # when both are integers and match the remaining rows; otherwise treat the
    # row as part of a Selig header / data.
    c0, c1 = rows[0]
    is_counts = (c0 > 1.5 and c1 > 1.5 and abs(c0 - round(c0)) < 1e-9
                 and abs(c1 - round(c1)) < 1e-9 and len(rows) - 1 >= round(c0) + round(c1))
    if is_counts:
        n_up, n_lo = int(round(c0)), int(round(c1))
        pts = rows[1:]
        a, b = pts[:n_up], pts[n_up:n_up + n_lo]
    else:
        if c0 > 1.5 and c1 > 1.5:
            rows = rows[1:]  # numeric title line such as "2412 15"
        # Selig: one loop TE -> LE -> TE. Split at the minimum-x point.
        le = int(np.argmin(rows[:, 0]))
        if le == 0 or le == len(rows) - 1:
            raise AirfoilError("Could not find the leading edge inside the point loop")
        a, b = rows[: le + 1][::-1], rows[le:]

    xa, ya = _clean_surface(a[:, 0], a[:, 1])
    xb, yb = _clean_surface(b[:, 0], b[:, 1])
    if len(xa) < 3 or len(xb) < 3:
        raise AirfoilError("Each surface needs at least 3 distinct points")

    # Upper surface = the one that is higher at mid-chord.
    xm = 0.5 * (min(xa[-1], xb[-1]) + max(xa[0], xb[0]))
    if np.interp(xm, xa, ya) >= np.interp(xm, xb, yb):
        xu, yu, xl, yl = xa, ya, xb, yb
    else:
        xu, yu, xl, yl = xb, yb, xa, ya

    # Share a single LE point.
    x0 = min(xu[0], xl[0])
    if xu[0] <= xl[0]:
        xl, yl = np.insert(xl, 0, xu[0]), np.insert(yl, 0, yu[0])
        xl, yl = _clean_surface(xl, yl)
    else:
        xu, yu = np.insert(xu, 0, xl[0]), np.insert(yu, 0, yl[0])
        xu, yu = _clean_surface(xu, yu)

    x1 = max(xu[-1], xl[-1])
    span = x1 - x0
    if span <= 0:
        raise AirfoilError("Invalid chord in file")
    s = chord / span
    return Airfoil((xu - x0) * s, yu * s, (xl - x0) * s, yl * s, chord, name)


def close_small_te_gap(af, rel_tol=1e-4):
    """Snap a nearly-closed TE (gap < rel_tol*c) to a single point.

    Tiny gaps make DesignModeler fail to build a surface; real blunt trailing
    edges (larger gaps) are kept and closed later with a separate edge.
    """
    if 0 < af.te_gap < rel_tol * af.chord:
        xm = 0.5 * (af.xu[-1] + af.xl[-1])
        ym = 0.5 * (af.yu[-1] + af.yl[-1])
        xu, yu, xl, yl = af.xu.copy(), af.yu.copy(), af.xl.copy(), af.yl.copy()
        xu[-1], yu[-1], xl[-1], yl[-1] = xm, ym, xm, ym
        return Airfoil(xu, yu, xl, yl, af.chord, af.name)
    return af


def _split_surface(x, y, xs):
    ys = float(np.interp(xs, x, y))
    # Drop points that would create a sliver segment next to the split.
    dx = np.diff(x)
    tol = 0.25 * float(np.median(dx)) if len(dx) else 0.0
    front_mask = x < xs - tol
    rear_mask = x > xs + tol
    xf = np.append(x[front_mask], xs)
    yf = np.append(y[front_mask], ys)
    xr = np.insert(x[rear_mask], 0, xs)
    yr = np.insert(y[rear_mask], 0, ys)
    return (xf, yf), (xr, yr)


def split_at(af, x_split_frac=DEFAULT_SPLIT):
    """Cut both surfaces at x = x_split_frac * chord (vertical cut)."""
    if not 0.05 <= x_split_frac <= 0.9:
        raise AirfoilError("Split location must be between 0.05c and 0.9c")
    xs = x_split_frac * af.chord
    uf, ur = _split_surface(af.xu, af.yu, xs)
    lf, lr = _split_surface(af.xl, af.yl, xs)
    return SplitAirfoil(uf, ur, lf, lr, xs, af.chord, af.name)
