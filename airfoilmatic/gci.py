"""Grid Convergence Index (GCI) following Celik et al. (2008).

Celik, I. B., Ghia, U., Roache, P. J., Freitas, C. J., Coleman, H., Raad, P. E.
"Procedure for Estimation and Reporting of Uncertainty Due to Discretization
in CFD Applications", J. Fluids Eng. 130(7), 078001, 2008.

Grid 1 is the finest, grid 3 the coarsest.
"""
import math
from dataclasses import dataclass


@dataclass
class GCIResult:
    h1: float
    h2: float
    h3: float
    r21: float
    r32: float
    p: float
    phi_ext: float
    e_a21: float      # approximate relative error (fine vs medium)
    e_ext21: float    # extrapolated relative error
    gci_fine: float   # GCI_fine^21 (fraction, multiply by 100 for %)
    gci_medium: float  # GCI^32
    asymptotic: float  # GCI32 / (r21^p * GCI21), ~1 => asymptotic range
    oscillatory: bool
    diverging: bool
    converged_iter: int


def representative_size(n_cells, area=1.0, dim=2):
    return (area / n_cells) ** (1.0 / dim)


def compute_gci(n1, n2, n3, phi1, phi2, phi3, dim=2, fs=1.25, max_iter=200, tol=1e-10):
    if not (n1 > n2 > n3 > 0):
        raise ValueError("Cell counts must satisfy N1 (fine) > N2 > N3 (coarse)")
    h1, h2, h3 = (representative_size(n, dim=dim) for n in (n1, n2, n3))
    r21, r32 = h2 / h1, h3 / h2
    e21 = phi2 - phi1
    e32 = phi3 - phi2
    if phi1 == 0:
        raise ValueError("Fine-grid value is zero; relative errors are undefined")
    if e21 == 0 or e32 == 0:
        raise ValueError("Solutions on two grids are identical; p cannot be computed")
    s = math.copysign(1.0, e32 / e21)
    ratio = abs(e32 / e21)

    # Fixed-point iteration for the apparent order p (Celik eq. 5a-5c)
    p = abs(math.log(ratio)) / math.log(r21)
    it = 0
    for it in range(1, max_iter + 1):
        num = r21**p - s
        den = r32**p - s
        if num <= 0 or den <= 0:
            break
        q = math.log(num / den)
        p_new = abs(math.log(ratio) + q) / math.log(r21)
        if abs(p_new - p) < tol:
            p = p_new
            break
        p = p_new

    if not math.isfinite(p) or p < 0.05:
        raise ValueError("Apparent order p is ~0 (the two error differences are almost equal); "
                         "GCI is not meaningful for these values")
    rp21 = r21**p
    rp32 = r32**p
    phi_ext = (rp21 * phi1 - phi2) / (rp21 - 1.0)
    e_a21 = abs((phi1 - phi2) / phi1)
    e_a32 = abs((phi2 - phi3) / phi2)
    e_ext21 = abs((phi_ext - phi1) / phi_ext)
    gci21 = fs * e_a21 / (rp21 - 1.0)
    gci32 = fs * e_a32 / (rp32 - 1.0)
    asym = gci32 / (rp21 * gci21) if gci21 > 0 else float("nan")

    return GCIResult(h1, h2, h3, r21, r32, p, phi_ext, e_a21, e_ext21,
                     gci21, gci32, asym, s < 0, s > 0 and ratio < 1.0, it)
