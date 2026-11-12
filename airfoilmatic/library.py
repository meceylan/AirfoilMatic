"""Airfoil sections the app can look up by name.

NACA 4- and 5-digit sections are drawn from the NACA equations (``geometry.naca``). Every
other section comes from a selection of 200 files of the UIUC Airfoil Coordinates Database
(``data/uiuc_library.json.gz``, built by ``tools/build_airfoil_library.py``); the app reads
those files with the same reader as an uploaded file. A name that is in neither is not
found: the app does not invent a section.
"""
import gzip
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from .geometry import AirfoilError, naca, parse_airfoil_file

DATA = Path(__file__).resolve().parent / "data" / "uiuc_library.json.gz"
UIUC_URL = "https://m-selig.ae.illinois.edu/ads/coord_database.html"
NACA_FORMULA = "naca"
UIUC = "uiuc"
MAX_RESULTS = 40


@dataclass(frozen=True)
class Section:
    id: str              # UIUC file name without .dat, or "naca4412" for a NACA section
    title: str
    source: str          # NACA_FORMULA or UIUC
    family: str
    family_name: str
    t: float = 0.0       # max thickness / c
    xt: float = 0.0      # its position / c
    camber: float = 0.0  # max camber / c (signed)
    xc: float = 0.0
    te: float = 0.0      # trailing-edge gap / c
    points: int = 0
    data: str = ""       # coordinate file text (UIUC only)

    @property
    def code(self):
        """NACA digits of a NACA section."""
        return self.id[4:] if self.source == NACA_FORMULA else ""

    def airfoil(self, chord=1.0):
        if self.source == NACA_FORMULA:
            return naca(self.code, chord)
        return parse_airfoil_file(self.data.encode("latin-1"), chord, name=self.title)


@lru_cache(maxsize=1)
def library():
    with gzip.open(DATA, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return tuple(Section(source=UIUC, **e) for e in payload["airfoils"])


def families():
    """(key, display name) of the families in the library, in display order."""
    seen = {}
    for s in library():
        seen.setdefault(s.family, s.family_name)
    return sorted(seen.items(), key=lambda kv: kv[1].lower())


def _norm(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _keys(s):
    """Spellings a section is found by: file name, title, and both without a NACA prefix."""
    keys = {_norm(s.id), _norm(s.title)}
    for k in list(keys):
        m = re.fullmatch(r"(?:naca|n)(\d.*)", k)
        if m:
            keys.add(m.group(1))
    return keys


@lru_cache(maxsize=1)
def _index():
    return [(s, _keys(s)) for s in library()]


def naca_section(query):
    """The NACA 4/5-digit section a query names ("4412", "NACA 23012", "naca-0012"), or None."""
    q = _norm(query)
    m = re.fullmatch(r"(?:naca)?(\d{4,5})", q)
    if not m:
        return None
    code = m.group(1)
    try:
        af = naca(code)
    except (AirfoilError, ValueError):
        return None
    xs = np.linspace(0.0, 1.0, 201)
    t = np.interp(xs, af.xu, af.yu) - np.interp(xs, af.xl, af.yl)
    return Section(id=f"naca{code}", title=f"NACA {code}", source=NACA_FORMULA, family="naca_formula",
                   family_name="NACA", t=round(float(t.max()), 4), xt=round(float(xs[t.argmax()]), 3))


def search(query):
    """Sections matching ``query``, best first. A NACA 4/5-digit code comes first, drawn
    from the equations; then library sections whose name equals, starts with or contains
    the query (spaces, dashes and brackets ignored, so "63-215", "n63215" and
    "NACA 63-215" are the same)."""
    q = _norm(query)
    if not q:
        return []
    found = []
    first = naca_section(query)
    if first is not None:
        found.append((-1, 0, first))
    q_bare = re.sub(r"^(?:naca|n)(?=\d)", "", q)
    for s, keys in _index():
        best = None
        for k in keys:
            for want in {q, q_bare}:
                if k == want:
                    rank = 0
                elif k.startswith(want):
                    rank = 1
                elif want in k:
                    rank = 2
                else:
                    continue
                best = rank if best is None else min(best, rank)
        if _norm(s.id) == q:
            best = -0.5   # the file name itself (what the dice and the history put in the box)
        if best is not None:
            found.append((best, len(s.id), s))
    found.sort(key=lambda r: (r[0], r[1], r[2].id))
    return [s for _, _, s in found[:MAX_RESULTS]]


def by_id(section_id):
    if section_id.startswith("naca") and naca_section(section_id) is not None and section_id[4:].isdigit():
        return naca_section(section_id)
    for s in library():
        if s.id == section_id:
            return s
    return None


CAMBER_ANY, CAMBER_SYMMETRIC, CAMBER_CAMBERED = "any", "symmetric", "cambered"
SYMMETRIC_TOL = 0.002   # |max camber| below this (/ c) counts as symmetric


def pool(t_range=(0.0, 1.0), camber=CAMBER_ANY, family_keys=None):
    """Library sections that pass the random-pick filters."""
    lo, hi = t_range
    out = []
    for s in library():
        if not lo <= s.t <= hi:
            continue
        if camber == CAMBER_SYMMETRIC and abs(s.camber) >= SYMMETRIC_TOL:
            continue
        if camber == CAMBER_CAMBERED and abs(s.camber) < SYMMETRIC_TOL:
            continue
        if family_keys and s.family not in family_keys:
            continue
        out.append(s)
    return out


def random_section(rng, avoid=None, **filters):
    """A random library section that passes the filters (not ``avoid`` when there is a choice), or None."""
    candidates = pool(**filters)
    if len(candidates) > 1 and avoid is not None:
        candidates = [s for s in candidates if s.id != avoid] or candidates
    if not candidates:
        return None
    return candidates[int(rng.integers(len(candidates)))]
