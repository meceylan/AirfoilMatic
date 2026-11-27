"""Shared, cached sweeps over the 300-section library (each one meshes every section once)."""
import functools

import numpy as np
import pytest


@functools.lru_cache(maxsize=None)
def _sweep(kind, re, refine):
    from airfoilmatic import library as lib
    from airfoilmatic.blockmesh import build_cgrid, quality
    from airfoilmatic.geometry import close_small_te_gap, parse_airfoil_file, split_at
    from airfoilmatic.mesh import plan_mesh
    from airfoilmatic.topology import build_domain
    out = []
    for s in lib.library():
        af = split_at(close_small_te_gap(parse_airfoil_file(s.data)))
        d = build_domain(af, kind, r_inlet=15.0, l_wake=20.0, l_top=15.0, l_bottom=15.0)
        m = build_cgrid(d, af, plan_mesh(d, af, re, refine=refine))
        skew, oq = quality(m)
        c = m.nodes[m.cells].mean(1)
        nose, far = c[:, 0] < 0.1, np.abs(c[:, 1]) > 1.0
        out.append(dict(id=s.id, oq_min=float(oq.min()), nose_skew=float(skew[nose].max()),
                        far_oq=float(oq[far].min())))
    return tuple(out)


@pytest.fixture(scope="session")
def library_sweep():
    """library_sweep(kind, re, refine) -> per-section quality summary, computed once per session."""
    return _sweep
