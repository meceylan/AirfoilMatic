"""Mesh sizing assistant for Ansys Meshing (Edge Sizing + Mapped Face Meshing).

All edges use geometric (single-direction) spacing, which is what Ansys Edge
Sizing produces with ``Number of Divisions`` + ``Bias Factor``. Ansys defines
the bias factor as the ratio of the largest to the smallest element on the
edge, so for a geometric progression with ratio r over n divisions:

    bias = r**(n - 1)

In a mapped (structured) mesh, opposite sides of a block must have the same
number of divisions, so the plan is built from four counts that are shared by
every block:

    n_normal  - wall-normal direction (all vertical lines, front axis, outlet)
    n_front   - airfoil LE -> split   (and the inlet edge opposite to it)
    n_rear    - airfoil split -> TE   (and the top/bottom edge opposite to it)
    n_wake    - TE -> outlet          (wake axis and top/bottom wake edges)

    cells = 2 * n_normal * (n_front + n_rear + n_wake)        (sharp TE)
"""
import math
from dataclasses import dataclass, field

import numpy as np

from .topology import C_GRID

# Default sizing inputs (fractions of chord unless stated otherwise)
DEFAULTS = dict(
    y_plus=1.0,
    growth=1.10,        # wall-normal growth ratio
    ds_le=0.001,        # LE spacing / c
    ds_split=0.01,      # spacing at the split line / c
    ds_te=0.001,        # TE spacing / c
    wake_growth=1.10,   # streamwise growth ratio in the wake
)

MAX_GOOD_GROWTH = 1.2


# --------------------------------------------------------------------------
# Boundary-layer estimates (flat-plate correlations at x = c)
# --------------------------------------------------------------------------

def reynolds(velocity, density, viscosity, chord):
    return density * velocity * chord / viscosity


MIN_RE = 1.0e3


def skin_friction(re):
    """Schlichting turbulent flat-plate correlation, valid for Re < 1e9."""
    if re < MIN_RE:
        raise ValueError(f"Reynolds number must be at least {MIN_RE:g}")
    return (2.0 * math.log10(re) - 0.65) ** -2.3


def first_cell_height(re, y_plus, chord):
    """First-cell height for a target y+ (flat-plate estimate at x = c).

    dy = y+ * nu / u_tau with u_tau = U*sqrt(Cf/2), written in chord units:
    dy/c = y+ * sqrt(2/Cf) / Re  (independent of U, rho, mu individually).
    """
    cf = skin_friction(re)
    return chord * y_plus * math.sqrt(2.0 / cf) / re


def bl_thickness_turbulent(re, chord):
    return chord * 0.37 * re ** -0.2


def bl_thickness_laminar(re, chord):
    return chord * 5.0 / math.sqrt(re)


# --------------------------------------------------------------------------
# Geometric-progression helpers
# --------------------------------------------------------------------------

def geometric_length(ds, r, n):
    if abs(r - 1.0) < 1e-12:
        return ds * n
    if r > 1.0 and n * math.log(r) > 700.0:
        return math.inf  # avoids OverflowError for very large r**n
    return ds * (r**n - 1.0) / (r - 1.0)


def n_for_growth(length, ds, r):
    """Divisions needed to cover ``length`` from first cell ``ds`` at ratio r."""
    if length <= ds:
        return 1
    if r <= 1.0 + 1e-9:
        return max(1, math.ceil(length / ds))
    return max(1, math.ceil(math.log(1.0 + length * (r - 1.0) / ds) / math.log(r)))


def ratio_for(length, ds, n):
    """Growth ratio so that n cells starting at ``ds`` exactly fill ``length``."""
    if n <= 1:
        return 1.0
    if abs(n * ds - length) < 1e-12 * length:
        return 1.0
    f = lambda r: geometric_length(ds, r, n) - length
    if n * ds < length:
        lo, hi = 1.0 + 1e-12, 2.0
        while f(hi) < 0:
            hi *= 2.0
    else:
        lo, hi = 1e-6, 1.0 - 1e-12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def two_end_spacing(length, ds_a, ds_b):
    """Divisions and ratio for a geometric edge from spacing ds_a to ds_b.

    Closed form: r = (L - a) / (L - b), n = 1 + ln(b/a) / ln(r).
    n is rounded to an integer; the bias (b/a) is kept and the end spacings
    are recomputed from it.
    """
    if length <= max(ds_a, ds_b):
        raise ValueError("Edge is shorter than the requested cell size")
    if abs(ds_a - ds_b) < 1e-12 * length:
        n = max(2, round(length / ds_a))
        return n, 1.0
    r = (length - ds_a) / (length - ds_b)
    n = max(2, round(1.0 + math.log(ds_b / ds_a) / math.log(r)))
    r = (ds_b / ds_a) ** (1.0 / (n - 1))
    return n, r


def polyline_length(x, y):
    return float(np.sum(np.hypot(np.diff(x), np.diff(y))))


# --------------------------------------------------------------------------
# Sizing plan
# --------------------------------------------------------------------------

@dataclass
class EdgeSizing:
    group: str            # translation key of the edge group
    edges: list           # translation keys of the physical edges
    length: float         # length of one edge [m]
    n: int                # Number of Divisions
    ratio: float          # geometric growth ratio (>1 grows away from small end)
    small_end: str        # translation key: where the smallest cell is

    @property
    def bias(self):
        if self.n <= 1:
            return 1.0
        r = self.ratio if self.ratio >= 1 else 1.0 / self.ratio
        return r ** (self.n - 1)

    @property
    def growth(self):
        return self.ratio if self.ratio >= 1 else 1.0 / self.ratio

    @property
    def ds_min(self):
        r = self.growth
        if abs(r - 1.0) < 1e-12:
            return self.length / self.n
        return self.length * (r - 1.0) / (r**self.n - 1.0)

    @property
    def ds_max(self):
        return self.ds_min * self.bias


@dataclass
class MeshPlan:
    re: float
    dy1: float
    delta_turb: float
    delta_lam: float
    n_bl: int
    n_normal: int
    n_front: int
    n_rear: int
    n_wake: int
    n_closure: int
    cells: int
    edges: list = field(default_factory=list)
    params: dict = field(default_factory=dict)

    @property
    def max_growth(self):
        return max(e.growth for e in self.edges)


def plan_mesh(domain, af, re, refine=1.0, max_wake_cell=None, **kwargs):
    """Build the Edge Sizing plan for a domain.

    ``refine`` scales all cell sizes by 1/refine (refine=sqrt(2) roughly
    doubles the cell count in 2D) and the growth ratios by r**(1/refine), which
    is the consistent way to build a grid family for a convergence study.
    """
    p = dict(DEFAULTS)
    p.update({k: v for k, v in kwargs.items() if v is not None})
    c = af.chord
    k = float(refine)

    growth = p["growth"] ** (1.0 / k)
    wake_growth = p["wake_growth"] ** (1.0 / k)
    dy1 = first_cell_height(re, p["y_plus"], c) / k
    ds_le, ds_split, ds_te = (p[n] * c / k for n in ("ds_le", "ds_split", "ds_te"))

    delta_t = bl_thickness_turbulent(re, c)
    delta_l = bl_thickness_laminar(re, c)
    n_bl = n_for_growth(delta_t, dy1, growth)

    d = domain
    edges = []

    # ---- airfoil, chordwise -------------------------------------------------
    uf = d.get("af_upper_front")
    lf = d.get("af_lower_front")
    ur = d.get("af_upper_rear")
    lr = d.get("af_lower_rear")
    L_front = max(polyline_length(uf.x, uf.y), polyline_length(lf.x, lf.y))
    L_rear = max(polyline_length(ur.x, ur.y), polyline_length(lr.x, lr.y))

    n_front, r_front = two_end_spacing(L_front, ds_le, ds_split)
    n_rear, r_rear = two_end_spacing(L_rear, ds_te, ds_split)  # small end at TE
    edges.append(EdgeSizing("g_af_front", ["af_upper_front", "af_lower_front"],
                            L_front, n_front, r_front, "end_le"))
    edges.append(EdgeSizing("g_af_rear", ["af_upper_rear", "af_lower_rear"],
                            L_rear, n_rear, r_rear, "end_te"))

    # ---- outer edges opposite the airfoil -----------------------------------
    x_le, y_le = af.le
    # The side opposite the airfoil front is a chain of two edges: inlet half
    # (arc or vertical line) + front segment of the top/bottom boundary.
    # Divisions are shared proportionally to length, uniform spacing.
    if d.kind == C_GRID:
        R = d.y_top
        L_in = R * (math.pi / 2 + math.asin(max(-1.0, min(1.0, abs(y_le) / R))))
    else:
        L_in = max(d.y_top - y_le, d.y_bottom + y_le)
    L_tf = d.x_split - d.x_top0
    if L_tf <= 1e-9 * c:
        # C-grid: the arc half alone is the side opposite the airfoil front.
        edges.append(EdgeSizing("g_inlet", ["inlet_up", "inlet_low"],
                                L_in, n_front, 1.0, "end_uniform"))
    else:
        n_front = max(n_front, 2)
        n_in = max(1, min(n_front - 1, round(n_front * L_in / (L_in + L_tf))))
        edges.append(EdgeSizing("g_inlet", ["inlet_up", "inlet_low"],
                                L_in, n_in, 1.0, "end_uniform"))
        edges.append(EdgeSizing("g_top_front", ["top_front", "bottom_front"],
                                L_tf, n_front - n_in, 1.0, "end_uniform"))

    # Same divisions and bias as the airfoil rear so mesh lines stay vertical.
    L_mid = d.x_te - d.x_split
    edges.append(EdgeSizing("g_top_mid", ["top_mid", "bottom_mid"],
                            L_mid, n_rear, r_rear, "end_te"))

    # ---- wake -----------------------------------------------------------------
    L_wake = d.x_exit - d.x_te
    n_wake = n_for_growth(L_wake, ds_te, wake_growth)
    r_wake = ratio_for(L_wake, ds_te, n_wake)
    if max_wake_cell is not None:
        # Cap the last wake element (e.g. at the far-field element size) so the
        # wake axis does not end with elements much larger than its surroundings.
        cap = max_wake_cell / k
        if ds_te * r_wake ** (n_wake - 1) > cap and cap > ds_te:
            n_wake, r_wake = two_end_spacing(L_wake, ds_te, cap)
    edges.append(EdgeSizing("g_wake", ["wake_axis", "top_wake", "bottom_wake"],
                            L_wake, n_wake, r_wake, "end_te"))

    # ---- wall-normal ------------------------------------------------------------
    normal_edges = [
        ("front_axis", d.get("front_axis"), "end_airfoil"),
        ("split_up", d.get("split_up"), "end_airfoil"),
        ("split_low", d.get("split_low"), "end_airfoil"),
        ("te_up", d.get("te_up"), "end_airfoil"),
        ("te_low", d.get("te_low"), "end_airfoil"),
    ]
    wake_y = d.get("wake_axis").y[0]
    lengths = [polyline_length(cv.x, cv.y) for _, cv, _ in normal_edges]
    lengths += [d.y_top - wake_y, d.y_bottom + wake_y]
    n_normal = n_for_growth(max(lengths), dy1, growth)

    for key, cv, end in normal_edges:
        L = polyline_length(cv.x, cv.y)
        edges.append(EdgeSizing("g_normal", [key], L, n_normal,
                                ratio_for(L, dy1, n_normal), end))

    # Blunt TE: closure edge is split in two by the wake axis; each half adds
    # its divisions to the outlet side of the wake blocks.
    n_closure = 0
    if d.blunt_te:
        gap = af.te_gap
        n_half = max(2, math.ceil(0.5 * gap / max(ds_te, dy1)))
        n_closure = 2 * n_half
        edges.append(EdgeSizing("g_te_closure", ["te_closure"], gap, n_closure, 1.0, "end_uniform"))

    n_out = n_normal + n_closure // 2
    for key, L in (("outlet_up", d.y_top - wake_y), ("outlet_low", d.y_bottom + wake_y)):
        edges.append(EdgeSizing("g_outlet", [key], L, n_out, ratio_for(L, dy1, n_out), "end_axis"))

    cells = 2 * n_normal * (n_front + n_rear) + 2 * n_out * n_wake

    return MeshPlan(re=re, dy1=dy1, delta_turb=delta_t, delta_lam=delta_l, n_bl=n_bl,
                    n_normal=n_normal, n_front=n_front, n_rear=n_rear, n_wake=n_wake,
                    n_closure=n_closure, cells=cells, edges=edges,
                    params=dict(p, refine=k, growth_eff=growth, wake_growth_eff=wake_growth))


# --------------------------------------------------------------------------
# Inflation (prism layer) settings for unstructured / quad-dominant meshes
# --------------------------------------------------------------------------

@dataclass
class InflationPlan:
    re: float
    first_layer: float      # Ansys "First Layer Thickness" [m]
    growth: float           # Ansys "Growth Rate"
    layers: int             # Ansys "Maximum Layers"
    total: float            # total inflation thickness [m]
    last_layer: float       # thickness of the outermost layer [m]
    delta_turb: float
    delta_lam: float
    surface_size: float     # suggested airfoil edge element size [m]


def plan_inflation(re, chord, y_plus=1.0, growth=1.2, coverage=1.0, refine=1.0):
    """Inflation layers that start at the y+ first-cell height and cover
    ``coverage`` x the turbulent boundary-layer thickness at the TE.

    ``refine`` scales the first layer by 1/refine and the growth rate by
    growth**(1/refine) for a consistent grid family.
    """
    k = float(refine)
    g = growth ** (1.0 / k)
    dy1 = first_cell_height(re, y_plus, chord) / k
    delta_t = bl_thickness_turbulent(re, chord)
    target = coverage * delta_t
    n = n_for_growth(target, dy1, g)
    total = geometric_length(dy1, g, n)
    last = dy1 * g ** (n - 1)
    return InflationPlan(re=re, first_layer=dy1, growth=g, layers=n, total=total,
                         last_layer=last, delta_turb=delta_t,
                         delta_lam=bl_thickness_laminar(re, chord),
                         surface_size=last)
