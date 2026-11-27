"""Grid convergence index (GCI) of three meshes.

Procedure of Celik et al. (2008), "Procedure for estimation and reporting of uncertainty due to
discretization in CFD applications", J. Fluids Eng. 130, 078001 (Richardson extrapolation with
the safety factor 1.25). In 2D the representative cell size is h = (1/N)^(1/2).
"""
import math
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
    p = 1.0
    for _ in range(200):          # fixed point of p = |ln|e32/e21| + q(p)| / ln r21
        q = math.log((r21 ** p - s) / (r32 ** p - s))
        p_new = abs(math.log(abs(e32 / e21)) + q) / math.log(r21)
        if abs(p_new - p) < 1e-10:
            p = p_new
            break
        p = p_new
    phi_ext = (r21 ** p * f1 - f2) / (r21 ** p - 1.0)
    e_a = abs((f1 - f2) / f1) if f1 else math.inf
    e_ext = abs((phi_ext - f1) / phi_ext) if phi_ext else math.inf
    return GCI(r21, r32, p, phi_ext, e_a, e_ext, SAFETY * e_a / (r21 ** p - 1.0), s > 0)
