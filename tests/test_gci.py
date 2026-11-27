"""Mesh independence: the grid family (coarse / medium / fine .msh) and the grid convergence
index (Celik et al. 2008, J. Fluids Eng. 130, 078001)."""
import io
import zipfile
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.blockmesh import build_cgrid, mesh_family
from airfoilmatic.gci import gci
from airfoilmatic.geometry import naca, split_at
from airfoilmatic.i18n import ERRORS_TR, tr
from airfoilmatic.mesh import plan_mesh, reynolds
from airfoilmatic.topology import build_domain

APP = str(Path(__file__).resolve().parents[1] / "app.py")
RE = reynolds(51.04, 1.225, 3.126e-5, 1.0)


# ---------------------------------------------------------------- GCI
def test_celik_worked_example():
    """Celik et al. 2008, table 1, first column (2D, N = 18000 / 8000 / 4500)."""
    g = gci([18000, 8000, 4500], [6.063, 5.972, 5.863])
    assert g.r21 == pytest.approx(1.5, abs=1e-3)
    assert g.r32 == pytest.approx(1.333, abs=1e-3)
    assert g.p == pytest.approx(1.53, abs=0.01)
    assert g.phi_ext == pytest.approx(6.1685, abs=1e-3)
    assert 100 * g.e_a == pytest.approx(1.5, abs=0.05)
    assert 100 * g.e_ext == pytest.approx(1.7, abs=0.05)
    assert 100 * g.gci_fine == pytest.approx(2.2, abs=0.05)
    assert g.monotonic


def test_order_of_inputs_does_not_matter():
    a = gci([18000, 8000, 4500], [6.063, 5.972, 5.863])
    b = gci([4500, 18000, 8000], [5.863, 6.063, 5.972])
    assert b.p == pytest.approx(a.p) and b.phi_ext == pytest.approx(a.phi_ext)


def test_oscillating_values_are_flagged():
    g = gci([18000, 8000, 4500], [1.00, 1.02, 0.99])
    assert not g.monotonic


def test_equal_fine_and_medium_value_means_mesh_independent():
    g = gci([18000, 8000, 4500], [1.0, 1.0, 1.01])
    assert g.gci_fine == 0.0 and g.phi_ext == 1.0


@pytest.mark.parametrize("cells, msg", [
    ([18000, 18000, 4500], "The three meshes need different cell counts"),
    ([18000, 0, 4500], "Cell counts must be positive"),
])
def test_bad_input(cells, msg):
    with pytest.raises(ValueError, match=msg):
        gci(cells, [1.0, 1.1, 1.2])
    assert msg in ERRORS_TR


# ---------------------------------------------------------------- grid family
def family(code="4412", blunt=False):
    af = split_at(naca(code, blunt_te=blunt))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    return d, af, mesh_family(d, af, RE)


@pytest.mark.parametrize("blunt", [False, True])
def test_family_has_three_valid_meshes_about_twice_apart(blunt):
    d, af, fam = family("0012", blunt)
    assert [f.label for f in fam] == ["coarse", "medium", "fine"]
    cells = [f.mesh.n_cells for f in fam]
    assert cells == [f.plan.cells for f in fam]
    assert 1.6 < cells[1] / cells[0] < 2.5 and 1.6 < cells[2] / cells[1] < 2.5
    medium = plan_mesh(d, af, RE)
    assert cells[1] == medium.cells                  # the medium mesh is the one shown in the app


# ---------------------------------------------------------------- app
def widget(at, kind, key):
    return [w for w in getattr(at, kind) if w.key == key][0]


def mapped():
    at = AppTest.from_file(APP, default_timeout=180).run()
    widget(at, "text_input", "af_query").set_value("0012")
    at = at.run()
    mode = widget(at, "radio", "mesh_mode")
    mode.set_value(mode.options[1])
    return at.run()


def test_family_download_after_ticking_the_box():
    at = mapped()
    assert not any(el.proto.id.endswith("msh_family_download") for el in at.get("download_button"))
    widget(at, "checkbox", "msh_family").set_value(True)
    at = at.run()
    assert not at.exception and not at.error
    assert any(el.proto.id.endswith("msh_family_download") for el in at.get("download_button"))


def test_gci_section_in_automation_tab():
    at = AppTest.from_file(APP, default_timeout=180).run()
    auto = at.tabs[2]
    keys = {w.key for w in auto.number_input}
    for k in ("gci_n1", "gci_n2", "gci_n3", "gci_cl1", "gci_cl2", "gci_cl3", "gci_cd1", "gci_cd2", "gci_cd3"):
        assert k in keys, k
    vals = dict(gci_n1=18000, gci_n2=8000, gci_n3=4500, gci_cl1=6.063, gci_cl2=5.972, gci_cl3=5.863)
    for k, v in vals.items():
        widget(at, "number_input", k).set_value(v)
    at = at.run()
    assert not at.exception and not at.error
    text = " ".join(str(d.value) for d in at.dataframe)
    assert "6.1685" in text or "6.168" in text


def test_workflow_line_on_automation_tab():
    at = AppTest.from_file(APP, default_timeout=180).run()
    assert any(tr("auto_steps", "tr")[:30] in m.value for m in at.tabs[2].markdown)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_texts(lang):
    for k in ("msh_family", "msh_family_help", "msh_family_download", "msh_family_cells", "gci_title",
              "gci_note", "gci_fine", "gci_medium", "gci_coarse", "gci_cells", "auto_steps", "gci_osc"):
        assert tr(k, lang) != k, k


@pytest.mark.parametrize("name", ["README.md", "README.en.md", "CHANGELOG.md"])
def test_docs_describe_mesh_independence(name):
    text = (Path(APP).parent / name).read_text(encoding="utf-8")
    assert "GCI" in text and "Celik" in text and "√2" in text


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_family_note_says_it_was_tried(lang):
    text = tr("msh_family_cells", lang)
    assert "denenmedi" not in text and "not tried" not in text and "0.835" in text


@pytest.mark.parametrize("name", ["README.md", "README.en.md", "CHANGELOG.md"])
def test_docs_hold_the_family_run(name):
    text = (Path(APP).parent / name).read_text(encoding="utf-8")
    assert "0.8355" in text and ("0.8353" in text or "0.83529" in text)
