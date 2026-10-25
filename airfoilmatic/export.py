"""Export to the Ansys DesignModeler ``Concept > 3D Curve`` text format.

Each line is ``group point x y z``; every curve gets its own group number so
DesignModeler creates one edge per curve.
"""
import numpy as np


def remove_consecutive_duplicates(x, y, tol=1e-9):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) == 0:
        return x, y
    keep = [0]
    for i in range(1, len(x) - 1):
        if np.hypot(x[i] - x[keep[-1]], y[i] - y[keep[-1]]) > tol:
            keep.append(i)
    if len(x) > 1:
        # always keep the true end point; drop the previous one if it is a near-duplicate
        if len(keep) > 1 and np.hypot(x[-1] - x[keep[-1]], y[-1] - y[keep[-1]]) <= tol:
            keep.pop()
        keep.append(len(x) - 1)
    return x[keep], y[keep]


def to_ansys_txt(domain, precision=None):
    """``precision`` defaults to enough decimals for ~1e-7 of the chord."""
    if precision is None:
        c = max(getattr(domain, "chord", 1.0), 1e-9)
        precision = max(6, int(np.ceil(-np.log10(c * 1e-7))))
    lines = []
    fmt = f"{{:d}} {{:d}} {{:.{precision}f}} {{:.{precision}f}} {{:.{precision}f}}"
    for g, curve in enumerate(domain.curves, start=1):
        x, y = remove_consecutive_duplicates(curve.x, curve.y, tol=10.0 ** -precision)
        for i, (px, py) in enumerate(zip(x, y), start=1):
            lines.append(fmt.format(g, i, px, py, 0.0))
    return "\n".join(lines) + "\n"
