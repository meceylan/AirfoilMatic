"""Node merging in ``blockmesh._assemble`` is vectorised (it was a Python dict loop over every node
and took about half of the mesh build). Nodes, cells, faces and zones must stay exactly as before,
so the .msh file does not change: compared with the dict version kept in tests/data."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from airfoilmatic.blockmesh import build_cgrid, to_fluent_msh
from airfoilmatic.geometry import naca, split_at
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.topology import RECT, build_domain

REF = None


def reference():
    """The previous blockmesh module, imported inside the package so its relative imports work."""
    global REF
    if REF is None:
        import airfoilmatic
        spec = importlib.util.spec_from_file_location("airfoilmatic._blockmesh_reference",
                                                      Path(__file__).resolve().parent / "data" / "blockmesh_reference.py")
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = "airfoilmatic"
        spec.loader.exec_module(mod)
        REF = mod
    return REF


@pytest.mark.parametrize("code, blunt, kind", [("4412", False, "c_grid"), ("0012", True, "c_grid"),
                                               ("4412", False, RECT)])
def test_same_mesh_and_file_as_before(code, blunt, kind):
    af = split_at(naca(code, blunt_te=blunt))
    d = build_domain(af, kind, r_inlet=15.0, l_wake=20.0, l_top=15.0, l_bottom=15.0)
    plan = plan_mesh(d, af, 2.0e6, refine=0.5)
    new, old = build_cgrid(d, af, plan), reference().build_cgrid(d, af, plan)
    assert np.array_equal(new.nodes, old.nodes) and np.array_equal(new.cells, old.cells)
    assert np.array_equal(new.faces, old.faces) and np.array_equal(new.face_zone, old.face_zone)
    assert to_fluent_msh(new) == reference().to_fluent_msh(old)


def test_assemble_is_faster():
    import time
    af = split_at(naca("4412"))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    plan = plan_mesh(d, af, 2.0e6)
    t0 = time.perf_counter(); build_cgrid(d, af, plan); t1 = time.perf_counter()
    reference().build_cgrid(d, af, plan); t2 = time.perf_counter()
    assert (t1 - t0) < 0.7 * (t2 - t1)
