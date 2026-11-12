"""Airfoil geometry: NACA 4/5-digit generation and custom .dat parsing.

Every airfoil is returned as an ``Airfoil`` object holding the upper and lower
surfaces ordered from leading edge (LE) to trailing edge (TE), already scaled
to the requested chord. ``split_at`` cuts both surfaces at a given x so the
domain topology can attach vertical split lines there.
"""
import re
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
    overlap: float = 0.0   # largest overlap of the two surfaces found in a file and repaired, / chord

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

_NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eEdD][-+]?\d+)?")
_ONLY_NUMBERS = re.compile(r"^[\s\d.+\-eEdD]+$")


def _decode(content):
    """Bytes -> text. Handles the byte-order marks Windows editors and Excel write."""
    if not isinstance(content, bytes):
        return content.lstrip("﻿")
    if content[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return content.decode("utf-16", errors="ignore")
    if len(content) >= 4:
        # UTF-16 without a byte-order mark: every other byte of plain text is zero.
        if content[1::2].count(0) > len(content) // 4:
            return content.decode("utf-16-le", errors="ignore")
        if content[0::2].count(0) > len(content) // 4:
            return content.decode("utf-16-be", errors="ignore")
    return content.decode("utf-8-sig", errors="ignore")  # drops a UTF-8 BOM


def _tokens(line):
    """Split a coordinate line. Separators: whitespace, ';' or ','.

    A comma inside a whitespace/semicolon-separated token is a decimal comma
    ("0,500000  0,061200", as Excel writes in a Turkish or European locale).
    """
    parts = [p.rstrip(",") for p in line.replace(";", " ").split()]
    parts = [p for p in parts if p]
    if len(parts) >= 2:
        parts = [p.replace(",", ".") if p.count(",") == 1 and "." not in p else p for p in parts]
    return [q for p in parts for q in p.split(",") if q]


def _float(token):
    return float(token.replace("D", "E").replace("d", "e"))  # Fortran double-precision exponent


def _line_numbers(line):
    """The numbers a line starts with ([] for a text line)."""
    values = []
    for token in _tokens(line):
        try:
            values.append(_float(token))
        except ValueError:
            break  # the rest is a comment
    if len(values) < 2 and _ONLY_NUMBERS.match(line):
        # Fortran fixed-width output: columns touch when a value is negative ("0.99893-0.00016").
        values = [_float(m) for m in _NUMBER.findall(line)]
    return values


def _xy_columns(table):
    """Which two of three numeric columns hold the outline."""
    if len(table) >= 3:
        first = table[:, 0]
        if abs(first[0] - round(first[0])) < 1e-9 and np.all(np.abs(np.diff(first) - 1.0) < 1e-9):
            return [1, 2]  # running point number
        span = np.ptp(table, axis=0)
        flat = span <= 1e-9 * max(float(span.max()), 1e-300)
        if flat.sum() == 1:
            return [i for i in range(3) if not flat[i]]  # constant column: z = 0, or a span position
    return [0, 1]


def _numeric_rows(text):
    """Coordinate rows of the file as an (n, 2) array."""
    table = [v for v in (_line_numbers(line) for line in text.splitlines()) if len(v) >= 2]
    if not table:
        return np.empty((0, 2))
    if sum(len(v) >= 3 for v in table) > len(table) / 2:
        # Three columns (x y z, x 0 z, "number x y"): shorter rows are title / count lines.
        full = np.array([v[:3] for v in table if len(v) >= 3], dtype=float)
        full = full[np.all(np.isfinite(full), axis=1)]
        return full[:, _xy_columns(full)]
    arr = np.array([v[:2] for v in table], dtype=float)
    return arr[np.all(np.isfinite(arr), axis=1)]  # drop NaN / inf rows


def _is_outlier(row, rest):
    """True when ``row`` lies far outside the box of the other rows, i.e. it cannot be
    a point of the outline (a count line "61. 61." or a title such as "2412 15")."""
    lo, hi = rest.min(axis=0), rest.max(axis=0)
    pad = 0.5 * np.maximum(hi - lo, 1e-12)
    return bool(np.any(row < lo - pad) or np.any(row > hi + pad))


def _two_surfaces(rows):
    """Split the point list of a file without a count line into its two surfaces."""
    x = rows[:, 0]
    last = len(rows) - 1
    steps = np.abs(np.diff(x))
    jump = int(np.argmax(steps))
    if steps[jump] > 0.8 * np.ptp(x):
        # Two separate blocks (LE -> TE twice): Lednicer order without the count line.
        return rows[: jump + 1], rows[jump + 1:]
    le = int(np.argmin(x))
    if 0 < le < last:
        # Selig: one loop TE -> LE -> TE.
        return rows[: le + 1][::-1], rows[le:]
    te = int(np.argmax(x))
    if 0 < te < last:
        # One loop that starts at the leading edge: LE -> TE -> LE.
        return rows[: te + 1], rows[te:][::-1]
    raise AirfoilError("Could not find the leading edge inside the point loop")


def _check_order(points, span):
    """A surface must run along x. Going back by more than 5% of the chord means the rows
    are mixed up or the file holds more than one element (slat, flap, a second airfoil)."""
    x = points[:, 0]
    if float(np.max(np.maximum.accumulate(x) - x)) > 0.05 * span:
        raise AirfoilError("Points are not in order along the surface (mixed-up rows or more than one element)")


def _le_to_te(block):
    return block if block[0, 0] <= block[-1, 0] else block[::-1]


def _increasing(points):
    """Keep the points that advance in x. Repeated points, the base points of a closed
    blunt trailing edge and digitising jitter go; a second point straight above or below
    the first one (a file without a nose point) stays."""
    keep = [0]
    for i in range(1, len(points)):
        ahead = points[i, 0] > points[keep[-1], 0]
        open_nose = len(keep) == 1 and points[i, 0] == points[0, 0] and points[i, 1] != points[0, 1]
        if ahead or open_nose:
            keep.append(i)
    return points[keep]


def _split_at_nose(a, b, span):
    """Two point blocks -> two surfaces that start at the common leading-edge point.

    The blocks are joined into one loop (TE -> nose -> TE) in the order of the file and
    the loop is cut at its smallest x. Sorting the points by x instead would scramble a
    nose that wraps around x = 0, as cambered NACA sections from XFOIL do. A file without
    a nose point gets a straight segment between its two first points.
    """
    loop = np.vstack([_le_to_te(a)[::-1], _le_to_te(b)])
    moved = np.any(np.abs(np.diff(loop, axis=0)) > 1e-12 * span, axis=1)
    loop = loop[np.concatenate([[True], moved])]  # consecutive duplicates
    le = int(np.argmin(loop[:, 0]))
    if le == 0 or le == len(loop) - 1:
        raise AirfoilError("Could not find the leading edge inside the point loop")
    surfaces = []
    for part in (loop[: le + 1][::-1], loop[le:]):
        _check_order(part, span)
        surfaces.append(_increasing(part))
    return surfaces


MAX_REPAIR = 1e-3    # largest overlap of the two surfaces that is repaired, / chord
MIN_THICKNESS = 2e-5  # thickness the repaired stretch is given, / chord
MAX_TE_SHIFT = 1e-2   # a surface that stops this far short of the other is extended, / chord


def _extend(x, y, x_end, reach):
    """Add a point at ``x_end`` on the straight continuation of the end of the surface.

    The direction comes from the last point and the nearest earlier one that is at least
    ``reach`` away, so two points that sit almost on top of each other (digitising jitter)
    do not set a steep slope.
    """
    far = np.nonzero(x[-1] - x[:-1] >= reach)[0]
    i = int(far[-1]) if len(far) else 0
    slope = (y[-1] - y[i]) / (x[-1] - x[i])
    return np.append(x, x_end), np.append(y, y[-1] + slope * (x_end - x[-1]))


def _repair_overlap(xu, yu, xl, yl, span):
    """Pull apart the two surfaces where the file lets them cross or touch.

    Real files do this by a few ten-thousandths of the chord at a cusped trailing edge
    (rounded coordinates, a lower surface that ends a little short of the upper one) or
    at a thin section. The exported curves would then intersect each other and
    DesignModeler cannot build a face from them. The surfaces are moved apart, half of
    the gap to each, until they are ``MIN_THICKNESS`` apart; the shape changes by no more
    than the overlap itself. Returns the new surfaces and the largest overlap (0 when
    nothing had to be done). Overlaps beyond ``MAX_REPAIR`` are not repaired.
    """
    # A surface that ends short of the other one: look at the tip as if it went on.
    gap = xu[-1] - xl[-1]
    if gap != 0 and abs(gap) <= MAX_TE_SHIFT * span:
        sx, sy = (xl, yl) if gap > 0 else (xu, yu)
        ex, ey = _extend(sx, sy, max(xu[-1], xl[-1]), 0.005 * span)
        tip = (yu[-1] - ey[-1]) if gap > 0 else (ey[-1] - yl[-1])
        if tip < 0:
            if gap > 0:
                xl, yl = ex, ey
            else:
                xu, yu = ex, ey
    grid = np.unique(np.concatenate([xu, xl]))
    grid = grid[(grid >= max(xu[0], xl[0])) & (grid <= min(xu[-1], xl[-1]))]
    t = np.interp(grid, xu, yu) - np.interp(grid, xl, yl)
    worst = -float(t.min())
    if worst <= 1e-9 * span:
        return xu, yu, xl, yl, 0.0
    if worst > MAX_REPAIR * span:
        raise AirfoilError("Upper and lower surfaces cross each other")
    neg = np.nonzero(t < -1e-9 * span)[0]
    lo, hi = max(neg[0] - 1, 0), min(neg[-1] + 1, len(grid) - 1)
    sharp_end = abs(t[-1]) < 1e-9 * span and hi == len(grid) - 1
    need = np.maximum(MIN_THICKNESS * span - t, 0.0)
    need[:lo], need[hi + 1:] = 0.0, 0.0
    if sharp_end:
        need[-1] = 0.0   # the surfaces meet at the trailing edge and must go on doing so
    if abs(t[0]) < 1e-9 * span:
        need[0] = 0.0    # both surfaces start at the common leading-edge point
    # Both surfaces get a point at every grid value of the stretch, so the shift is exact.
    win = grid[lo: hi + 1]
    out = []
    for x, y, sign in ((xu, yu, 1.0), (xl, yl, -1.0)):
        inside = (x >= win[0]) & (x <= win[-1])
        nx = np.unique(np.concatenate([x[~inside], win, x[inside]]))
        ny = np.interp(nx, x, y)
        ny = ny + sign * 0.5 * np.interp(nx, grid, need)
        out += [nx, ny]
    return out[0], out[1], out[2], out[3], worst / span


def parse_airfoil_file(content, chord=1.0, name="Custom", mirror=False):
    """Parse a Selig or Lednicer coordinate file into an ``Airfoil``.

    The outline is moved so the leading edge (the point with the smallest x) is at the
    origin and scaled so its x extent equals ``chord``. Units, origin and point order of
    the file do not matter. ``mirror`` flips the file in x first, for an outline whose
    leading edge is at the right.
    """
    rows, counts, n_up = _file_rows(content)
    if mirror:
        rows = rows * np.array([-1.0, 1.0])
    span = float(np.ptp(rows[:, 0]))
    if span <= 0:
        raise AirfoilError("Invalid chord in file")
    a, b = (rows[:n_up], rows[n_up:]) if counts else _two_surfaces(rows)
    if len(a) < 2 or len(b) < 2:
        raise AirfoilError("Each surface needs at least 3 distinct points")
    sa, sb = _split_at_nose(a, b, span)
    if len(sa) < 3 or len(sb) < 3:
        raise AirfoilError("Each surface needs at least 3 distinct points")

    # Upper surface = the one that is higher at mid-chord.
    xm = 0.5 * (sa[0, 0] + min(sa[-1, 0], sb[-1, 0]))
    upper_first = np.interp(xm, sa[:, 0], sa[:, 1]) >= np.interp(xm, sb[:, 0], sb[:, 1])
    up, lo = (sa, sb) if upper_first else (sb, sa)
    xu, yu, xl, yl = up[:, 0], up[:, 1], lo[:, 0], lo[:, 1]

    # The two surfaces must enclose something and must not cross.
    xs = np.linspace(max(xu[0], xl[0]), min(xu[-1], xl[-1]), 203)[1:-1]
    thickness = np.interp(xs, xu, yu) - np.interp(xs, xl, yl)
    if thickness.max() < 1e-4 * span:
        raise AirfoilError("Airfoil has no thickness")
    xu, yu, xl, yl, overlap = _repair_overlap(xu, yu, xl, yl, span)

    x0, y0 = xu[0], yu[0]
    s = chord / (max(xu[-1], xl[-1]) - x0)
    return Airfoil((xu - x0) * s, (yu - y0) * s, (xl - x0) * s, (yl - y0) * s, chord, name, overlap)


def _file_rows(content):
    """Coordinate rows of a file without its title, count and parameter lines.

    Returns ``(rows, counts, n_up)``: ``counts`` is True for a Lednicer file whose count
    line matched, and then ``n_up`` rows belong to the first block.
    """
    rows = _numeric_rows(_decode(content))
    if len(rows) < 3:
        raise AirfoilError("File does not contain enough coordinate rows")

    # Lednicer: the first numeric row holds the two point counts. It is only accepted when
    # the counts match the rows exactly; in a file written in millimetres or percent a first
    # row of two large numbers is simply the first point.
    c0, c1 = rows[0]
    n_up, n_lo = int(round(c0)), int(round(c1))
    counts = (c0 > 1.5 and c1 > 1.5 and abs(c0 - n_up) < 1e-9 and abs(c1 - n_lo) < 1e-9
              and len(rows) - 1 == n_up + n_lo)
    if counts:
        rows = rows[1:]
    else:
        # Leading rows that cannot be points of the outline: a numeric title ("2412 15"),
        # a parameter line, counts that do not match, a date.
        for _ in range(5):
            if len(rows) > 3 and _is_outlier(rows[0], rows[1:]):
                rows = rows[1:]
            else:
                break
    return rows, counts, n_up


def looks_reversed(af):
    """True when the round nose seems to be at the right end of the file's outline.

    A leading edge is round and a trailing edge thin, so the section is much thicker 2%
    behind the nose than 2% ahead of the tail. (A flat-back section with a thick base
    still passes: its nose is not that much thinner than its base.)
    """
    def thickness(x):
        return float(np.interp(x, af.xu, af.yu) - np.interp(x, af.xl, af.yl))
    return thickness(0.02 * af.chord) < 0.25 * thickness(0.98 * af.chord)


def chord_line_angle(af):
    """Angle between the LE -> TE line and the x axis in degrees, positive nose-up."""
    x_te = 0.5 * (af.xu[-1] + af.xl[-1]) - af.xu[0]
    y_te = 0.5 * (af.yu[-1] + af.yl[-1]) - af.yu[0]
    return float(np.degrees(np.arctan2(-y_te, x_te)))


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


# --------------------------------------------------------------------------
# Outline used as drawn (vortex generator, flap, kinked section)
# --------------------------------------------------------------------------
#
# The normal reader splits a file into two surfaces that advance in x. A surface with a
# vortex-generator fin (vertical or forward-leaning walls) or a kink does not, so in this
# mode the points are kept as ONE closed loop in file order and only cut in two at the
# leading edge (smallest x) and the trailing edge (largest x). Nothing is sorted, dropped
# or repaired, apart from repeated points and the inner points of a flat base.

AS_IS_MIN_POINTS = 6
_FLAT = 1e-7   # points within this x distance (/ x extent) of the extreme x share the LE / TE


def _as_is_loop(rows, counts, n_up, span):
    """The file's points as one loop in file order, consecutive duplicates removed."""
    if counts:
        a, b = rows[:n_up], rows[n_up:]
    else:
        steps = np.abs(np.diff(rows[:, 0]))
        jump = int(np.argmax(steps))
        # Two blocks LE -> TE (Lednicer without the count line): the same test as _two_surfaces.
        a, b = (rows[: jump + 1], rows[jump + 1:]) if steps[jump] > 0.8 * span else (rows, None)
    if b is not None:
        if len(a) < 2 or len(b) < 2:
            raise AirfoilError("Each surface needs at least 3 distinct points")
        rows = np.vstack([_le_to_te(a)[::-1], _le_to_te(b)])   # TE -> nose -> TE, as _split_at_nose
    moved = np.any(np.abs(np.diff(rows, axis=0)) > 1e-12 * span, axis=1)
    return rows[np.concatenate([[True], moved])]


def _crosses_itself(loop, span):
    """True when two non-neighbouring edges of the closed polygon cross (touching does not count)."""
    n = len(loop)
    a, b = loop, np.roll(loop, -1, axis=0)
    eps = (1e-12 * span**2) ** 2

    def cross(u, v):
        return u[..., 0] * v[..., 1] - u[..., 1] * v[..., 0]

    for i in range(n - 2):
        j = np.arange(i + 2, n if i else n - 1)
        if len(j) == 0:
            continue
        c, e = a[j], b[j]
        di = b[i] - a[i]
        side_ce = cross(di, c - a[i]) * cross(di, e - a[i])
        side_ab = cross(e - c, a[i] - c) * cross(e - c, b[i] - c)
        if np.any((side_ce < -eps) & (side_ab < -eps)):
            return True
    return False


def _ray_hits(paths, x0, y0, direction, tol):
    """True when a wall path meets the horizontal ray from (x0, y0) towards ``direction`` (+-1)."""
    for p in paths:
        a, b = p[:-1], p[1:]
        da, db = a[:, 1] - y0, b[:, 1] - y0
        on = (da == 0) & (db == 0)                    # a piece of wall lying on the axis line
        meet = (da * db <= 0) & ~on
        with np.errstate(divide="ignore", invalid="ignore"):
            xi = a[:, 0] + np.where(meet, da / (da - db), 0.0) * (b[:, 0] - a[:, 0])
        if np.any(meet & (direction * (xi - x0) > tol)):
            return True
        if np.any(on & ((direction * (a[:, 0] - x0) > tol) | (direction * (b[:, 0] - x0) > tol))):
            return True
    return False


def parse_outline_as_is(content, chord=1.0, name="Custom", mirror=False):
    """Read a coordinate file as one closed outline, keeping every point where it was drawn.

    The file is read like ``parse_airfoil_file`` (same decoder, title / count / outlier
    handling, ``mirror`` and normalisation: LE at the origin, x extent = ``chord``). Then:

    * The points form one loop in file order (Selig style; two Lednicer blocks are joined at
      the nose). If the first and last point differ, the loop is closed between them: a gap
      below 1e-4 of the chord is snapped to one point; a larger gap behind mid-chord is the
      blunt trailing-edge closure.
    * Leading edge = the point with the smallest x (if several share it, the one nearest the
      middle of them in y). Trailing edge = the point with the largest x. If several
      neighbouring points share the largest x (a flat base drawn as part of the loop), the
      two outermost become the ends of the TE closure and the base points between them go:
      the closure is drawn as one straight edge, as for any blunt trailing edge.
    * The loop is cut at LE and TE into the upper and lower path, both LE -> TE in file
      order and never sorted by x. They are returned as ``Airfoil.xu/yu`` and ``xl/yl``.

    Rejected: fewer than 6 points, a loop that crosses itself, and an outline that crosses
    the horizontal axis lines of the domain (ahead of the LE at its height, behind the TE at
    the height of the TE / closure middle), which the inflation workflow draws.
    """
    rows, counts, n_up = _file_rows(content)
    if mirror:
        rows = rows * np.array([-1.0, 1.0])
    span = float(np.ptp(rows[:, 0]))
    if span <= 0:
        raise AirfoilError("Invalid chord in file")
    loop = _as_is_loop(rows, counts, n_up, span)

    open_te = False
    gap = float(np.hypot(*(loop[-1] - loop[0])))
    if len(loop) > 1 and gap <= 1e-12 * span:
        loop = loop[:-1]                                   # file repeats its first point
    elif gap < 1e-4 * span:
        loop = np.vstack([0.5 * (loop[0] + loop[-1]), loop[1:-1]])   # as close_small_te_gap
    else:
        # An open end is the TE closure only behind mid-chord; elsewhere it is a wall edge.
        open_te = min(loop[0, 0], loop[-1, 0]) > loop[:, 0].min() + 0.5 * span
    n = len(loop)
    if n < AS_IS_MIN_POINTS:
        raise AirfoilError("The outline needs at least 6 distinct points")
    x, y = loop[:, 0], loop[:, 1]
    x_min, x_max = float(x.min()), float(x.max())
    span = x_max - x_min

    if _crosses_itself(loop, span):
        raise AirfoilError("The outline crosses itself")
    area = 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
    if abs(area) < 1e-5 * span**2:
        raise AirfoilError("Airfoil has no thickness")

    near_le = np.nonzero(x <= x_min + _FLAT * span)[0]
    le = int(near_le[np.argmin(np.abs(y[near_le] - y[near_le].mean()))])
    if open_te:
        te_first, te_last = n - 1, 0          # the closure edge runs from the last point to the first
    else:
        flat = x >= x_max - _FLAT * span
        te_first = te_last = int(np.argmax(x))
        while flat[(te_first - 1) % n] and (te_first - 1) % n != te_last:
            te_first = (te_first - 1) % n
        while flat[(te_last + 1) % n] and (te_last + 1) % n != te_first:
            te_last = (te_last + 1) % n

    def walk(stop, step):
        idx = [le]
        while idx[-1] != stop:
            idx.append((idx[-1] + step) % n)
        return loop[idx]

    forward, backward = walk(te_first, 1), walk(te_last, -1)
    if len(forward) < 2 or len(backward) < 2:
        raise AirfoilError("Could not find the leading edge inside the point loop")
    # Counter-clockwise loop (Selig: TE -> upper -> LE -> lower): forward from the LE is the lower side.
    upper, lower = (backward, forward) if area > 0 else (forward, backward)

    x0, y0 = loop[le]
    s = chord / span
    upper = (upper - [x0, y0]) * s
    lower = (lower - [x0, y0]) * s
    tol = 1e-9 * chord
    if _ray_hits((upper, lower), 0.0, 0.0, -1.0, tol):
        raise AirfoilError("The outline crosses the front axis (the horizontal line ahead of the leading edge)")
    xm, ym = 0.5 * (upper[-1] + lower[-1])
    if _ray_hits((upper, lower), xm, ym, 1.0, tol):
        raise AirfoilError("The outline crosses the wake axis (the horizontal line behind the trailing edge)")
    return Airfoil(upper[:, 0], upper[:, 1], lower[:, 0], lower[:, 1], chord, name)


def as_is_split(af, x_split_frac=DEFAULT_SPLIT):
    """``SplitAirfoil`` for an outline used as drawn: there is no split; the front and the rear
    piece of each side are both the whole wall path, so LE, TE and TE gap come out right.
    ``x_split`` only places the centre of the C-grid inlet arc, as in the normal mode."""
    up, lo = (af.xu, af.yu), (af.xl, af.yl)
    return SplitAirfoil(up, up, lo, lo, x_split_frac * af.chord, af.chord, af.name)
