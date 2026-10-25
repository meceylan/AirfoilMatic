"""Domain topology: outer boundaries and block split lines.

Block layout (both domain types), 6 four-sided blocks:

                 top boundary
      +-----------+-----------+-------------------+
      |  front-   |   mid-    |      wake-        |
 inlet|  top      |   top     |      top          |outlet
      +---axis----LE~~airfoil~~TE----wake axis----+
      |  front-   |   mid-    |      wake-        |
      |  bottom   |   bottom  |      bottom       |
      +-----------+-----------+-------------------+
              x = split     x = TE

For the C-grid, the inlet arc is centred on the split location (x = 0.3c),
so the arc ends exactly where the vertical split lines meet the outer
boundary. The front region is then bounded only by the two arc halves, with
no short straight piece between the arc and the split line, and every block
is a clean four-sided face. (This is the classic C-mesh layout: semicircle
centred on the vertical split line, rectangle behind it.) The exported end
points of the arc, the straight boundary and the split line are identical,
so DesignModeler sees one shared vertex there.
"""
from dataclasses import dataclass, field

import numpy as np

from .geometry import SplitAirfoil

C_GRID = "c_grid"
RECT = "rect"

LINE_POINTS = 50
ARC_POINTS = 100


@dataclass
class Curve:
    key: str      # stable identifier, also used for translations
    kind: str     # "airfoil" | "boundary" | "split"
    x: np.ndarray
    y: np.ndarray


@dataclass
class Domain:
    kind: str
    curves: list = field(default_factory=list)
    # Characteristic dimensions used by the mesh sizing module
    x_split: float = 0.0
    x_te: float = 0.0
    x_inlet: float = 0.0      # x of inlet at the axis (C-grid arc apex)
    x_exit: float = 0.0
    x_top0: float = 0.0       # x where the straight top/bottom boundaries start
    y_top: float = 0.0
    y_bottom: float = 0.0
    blunt_te: bool = False
    chord: float = 1.0

    def get(self, key):
        for c in self.curves:
            if c.key == key:
                return c
        raise KeyError(key)

    def by_kind(self, kind):
        return [c for c in self.curves if c.kind == kind]


def _line(p0, p1, n=LINE_POINTS):
    return np.linspace(p0[0], p1[0], n), np.linspace(p0[1], p1[1], n)


def build_domain(af: SplitAirfoil, kind=C_GRID, r_inlet=10.0, l_wake=20.0,
                 l_top=10.0, l_bottom=10.0, blunt_tol=1e-4):
    """Create outer boundaries and split lines around a split airfoil.

    Lengths are in metres. For the C-grid, ``r_inlet`` is the arc radius and
    the top/bottom boundaries sit at +-r_inlet. For the rectangle, ``r_inlet``
    is the inlet distance upstream of the LE.
    """
    c = af.chord
    xs = af.x_split
    x_le, y_le = af.le
    (xtu, ytu), (xtl, ytl) = af.te_upper, af.te_lower
    (xsu, ysu), (xsl, ysl) = af.split_upper, af.split_lower
    x_te = max(xtu, xtl)
    x_te_mid, y_te_mid = 0.5 * (xtu + xtl), 0.5 * (ytu + ytl)
    x_exit = c + l_wake
    if l_wake <= 0.5 * c:
        raise ValueError("Wake length must be at least 0.5c")
    blunt = af.te_gap >= blunt_tol * c

    if kind == C_GRID:
        y_top, y_bot = r_inlet, r_inlet
    else:
        y_top, y_bot = l_top, l_bottom

    d = Domain(kind=kind, x_split=xs, x_te=x_te, x_exit=x_exit,
               y_top=y_top, y_bottom=y_bot, blunt_te=blunt, chord=c)

    # 1) airfoil (4 segments, written in a closed loop order)
    d.curves += [
        Curve("af_upper_front", "airfoil", *af.upper_front),
        Curve("af_upper_rear", "airfoil", *af.upper_rear),
        # All four airfoil edges run LE -> TE, so one Edge Sizing (with its bias)
        # acts the same way on the upper and the lower edge in Ansys.
        Curve("af_lower_rear", "airfoil", *af.lower_rear),
        Curve("af_lower_front", "airfoil", *af.lower_front),
    ]

    # 2) outer boundaries
    if kind == C_GRID:
        if r_inlet <= max(abs(y_le), c):
            raise ValueError("Inlet radius must be larger than the chord")
        th = np.linspace(np.pi / 2, 3 * np.pi / 2, ARC_POINTS)
        # Put an exact arc vertex where the front axis meets the inlet.
        th_axis = np.pi - np.arcsin(y_le / r_inlet)
        th = np.unique(np.append(th[np.abs(th - th_axis) > 0.25 * (th[1] - th[0])], th_axis))
        x_arc, y_arc = xs + r_inlet * np.cos(th), r_inlet * np.sin(th)
        x_arc[0], y_arc[0], x_arc[-1], y_arc[-1] = xs, r_inlet, xs, -r_inlet
        d.x_inlet = xs - np.sqrt(r_inlet**2 - y_le**2)
        d.curves.append(Curve("inlet", "boundary", x_arc, y_arc))
        x_top0 = xs
    else:
        y_all = np.concatenate([af.upper_front[1], af.upper_rear[1], af.lower_front[1], af.lower_rear[1]])
        if y_top <= y_all.max() + 0.5 * c or y_bot <= -y_all.min() + 0.5 * c:
            raise ValueError("Top/bottom boundaries must be at least 0.5c away from the airfoil")
        if r_inlet <= 0.5 * c:
            raise ValueError("Inlet must be at least 0.5c upstream of the leading edge")
        d.x_inlet = -r_inlet
        d.curves.append(Curve("inlet", "boundary", *_line((-r_inlet, y_top), (-r_inlet, -y_bot))))
        x_top0 = -r_inlet
    d.x_top0 = x_top0
    d.curves += [
        Curve("top", "boundary", *_line((x_top0, y_top), (x_exit, y_top))),
        Curve("outlet", "boundary", *_line((x_exit, y_top), (x_exit, -y_bot))),
        Curve("bottom", "boundary", *_line((x_top0, -y_bot), (x_exit, -y_bot))),
    ]

    # 3) split lines
    d.curves += [
        Curve("front_axis", "split", *_line((d.x_inlet, y_le), (x_le, y_le))),
        Curve("split_up", "split", *_line((xsu, ysu), (xsu, y_top))),
        Curve("split_low", "split", *_line((xsl, ysl), (xsl, -y_bot))),
        Curve("te_up", "split", *_line((xtu, ytu), (xtu, y_top))),
        Curve("te_low", "split", *_line((xtl, ytl), (xtl, -y_bot))),
        Curve("wake_axis", "split", *_line((x_te_mid, y_te_mid), (x_exit, y_te_mid))),
    ]
    if blunt:
        d.curves.append(Curve("te_closure", "split", *_line((xtu, ytu), (xtl, ytl))))
    return d


# The six split lines, in sidebar order. Each one runs from the airfoil to the
# outer boundary.
SPLIT_LINES = ("front_axis", "split_up", "split_low", "te_up", "te_low", "wake_axis")


def select_lines(domain, keep):
    """Domain with only the chosen split lines (the blunt-TE closure, which is
    part of the airfoil wall, is always kept)."""
    from dataclasses import replace
    keep = set(keep)
    curves = [c for c in domain.curves
              if c.kind != "split" or c.key == "te_closure" or c.key in keep]
    return replace(domain, curves=curves)


def line_warnings(keep):
    """Topology problems of a split-line selection.

    Every split line connects the airfoil (inner loop) to the outer boundary.
    With two or more of them the surface is cut into that many faces. With
    exactly one, the surface is NOT divided: the line is left as a slit inside
    a single face, which Ansys cannot use as an inflation boundary and which
    meshes poorly. Mapped meshing needs all six lines (six four-sided blocks).
    """
    keep = [k for k in SPLIT_LINES if k in set(keep)]
    warnings = []
    if len(keep) == 1:
        warnings.append(("single_line", keep[0]))
    return warnings
