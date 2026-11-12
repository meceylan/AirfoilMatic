"""Build the airfoil library shipped with the app from the UIUC coordinate database.

    python tools/build_airfoil_library.py path/to/coord_seligFmt

Download the database from https://m-selig.ae.illinois.edu/ads/coord_database.html
(coord_seligFmt.zip). The script reads every file with the app's own reader, drops files
that would make a poor CFD outline, picks about 200 sections spread over the families
below and writes them to airfoilmatic/data/uiuc_library.json.gz.

NACA 4- and 5-digit sections are left out on purpose: the app draws those from the NACA
equations with 201 points and a sharp trailing edge, while the database copies have 18
points and a blunt trailing edge (and NACA 0012 is not in the database at all).
"""
import gzip
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airfoilmatic.geometry import (AirfoilError, chord_line_angle, close_small_te_gap,  # noqa: E402
                                   looks_reversed, parse_airfoil_file, split_at)
from airfoilmatic.geometry import naca  # noqa: E402
from airfoilmatic.topology import C_GRID, build_domain  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "airfoilmatic" / "data" / "uiuc_library.json.gz"
TARGET = 200

# Quality limits for a file to be considered at all.
MIN_POINTS = 25      # per surface; DesignModeler's curve through fewer points is visibly coarse
MAX_DX = 0.07        # largest chordwise gap between two points, / chord
MAX_KINK = 30.0      # largest turn between two segments behind the first 1% of the chord, degrees
MAX_TILT = 1.0       # chord line angle in the file, degrees
MIN_THICKNESS = 0.03

# family key -> (display name, file-name pattern, how many to take)
FAMILIES = [
    ("naca", "NACA", r"^(naca|n)(1[0-9]|6[0-9]|7[0-9])", 24),
    ("nasa", "NASA", r"^(sc2\d{4}$|nlf|ls|ms|ga)", 22),
    ("eppler", "Eppler", r"^e\d", 34),
    ("selig", "Selig", r"^(s\d|sd\d|sg\d|sa\d)", 30),
    ("wortmann", "Wortmann FX", r"^fx", 20),
    ("hepperle", "Hepperle MH", r"^mh", 15),
    ("drela", "Drela AG / HT", r"^(ag|ht)\d", 12),
    ("althaus", "Althaus AH", r"^ah", 7),
    ("quabeck", "Quabeck HQ", r"^hq", 7),
    ("girsberger", "Girsberger RG", r"^rg", 4),
    ("rae", "RAE", r"^rae", 6),
    ("du", "Delft DU", r"^du", 3),
    ("classic", "Classic", r"^(clarky|clark|goe|usa|raf|dae|davis)", 16),
]

# Sections people look for by name; taken first when they pass the quality limits.
WANTED = {
    "naca": ["n63215", "n64215", "naca642415", "naca64a010", "naca64a210", "naca65410", "naca652415",
             "naca63a210", "naca66210", "naca16012"],
    "nasa": ["sc20714", "sc20410", "sc20412", "sc20012", "sc20610", "nlf0215f", "nlf416", "nlf0115", "ls417",
             "ls413", "ls421", "ms0313"],
    "eppler": ["e387", "e423", "e374", "e205", "e214", "e216", "e231", "e335", "e392", "e395", "e420", "e422",
               "e61", "e63", "e174", "e169", "e471", "e472", "e473", "e474", "e591", "e325", "e176", "e186"],
    "selig": ["s1223", "s1210", "sd7003", "sd7037", "sd7032", "sd7062", "sd7080", "sd8020", "s3021", "s8036",
              "s4083", "s2027", "s2048", "s4061", "s9000", "s1091", "s3010", "s7012", "s8037"],
    "wortmann": ["fx63137", "fx74modsm", "fx60126", "fx61147", "fx66s196", "fx38153", "fx60100", "fx63100"],
    "hepperle": ["mh32", "mh60", "mh45", "mh114", "mh43", "mh49", "mh30", "mh81", "mh104"],
    "drela": ["ag25", "ag35", "ag24", "ag26", "ag16", "ag03", "ht14", "ht13", "ht12"],
    "rae": ["rae2822", "rae5212", "rae5214", "rae101"],
    "du": ["du84132v", "du-80-141", "du-80-176-v1"],
    "classic": ["clarky", "clarkysm", "dae11", "dae21", "dae31", "davis"],
}


def turn(x, y):
    v = np.diff(np.column_stack([x, y]), axis=0)
    a = np.arctan2(v[:, 1], v[:, 0])
    da = np.degrees(np.abs(np.angle(np.exp(1j * np.diff(a)))))
    rear = x[1:-1] > 0.01
    return float(da[rear].max()) if rear.any() else 0.0


def measure(data):
    """Shape numbers of a file, or None when it is not good enough for the library."""
    try:
        af = parse_airfoil_file(data, 1.0)
    except AirfoilError:
        return None
    if looks_reversed(af) or af.overlap > 1e-5 or abs(chord_line_angle(af)) > MAX_TILT:
        return None
    if min(len(af.xu), len(af.xl)) < MIN_POINTS:
        return None
    if max(np.diff(af.xu).max(), np.diff(af.xl).max()) > MAX_DX:
        return None
    if max(turn(af.xu, af.yu), turn(af.xl, af.yl)) > MAX_KINK:
        return None
    xs = np.linspace(0.0, 1.0, 1001)
    yu, yl = np.interp(xs, af.xu, af.yu), np.interp(xs, af.xl, af.yl)
    t, c = yu - yl, 0.5 * (yu + yl)
    if t.max() < MIN_THICKNESS:
        return None
    build_domain(split_at(close_small_te_gap(af)), C_GRID, r_inlet=10, l_wake=20)   # must not raise
    i, j = int(t.argmax()), int(np.abs(c).argmax())
    return dict(t=round(float(t[i]), 4), xt=round(float(xs[i]), 3), camber=round(float(c[j]), 4),
                xc=round(float(xs[j]), 3), te=round(float(af.te_gap), 5),
                points=int(len(af.xu) + len(af.xl) - 1))


def spread(candidates, k):
    """``k`` names chosen so that thickness, camber and their positions are spread out
    (farthest-point sampling, started from the most typical section)."""
    names = sorted(candidates)
    if k <= 0:
        return []
    if len(names) <= k:
        return names
    p = np.array([[candidates[n]["t"] / 0.05, candidates[n]["camber"] / 0.02,
                   candidates[n]["xt"] / 0.1, candidates[n]["xc"] / 0.2] for n in names])
    chosen = [int(np.argmin(np.linalg.norm(p - np.median(p, axis=0), axis=1)))]
    d = np.linalg.norm(p - p[chosen[0]], axis=1)
    while len(chosen) < k:
        nxt = int(np.argmax(d))
        chosen.append(nxt)
        d = np.minimum(d, np.linalg.norm(p - p[nxt], axis=1))
    return [names[i] for i in chosen]


def drawn_by_the_app(stem):
    """True for a NACA 4- or 5-digit section, which the app draws from the equations."""
    m = re.fullmatch(r"(?:naca|n)(\d{4,5})", stem, re.I)
    if not m:
        return False
    try:
        naca(m.group(1))
    except (AirfoilError, ValueError):
        return False
    return True


def title_of(text, stem):
    first = text.splitlines()[0].strip() if text.strip() else stem
    first = re.split(r"\||\. ", first)[0].strip()
    first = re.sub(r"\s+AIRFOIL\s*$", "", first, flags=re.I)
    first = re.sub(r"\s{2,}", " ", first)
    if len(first) > 48:
        first = first[:47].rstrip() + "…"
    return first or stem.upper()


def main(folder):
    files = sorted(Path(folder).glob("*.dat"))
    if not files:
        sys.exit(f"No .dat files in {folder}")
    shapes, texts = {}, {}
    for f in files:
        data = f.read_bytes()
        if drawn_by_the_app(f.stem):
            continue
        m = measure(data)
        if m is not None:
            shapes[f.stem] = m
            texts[f.stem] = data.decode("latin-1")
    print(f"{len(files)} files, {len(shapes)} good enough")

    library, taken = [], set()
    for key, label, pattern, quota in FAMILIES:
        pool = {n: s for n, s in shapes.items() if re.match(pattern, n, re.I) and n not in taken}
        picked = [n for n in WANTED.get(key, []) if n in pool][:quota]
        rest = {n: s for n, s in pool.items() if n not in picked}
        picked += spread(rest, quota - len(picked))
        missing = [n for n in WANTED.get(key, []) if n not in pool]
        print(f"{label:16s} {len(pool):4d} usable, {len(picked):3d} taken"
              + (f"  (wanted but not usable: {', '.join(missing)})" if missing else ""))
        for n in picked:
            taken.add(n)
            library.append(dict(id=n, title=title_of(texts[n], n), family=key, family_name=label,
                                **shapes[n], data=texts[n]))
    # Top up to TARGET from the two largest low-Reynolds families.
    for key, label, pattern, _ in FAMILIES:
        if len(library) >= TARGET or key not in ("eppler", "selig"):
            continue
        pool = {n: s for n, s in shapes.items() if re.match(pattern, n, re.I) and n not in taken}
        for n in spread(pool, (TARGET - len(library) + 1) // 2 if key == "eppler" else TARGET - len(library)):
            taken.add(n)
            library.append(dict(id=n, title=title_of(texts[n], n), family=key, family_name=label,
                                **shapes[n], data=texts[n]))
    library.sort(key=lambda e: (e["family"], e["id"]))
    print(f"{len(library)} sections in the library")
    OUT.parent.mkdir(exist_ok=True)
    payload = dict(source="UIUC Airfoil Coordinates Database, https://m-selig.ae.illinois.edu/ads/coord_database.html",
                   airfoils=library)
    with gzip.open(OUT, "wt", encoding="utf-8", compresslevel=9) as fh:
        json.dump(payload, fh, separators=(",", ":"))
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
