"""Lift and drag polar from a Fluent report file written during an angle-of-attack sweep.

Fluent 2024 R2 writes a report file (.out) as

    "ladson-b-rfile"
    "Iteration" "alfa etc.."
    ("Iteration" "alfa" "cd" "cl")
    1050 0.0741764932 0.0064669173 0.4480810495
    ...

The third line holds the full column names, in alphabetical order rather than the order the
reports were made in, so columns are always looked up by name. An expression report of an angle
expression in [deg] is written in radians. With the sweep journal every angle is one block of
consecutive iterations; a sweep continued from a saved case writes some iteration numbers again,
and the later lines are the valid ones.
"""
import math
import re
from dataclasses import dataclass

import numpy as np

STEADY, OSCILLATING, SHORT = "steady", "oscillating", "short"

# Defaults of the polar: mean over the last N iterations of each angle; an angle whose Cl moves
# more than CL_TOL (absolute) or whose Cd moves more than CD_TOL (relative) over them is flagged.
LAST_N = 50
CL_TOL = 1e-3
CD_TOL = 0.01

_ANGLE_NAMES = ("alfa", "alpha", "aoa", "angle", "incidence")
_ANGLE_SAME = 1e-9     # radians or degrees: the journal writes the same expression value in a block


@dataclass
class Report:
    name: str
    columns: list
    rows: np.ndarray    # one row per iteration, columns as in ``columns`` (first: iteration)


@dataclass
class PolarRow:
    aoa: float          # degrees
    iterations: int     # rows in the angle's block
    first: int          # first and last iteration number of the block
    last: int
    cl: float           # mean of the last N iterations
    cl_range: float     # max - min of Cl over the same iterations
    cd: float
    cd_range: float
    ld: float           # cl / cd
    status: str         # STEADY, OSCILLATING or SHORT (fewer than N iterations)
    repeats: int = 1    # blocks seen for this angle (the latest one is used)


def _quoted(line):
    return re.findall(r'"([^"]*)"', line)


def is_transient(report):
    """True for a report file of a transient run: Fluent writes "Time Step" instead of "Iteration"
    as the first column, so each row is a time step."""
    return str(report.columns[0]).strip().lower() == "time step"


def read_report(data):
    """Columns and rows of a Fluent report file (bytes or str)."""
    text = data.decode("utf-8", errors="replace") if isinstance(data, (bytes, bytearray)) else str(data)
    lines = [l.strip() for l in text.splitlines()]
    header_i = next((i for i, l in enumerate(lines) if l.startswith("(") and len(_quoted(l)) >= 2), None)
    if header_i is None:
        raise ValueError("Not a Fluent report file: no header line with the column names")
    columns = _quoted(lines[header_i])
    name = next((q[0] for q in (_quoted(l) for l in lines[:header_i]) if len(q) == 1), "")
    rows = []
    for line in lines[header_i + 1:]:
        parts = line.split()
        if len(parts) != len(columns):
            continue
        try:
            vals = [float(p) for p in parts]
        except ValueError:
            continue
        if all(math.isfinite(v) for v in vals):      # a "nan" row would make its angle's mean nan
            rows.append(vals)
    if not rows:
        raise ValueError("The report file has no data rows")
    return Report(name=name, columns=columns, rows=np.array(rows, dtype=float))


def merge_reports(reports):
    """One report from several files of the same report definition.

    When a sweep is continued from a saved case, Fluent 2024 R2 refuses to append to a report file
    that already holds later iterations ("Report data in file must be lower than current
    iteration ... Do you want to create new file?") and with Yes writes the rest to
    ``<name>_<iteration>.out`` (tried 2026-11-25). From the first iteration of the file that starts
    later (the continued run) on, the earlier file's rows are dropped, whatever the upload order.
    Columns are matched by name."""
    reports = list(reports)
    if len(reports) == 1:
        return reports[0]
    columns = reports[0].columns
    if any(sorted(r.columns) != sorted(columns) for r in reports):
        joined = _join_definitions(reports)
        if joined is None:
            raise ValueError("The report files do not have the same columns")
        return joined
    parts = [rep.rows[:, [rep.columns.index(c) for c in columns]]
             for rep in sorted(reports, key=lambda r: r.rows[0, 0])]
    return Report(name=reports[0].name, columns=list(columns), rows=_latest_rows(np.vstack(parts)))


def _join_definitions(reports):
    """One report from files that each hold other report definitions (Fluent can write one file
    per definition: cl-rfile.out, cd-rfile.out, ...), joined on the iteration column. None when
    the files share a column other than the iteration (then they are not separate definitions)."""
    seen = set()
    for rep in reports:
        own = set(rep.columns[1:])
        if own & seen:
            return None
        seen |= own
    tables = []
    for rep in reports:
        rows = _latest_rows(rep.rows)
        tables.append({int(round(r[0])): r[1:] for r in rows})
    common = sorted(set.intersection(*(set(t) for t in tables)))
    if not common:
        raise ValueError("The report files have no iteration in common")
    columns = [reports[0].columns[0]] + [c for rep in reports for c in rep.columns[1:]]
    rows = np.array([[k] + [v for t in tables for v in t[k]] for k in common], dtype=float)
    return Report(name=reports[0].name, columns=columns, rows=rows)


def _latest_rows(rows):
    """Rows in the order written, keeping the valid run only: where the iteration number goes back
    (a run continued from a saved case), every earlier row from that iteration on belongs to the
    abandoned run and is dropped, also those beyond the end of the continued run (an angle that
    diverged for 2000 iterations and then converged in 300 kept its bad block before)."""
    by_iter = {}
    last = None
    for row in rows:
        k = int(round(row[0]))
        if last is not None and k <= last:
            for old in [i for i in by_iter if i >= k]:
                del by_iter[old]
        by_iter[k] = row
        last = k
    return np.array([by_iter[k] for k in sorted(by_iter)])


_FORCE_WORDS = {"cl", "cd", "cm", "lift", "drag", "moment", "conv", "clconv", "cdconv"}


def guess_columns(columns):
    """Most likely angle, Cl and Cd column names (None when not found). A column whose name also
    has a force word ("cl-alpha-report") is not taken for the angle, and convergence helpers
    (clconv, cdconv) are never taken for Cl or Cd."""
    low = {c: c.lower() for c in columns[1:]}
    words = {c: set(re.split(r"[^a-z0-9]+", l)) - {""} for c, l in low.items()}

    def first(match):
        return next((c for c, l in low.items() if match(c, l)), None)

    angle = first(lambda c, l: bool(words[c] & set(_ANGLE_NAMES)) and not words[c] & _FORCE_WORDS) \
        or first(lambda c, l: any(n in l for n in _ANGLE_NAMES) and not words[c] & _FORCE_WORDS)
    cl = first(lambda c, l: l == "cl") or first(lambda c, l: l.startswith("cl") and "conv" not in l) \
        or first(lambda c, l: "lift" in l)
    cd = first(lambda c, l: l == "cd") or first(lambda c, l: l.startswith("cd") and "conv" not in l) \
        or first(lambda c, l: "drag" in l)
    return dict(angle=angle, cl=cl, cd=cd)


def _column(report, name):
    if name not in report.columns:
        raise ValueError("Column not in the report file")
    return report.columns.index(name)


def polar(report, angle_col, cl_col, cd_col, angle_unit="rad", last_n=LAST_N, cl_tol=CL_TOL, cd_tol=CD_TOL):
    """One PolarRow per angle, smallest angle first."""
    ia, il, idd = (_column(report, c) for c in (angle_col, cl_col, cd_col))
    # A sweep continued from a saved case writes iteration numbers again: the later run wins.
    rows = _latest_rows(report.rows)
    angles = rows[:, ia]
    breaks = np.flatnonzero(np.abs(np.diff(angles)) > _ANGLE_SAME) + 1
    latest, seen = {}, {}
    for block in np.split(np.arange(len(rows)), breaks):
        key = round(float(angles[block[0]]), 9)
        latest[key] = block
        seen[key] = seen.get(key, 0) + 1
    out = []
    for key, block in latest.items():
        tail = block[-last_n:]
        cl, cd = rows[tail, il], rows[tail, idd]
        cl_mean, cd_mean = float(cl.mean()), float(cd.mean())
        cl_range, cd_range = float(cl.max() - cl.min()), float(cd.max() - cd.min())
        if len(block) < last_n:
            status = SHORT
        elif cl_range > cl_tol or (cd_mean != 0 and cd_range / abs(cd_mean) > cd_tol):
            status = OSCILLATING
        else:
            status = STEADY
        aoa = math.degrees(key) if angle_unit == "rad" else key
        out.append(PolarRow(aoa=aoa, iterations=len(block), first=int(rows[block[0], 0]),
                            last=int(rows[block[-1], 0]), cl=cl_mean, cl_range=cl_range, cd=cd_mean,
                            cd_range=cd_range, ld=cl_mean / cd_mean if cd_mean else math.nan,
                            status=status, repeats=seen[key]))
    return sorted(out, key=lambda r: r.aoa)


def polar_csv(rows):
    """CSV text of the polar, one line per angle."""
    head = "alpha_deg,cl,cd,cl_cd,cl_range,cd_range,iterations,first_iteration,last_iteration,status"
    lines = [head] + [f"{r.aoa:.6g},{r.cl:.8g},{r.cd:.8g},{r.ld:.6g},{r.cl_range:.3g},{r.cd_range:.3g},"
                      f"{r.iterations},{r.first},{r.last},{r.status}" for r in rows]
    return "\n".join(lines) + "\n"
