"""The app's own mapped C-grid mesh and its Fluent .msh file."""
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.blockmesh import (INLET, OUTLET, WALL, build_cgrid, quality, read_fluent_msh,
                                    to_fluent_msh)
from airfoilmatic.geometry import naca, split_at
from airfoilmatic.i18n import ERRORS_TR, tr
from airfoilmatic.mesh import plan_mesh, reynolds
from airfoilmatic.topology import RECT, build_domain

APP = str(Path(__file__).resolve().parents[1] / "app.py")
RE = reynolds(51.04, 1.225, 3.126e-5, 1.0)       # the Ladson / NACA 4412 runs


def make(code="4412", blunt=False):
    af = split_at(naca(code, blunt_te=blunt))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    plan = plan_mesh(d, af, RE)
    return af, d, plan, build_cgrid(d, af, plan)


CASES = [("4412", False), ("0012", False), ("0012", True)]


@pytest.mark.parametrize("code, blunt", CASES)
def test_cell_count_is_the_planned_count(code, blunt):
    _, d, plan, m = make(code, blunt)
    assert d.blunt_te == blunt
    assert m.n_cells == plan.cells


@pytest.mark.parametrize("code, blunt", CASES)
def test_cells_are_counter_clockwise_and_valid(code, blunt):
    m = make(code, blunt)[3]
    xy = m.nodes[m.cells]
    area = 0.5 * np.sum(xy[:, :, 0] * np.roll(xy[:, :, 1], -1, 1) - np.roll(xy[:, :, 0], -1, 1) * xy[:, :, 1], 1)
    assert area.min() > 0


@pytest.mark.parametrize("code, blunt", CASES)
def test_topology_one_hole_and_boundary_face_counts(code, blunt):
    _, _, plan, m = make(code, blunt)
    assert len(m.nodes) - len(m.faces) + m.n_cells == 0          # Euler: a domain with one hole
    n = np.bincount(m.face_zone, minlength=7)
    assert n[WALL] == 2 * (plan.n_front + plan.n_rear) + plan.n_closure
    assert n[INLET] == 2 * (plan.n_front + plan.n_rear + plan.n_wake)
    assert n[OUTLET] == 2 * (plan.n_normal + plan.n_closure // 2)
    boundary = m.faces[:, 3] < 0
    assert set(m.face_zone[boundary]) == {WALL, INLET, OUTLET}


@pytest.mark.parametrize("code, blunt", CASES)
def test_c0_is_left_of_n0_n1_and_c1_right(code, blunt):
    """Fluent rule (also seen in an Ansys Meshing .msh): c0 left, c1 right, c1 = 0 on a boundary."""
    m = make(code, blunt)[3]
    centre = m.nodes[m.cells].mean(1)
    p0, p1 = m.nodes[m.faces[:, 0]], m.nodes[m.faces[:, 1]]
    t = p1 - p0
    r0 =centre[m.faces[:, 2]] - p0
    assert np.all(t[:, 0] * r0[:, 1] - t[:, 1] * r0[:, 0] > 0)
    inner = m.faces[:, 3] >= 0
    r1 = centre[m.faces[inner, 3]] - p0[inner]
    assert np.all(t[inner, 0] * r1[:, 1] - t[inner, 1] * r1[:, 0] < 0)


def _first_cell(plan, m):
    wall = m.faces[m.face_zone == WALL]
    cells = wall[:, 2]
    p0, p1 = m.nodes[wall[:, 0]], m.nodes[wall[:, 1]]
    t = p1 - p0
    nrm = np.column_stack([-t[:, 1], t[:, 0]]) / np.linalg.norm(t, axis=1)[:, None]   # into the fluid (left)
    far = []
    for k, c in enumerate(cells):
        other = [n for n in m.cells[c] if n not in wall[k, :2]]
        far.append(min(np.dot(m.nodes[o] - p0[k], nrm[k]) for o in other))
    return np.array(far)


@pytest.mark.parametrize("code", ["4412", "0012"])
def test_wall_cells_are_about_the_planned_first_height(code):
    _, _, plan, m = make(code)
    h = _first_cell(plan, m)
    assert np.median(h) == pytest.approx(plan.dy1, rel=0.15)
    assert h.min() > 0.3 * plan.dy1


@pytest.mark.parametrize("code", ["4412", "0012"])
def test_quality_close_to_the_ansys_mapped_mesh(code):
    """Ansys Meshing 2024 R2, NACA 4412, same table: max skewness 0.445, min orthogonal quality 0.577."""
    skew, oq = quality(make(code)[3])
    assert skew.max() < 0.6 and oq.min() > 0.5
    assert skew.mean() < 0.1 and oq.mean() > 0.95


def test_fluent_file_reads_back_with_zones_and_codes():
    m = make()[3]
    text = to_fluent_msh(m)
    assert text.startswith("(0 ") and "(2 2)" in text
    assert f"(12 (0 1 {m.n_cells:x} 0))" in text and f"(10 (0 1 {len(m.nodes):x} 0 2))" in text
    xy, faces, names = read_fluent_msh(text)
    assert np.allclose(xy, m.nodes, rtol=0, atol=1e-12)
    assert {bc for bc, _ in faces.values()} == {2, 3, 10, 5}
    assert {n for _, n in names.values()} >= {"inlet", "outlet", "wall"}
    assert names[5] == ("velocity-inlet", "inlet") and names[6] == ("pressure-outlet", "outlet")
    total = sum(len(rows) for _, rows in faces.values())
    assert total == len(m.faces)
    for bc, rows in faces.values():
        assert rows[:, :3].min() >= 1
        if bc != 2:
            assert np.all(rows[:, 3] == 0)
        else:
            assert rows[:, 3].min() >= 1


def test_rectangle_domain_is_refused_with_turkish_text():
    af = split_at(naca("0012"))
    d = build_domain(af, RECT, r_inlet=15.0, l_wake=20.0, l_top=15.0, l_bottom=15.0)
    with pytest.raises(ValueError, match="only available for the C-grid"):
        build_cgrid(d, af, plan_mesh(d, af, RE))
    assert "The mesh file is only available for the C-grid domain" in ERRORS_TR


# ---------------------------------------------------------------- app
def widget(at, kind, key):
    return [w for w in getattr(at, kind) if w.key == key][0]


def mapped_page():
    at = AppTest.from_file(APP, default_timeout=120).run()
    widget(at, "text_input", "af_query").set_value("4412")
    at = at.run()
    mode = widget(at, "radio", "mesh_mode")
    mode.set_value(mode.options[1])
    return at.run()


def has_msh_button(at):
    return any(el.proto.id.endswith("msh_download") for el in at.get("download_button"))


def test_mapped_mode_offers_the_fluent_mesh_file():
    at = mapped_page()
    assert not at.exception and not at.error
    assert has_msh_button(at)
    assert any(tr("msh_note", "tr")[:40] in c.value for c in at.caption)


def test_inflation_mode_has_no_mesh_file():
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not has_msh_button(at)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_mesh_file_texts_exist(lang):
    for key in ("msh_title", "msh_download", "msh_note", "msh_cells", "msh_skew", "msh_oq"):
        assert tr(key, lang) != key


@pytest.mark.parametrize("name", ["README.md", "README.en.md", "CHANGELOG.md"])
def test_docs_describe_the_mesh_file(name):
    text = (Path(APP).parent / name).read_text(encoding="utf-8")
    assert "Fluent mesh" in text and ".msh" in text and "transfinite" in text
