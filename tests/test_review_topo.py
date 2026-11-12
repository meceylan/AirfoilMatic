"""Review of topology.py / export.py: exported curves must meet exactly and carry no repeated points."""
import numpy as np
import pytest

from airfoilmatic import library as lib
from airfoilmatic.export import to_ansys_txt
from airfoilmatic.geometry import close_small_te_gap, naca4, parse_airfoil_file, split_at
from airfoilmatic.topology import C_GRID, RECT, Curve, Domain, build_domain
from test_database_findings import crossings


def exported(domain):
    """Curves as written to the TXT file: {key: [(x_str, y_str), ...]} and a domain of the parsed values."""
    groups = {}
    for line in to_ansys_txt(domain).splitlines():
        g, _, x, y, _ = line.split()
        groups.setdefault(int(g), []).append((x, y))
    keys = [c.key for c in domain.curves]
    rows = {keys[g - 1]: pts for g, pts in groups.items()}
    parsed = Domain(kind=domain.kind, curves=[
        Curve(k, "x", np.array([float(a) for a, _ in p]), np.array([float(b) for _, b in p]))
        for k, p in rows.items()])
    return rows, parsed


def section(title):
    return next(s for s in lib.library() if s.title == title)


def test_wake_axis_starts_on_a_vertex_of_a_slanted_blunt_te_closure():
    """DAE-51, 10 m chord: the TE base is slanted (upper TE 2e-6 c ahead of the lower one). The wake
    axis starts at the middle of the closure line, which had no vertex there; rounded to 6 decimals its
    start moved 0.5 um into the airfoil and the exported wake axis crossed the closure."""
    sp = split_at(close_small_te_gap(section("DAE-51").airfoil(10.0)))
    assert sp.te_upper[0] != sp.te_lower[0]
    d = build_domain(sp, C_GRID, r_inlet=1000, l_wake=1000)
    rows, parsed = exported(d)
    assert crossings(parsed) == 0
    assert rows["wake_axis"][0] in rows["te_closure"][1:-1]


@pytest.mark.parametrize("chord", [0.05, 1.0, 10.0])
@pytest.mark.parametrize("kind", [C_GRID, RECT])
def test_wake_axis_start_is_on_exported_te_closure_for_all_blunt_sections(chord, kind):
    n = 0
    for s in lib.library():
        sp = split_at(close_small_te_gap(s.airfoil(chord)))
        d = build_domain(sp, kind, r_inlet=15, l_wake=20, l_top=15, l_bottom=15)
        if not d.blunt_te:
            continue
        n += 1
        rows, _ = exported(d)
        assert rows["wake_axis"][0] in rows["te_closure"], s.title
    assert n > 0


def test_points_printing_alike_are_not_repeated():
    """Two points 1.1e-7 c apart (more than the tolerance of 1e-7 c) but within one rounding step in
    x and in y were both kept and printed as the same row."""
    a = naca4("0012", n_points=61)
    upper = list(zip(a.xu, a.yu))
    k = next(j for j, (x, _) in enumerate(upper) if x > 0.7)
    y = round(float(np.interp(0.7, a.xu, a.yu)), 7)
    upper[k:k] = [(0.69999996, y - 0.4e-7), (0.70000004, y + 0.4e-7)]
    pts = upper[::-1] + list(zip(a.xl, a.yl))[1:]
    af = parse_airfoil_file("\n".join(f"{x:.10f} {y:.10f}" for x, y in pts).encode())
    rows, _ = exported(build_domain(split_at(close_small_te_gap(af))))
    for key, p in rows.items():
        values = [(float(x), float(y)) for x, y in p]
        assert all(u != v for u, v in zip(values, values[1:])), key
