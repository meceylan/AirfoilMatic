"""Grid convergence index (GCI) of three meshes.

Procedure of Celik et al. (2008), "Procedure for estimation and reporting of uncertainty due to
discretization in CFD applications", J. Fluids Eng. 130, 078001 (Richardson extrapolation with
the safety factor 1.25). In 2D the representative cell size is h = (1/N)^(1/2).
"""
import math
import re
from dataclasses import dataclass

SAFETY = 1.25


@dataclass
class GCI:
    r21: float          # refinement ratio medium / fine (cell size)
    r32: float          # coarse / medium
    p: float            # apparent order of convergence
    phi_ext: float      # extrapolated (mesh-independent) value
    e_a: float          # relative difference fine - medium
    e_ext: float        # relative difference to the extrapolated value
    gci_fine: float     # GCI of the fine mesh (fraction)
    monotonic: bool     # False: oscillatory convergence (the GCI is then less reliable)
    diverging: bool = False   # monotonic, but the difference grows as the mesh is refined


P_MIN, P_MAX = 1e-4, 20.0


def _order(r21, r32, e21, e32, s):
    """Apparent order p: root of p = |ln|e32/e21| + q(p)| / ln r21, q = ln((r21^p - s)/(r32^p - s))
    (Celik 2008, eq. 3). The plain fixed-point iteration overflowed, divided by zero or stopped
    on a wrong p when r21 != r32; the root is bracketed on [P_MIN, P_MAX] and bisected. With two
    roots the smaller p is taken: it gives the larger (safer) uncertainty."""
    ln_e = math.log(abs(e32 / e21))
    ln_r = math.log(r21)

    def g(p):
        return p - abs(ln_e + math.log((r21 ** p - s) / (r32 ** p - s))) / ln_r

    grid = [P_MIN * (P_MAX / P_MIN) ** (k / 400) for k in range(401)]
    vals = []
    for p in grid:
        try:
            vals.append(g(p))
        except (ValueError, ZeroDivisionError, OverflowError):
            vals.append(None)
    for (a, ga), (b, gb) in zip(zip(grid, vals), zip(grid[1:], vals[1:])):
        if ga is None or gb is None or ga * gb > 0:
            continue
        for _ in range(100):
            m = 0.5 * (a + b)
            gm = g(m)
            if ga * gm <= 0:
                b = m
            else:
                a, ga = m, gm
        return 0.5 * (a + b)
    raise ValueError("The order of convergence could not be determined")


def gci(cells, values):
    """GCI from cell counts and values of three meshes (any order; sorted fine -> coarse)."""
    if any(n <= 0 for n in cells):
        raise ValueError("Cell counts must be positive")
    if len(set(cells)) != 3:
        raise ValueError("The three meshes need different cell counts")
    (n1, f1), (n2, f2), (n3, f3) = sorted(zip(cells, values), key=lambda t: -t[0])
    h1, h2, h3 = (1.0 / math.sqrt(n) for n in (n1, n2, n3))
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    if e21 == 0.0:
        return GCI(r21, r32, math.nan, f1, 0.0, 0.0, 0.0, True)
    if e32 == 0.0:
        raise ValueError("Coarse and medium values are equal: the order of convergence is undefined")
    s = math.copysign(1.0, e32 / e21)
    p = _order(r21, r32, e21, e32, s)
    phi_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1.0)
    e_a = abs((f1 - f2) / f1) if f1 else math.inf
    e_ext = abs((phi_ext - f1) / phi_ext) if phi_ext else math.inf
    # Stern et al. (2001): the difference grows as the mesh is refined -> divergence, no GCI
    return GCI(r21, r32, p, phi_ext, e_a, e_ext, SAFETY * e_a / (r21 ** p - 1.0), s > 0,
               s > 0 and abs(e21) > abs(e32))


# ---------------------------------------------------------------- from report files
LABELS = ("coarse", "medium", "fine")
_LABEL_WORDS = {"coarse": ("coarse", "kaba"), "medium": ("medium", "orta"), "fine": ("fine", "ince")}


def mesh_label(filename):
    """"coarse", "medium" or "fine" when the file name has exactly one of these words (also Turkish
    kaba / orta / ince) as a separate word, e.g. ``NACA4412_kaba.out``; otherwise None."""
    stem = str(filename).rsplit(".", 1)[0]
    # Python lowercases "İ" to "i" + combining dot; drop the dot so "İnce" reads as "ince"
    words = set(re.split(r"[^0-9a-zçğıöşü]+", stem.lower().replace("\u0307", "")))
    found = [lab for lab, names in _LABEL_WORDS.items() if words & set(names)]
    return found[0] if len(found) == 1 else None


@dataclass
class AngleGCI:
    aoa: float          # degrees
    name: str           # "Cl" or "Cd"
    cells: list         # fine, medium, coarse
    values: list        # same order
    result: object      # GCI, or None when ``error``
    error: object       # message of the ValueError of gci(), or None
    unsteady: list      # labels ("coarse" / "medium" / "fine") whose polar row is not steady


def gci_by_angle(polars, cells, digits=4):
    """GCI of Cl and Cd at every angle found in all three polars (lists of ``polar.PolarRow``, one per
    mesh, in the order of ``cells``). Angles match when equal to ``digits`` decimals (degrees)."""
    from .polar import STEADY
    by_mesh = [{round(r.aoa, digits): r for r in p} for p in polars]
    common = sorted(set(by_mesh[0]).intersection(*by_mesh[1:]))
    order = sorted(range(3), key=lambda i: -cells[i])          # fine -> coarse
    out = []
    for a in common:
        rows = [by_mesh[i][a] for i in order]
        unsteady = [LABELS[2 - k] for k, r in enumerate(rows) if r.status != STEADY]
        for name in ("Cl", "Cd"):
            values = [getattr(r, name.lower()) for r in rows]
            try:
                res, err = gci([cells[i] for i in order], values), None
            except ValueError as e:
                res, err = None, str(e)
            out.append(AngleGCI(rows[0].aoa, name, [cells[i] for i in order], values, res, err, unsteady))
    return out
