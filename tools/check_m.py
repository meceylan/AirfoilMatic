# Development helper: solves for the NACA 5-digit mean-line parameter m
# for each camber position P (values used in airfoilmatic/geometry.py NACA5_TABLE).

import numpy as np

def get_m(p):
    roots = np.roots([1, -3, 6*p, -3*p**2])
    real_roots = roots[np.isreal(roots)].real
    for r in real_roots:
        if 0 < r < 1:
            return r
    return None

for P in [10, 20, 30, 40, 50]:
    p = P / 200.0
    m = get_m(p)
    print(f"P={P}, p={p}, m={m:.4f}")
