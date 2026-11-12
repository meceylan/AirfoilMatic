"""Export to the Ansys DesignModeler ``Concept > 3D Curve`` text format.

Each line is ``group point x y z``; every curve gets its own group number so
DesignModeler creates one edge per curve.
"""
import re
import unicodedata

import numpy as np

_TURKISH = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def safe_file_stem(name, fallback="custom"):
    """File name without extension, reduced to ASCII letters, digits, '_', '-' and '.'
    ("Ölçü kanadı (v2).dat" -> "Olcu_kanadi_v2"), so downloads get a usable name."""
    stem = name.rsplit(".", 1)[0] if "." in name else name
    stem = unicodedata.normalize("NFKD", stem.translate(_TURKISH)).encode("ascii", "ignore").decode()
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("_.-")
    return stem or fallback


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
    fmt = f"{{:d}} {{:d}} {{}} {{}} {{:.{precision}f}}"
    for g, curve in enumerate(domain.curves, start=1):
        x, y = remove_consecutive_duplicates(curve.x, curve.y, tol=10.0 ** -precision)
        pts = []
        for px, py in zip(x, y):
            p = (f"{px:.{precision}f}", f"{py:.{precision}f}")
            # points closer than the last digit can still print alike: write them once
            if not pts or (float(p[0]), float(p[1])) != (float(pts[-1][0]), float(pts[-1][1])):
                pts.append(p)
        for i, (px, py) in enumerate(pts, start=1):
            lines.append(fmt.format(g, i, px, py, 0.0))
    return "\n".join(lines) + "\n"
