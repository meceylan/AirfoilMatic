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


# ---------------------------------------------------------------- profile only
UNIT_SCALE = {"m": 1.0, "mm": 1000.0}


def _profile_points(af, unit):
    """Upper and lower surface as printed strings, LE -> TE, in ``unit`` (chord is in metres)."""
    if unit not in UNIT_SCALE:
        raise ValueError(f"unit must be one of {sorted(UNIT_SCALE)}")
    s = UNIT_SCALE[unit]
    precision = max(6, int(np.ceil(-np.log10(max(af.chord * s, 1e-9) * 1e-7))))
    out = []
    for x, y in ((af.xu, af.yu), (af.xl, af.yl)):
        x, y = remove_consecutive_duplicates(np.asarray(x) * s, np.asarray(y) * s, tol=10.0 ** -precision)
        pts = []
        for px, py in zip(x, y):
            p = (f"{px:.{precision}f}", f"{py:.{precision}f}")
            if not pts or (float(p[0]), float(p[1])) != (float(pts[-1][0]), float(pts[-1][1])):
                pts.append(p)
        out.append(pts)
    return out


def profile_dm_txt(af, unit="m"):
    """DesignModeler ``Concept > 3D Curve`` file with the airfoil only: group 1 = upper surface,
    group 2 = lower surface (both LE -> TE) and, for a blunt trailing edge, group 3 = the TE line."""
    upper, lower = _profile_points(af, unit)
    groups = [upper, lower]
    if upper[-1] != lower[-1]:
        groups.append([upper[-1], lower[-1]])
    lines = [f"{g} {i} {px} {py} {0.0}" for g, pts in enumerate(groups, start=1)
             for i, (px, py) in enumerate(pts, start=1)]
    return "\n".join(lines) + "\n"


def profile_solidworks_files(af, unit="mm"):
    """``Curve Through XYZ Points`` files, one curve per file (SolidWorks reads a single curve from a
    file): ``{"upper": text, "lower": text}``. Tab-separated ``X Y Z`` without a header; both surfaces
    start at the leading edge, so the two curves meet there and at a sharp trailing edge."""
    upper, lower = _profile_points(af, unit)
    return {name: "".join(f"{px}\t{py}\t0\n" for px, py in pts)
            for name, pts in (("upper", upper), ("lower", lower))}


def profile_solidworks_zip(af, stem, unit="mm"):
    """The two SolidWorks curve files in one ZIP (bytes)."""
    import io
    import zipfile
    files = profile_solidworks_files(af, unit)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{stem}_upper.txt", files["upper"])
        z.writestr(f"{stem}_lower.txt", files["lower"])
    return buf.getvalue()
