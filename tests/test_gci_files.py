"""GCI from uploaded Fluent report files: Cl and Cd of each mesh come from the report file, the cell
counts from the app's own grid family (file name says coarse / medium / fine) or are typed in."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.blockmesh import FAMILY
from airfoilmatic.gci import gci, gci_by_angle, mesh_label
from airfoilmatic.geometry import naca, split_at
from airfoilmatic.i18n import ERRORS_TR, tr
from airfoilmatic.mesh import plan_mesh
from airfoilmatic.polar import PolarRow, STEADY, OSCILLATING, guess_columns, polar, read_report
from airfoilmatic.topology import build_domain

APP = str(Path(__file__).resolve().parents[1] / "app.py")
DATA = Path(__file__).resolve().parent / "data" / "gci_naca4412"
CELLS = dict(coarse=42944, medium=84870, fine=169824)     # Fluent 2024 R2 transcript, 2026-11-27


def file_polar(name):
    rep = read_report((DATA / f"{name}.out").read_bytes())
    g = guess_columns(rep.columns)
    return polar(rep, g["angle"], g["cl"], g["cd"])


def row(aoa, cl, cd=0.01, status=STEADY):
    return PolarRow(aoa=aoa, iterations=100, first=1, last=100, cl=cl, cl_range=0.0, cd=cd, cd_range=0.0,
                    ld=cl / cd, status=status)


# ---------------------------------------------------------------- file names
@pytest.mark.parametrize("name, label", [
    ("coarse.out", "coarse"), ("medium.out", "medium"), ("fine.out", "fine"),
    ("NACA4412_Kaba.out", "coarse"), ("naca4412-orta-a4.out", "medium"), ("İnce.out", "fine"),
    ("ince.OUT", "fine"), ("medium_1929.out", "medium"), ("AirfoilMatic_NACA4412_CGrid_fine.out", "fine"),
])
def test_label_from_file_name(name, label):
    assert mesh_label(name) == label


@pytest.mark.parametrize("name", ["polar.out", "portal.out", "sincere.out", "refined.out", "fine_coarse.out",
                                  "mesh1.out"])
def test_no_or_ambiguous_label(name):
    assert mesh_label(name) is None


# ---------------------------------------------------------------- GCI per angle
def test_real_family_files_give_the_gci_of_their_means():
    pols = [file_polar(n) for n in ("coarse", "medium", "fine")]
    cells = [CELLS[n] for n in ("coarse", "medium", "fine")]
    out = gci_by_angle(pols, cells)
    assert [r.aoa for r in out] == [pytest.approx(4.0)] * 2
    assert [r.name for r in out] == ["Cl", "Cd"]
    cl = out[0]
    assert cl.values == pytest.approx([0.835286, 0.835907, 0.835520], abs=2e-6)   # fine, medium, coarse
    assert cl.cells == [169824, 84870, 42944]
    ref = gci(cells, [p[0].cl for p in pols])
    assert cl.result.phi_ext == pytest.approx(ref.phi_ext) and not cl.result.monotonic
    assert cl.error is None and cl.unsteady == []


def test_only_angles_in_all_three_files():
    pols = [[row(0, 0.40), row(2, 0.62), row(4, 0.83)],
            [row(2, 0.63), row(4, 0.84), row(6, 1.05)],
            [row(2, 0.635), row(4, 0.845)]]
    out = gci_by_angle(pols, [40000, 80000, 160000])
    assert sorted({r.aoa for r in out}) == [2, 4]


def test_no_common_angle_gives_nothing():
    assert gci_by_angle([[row(0, 0.4)], [row(2, 0.6)], [row(4, 0.8)]], [1, 2, 3]) == []


def test_unsteady_file_is_named_and_gci_error_kept_per_row():
    pols = [[row(4, 0.80, status=OSCILLATING)], [row(4, 0.82)], [row(4, 0.83)]]
    out = gci_by_angle(pols, [40000, 80000, 160000])
    assert out[0].unsteady == ["coarse"]
    # Cd is the same on all meshes: fine == medium means mesh independent, no error
    assert out[1].error is None
    bad = gci_by_angle([[row(4, 0.80)], [row(4, 0.80)], [row(4, 0.83)]], [40000, 80000, 160000])
    assert bad[0].error == "Coarse and medium values are equal: the order of convergence is undefined"
    assert bad[0].result is None


def test_equal_cell_counts_error():
    out = gci_by_angle([[row(4, 0.80)], [row(4, 0.82)], [row(4, 0.83)]], [80000, 80000, 160000])
    assert out[0].error == "The three meshes need different cell counts"


# ---------------------------------------------------------------- app
def widget(at, kind, key):
    return [w for w in getattr(at, kind) if w.key == key][0]


def mapped(code="4412"):
    at = AppTest.from_file(APP, default_timeout=240).run()
    widget(at, "text_input", "af_query").set_value(code)
    at = at.run()
    mode = widget(at, "radio", "mesh_mode")
    mode.set_value(mode.options[1])
    return at.run()


def upload(at, names, src=("coarse", "medium", "fine")):
    up = widget(at, "file_uploader", "gci_files")
    for name, s in zip(names, src):
        up.upload(name, (DATA / f"{s}.out").read_bytes(), "text/plain")
    return at.run()


def app_family_cells(code="4412"):
    af = split_at(naca(code))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    return {lab: plan_mesh(d, af, 2.0e6, refine=k).cells for lab, k in FAMILY}


def test_uploader_in_gci_section():
    at = AppTest.from_file(APP, default_timeout=240).run()
    assert "gci_files" in {u.key for u in at.tabs[2].file_uploader}


def test_labelled_files_take_cell_counts_from_the_family():
    at = upload(mapped(), ["coarse.out", "medium.out", "fine.out"])
    assert not at.exception and not at.error
    n = {k: widget(at, "number_input", k).value for k in ("gci_n1", "gci_n2", "gci_n3")}
    fam = app_family_cells()
    assert n == dict(gci_n1=fam["fine"], gci_n2=fam["medium"], gci_n3=fam["coarse"])
    keys = {w.key for w in at.number_input}
    assert "gci_cl1" not in keys and "gci_cd1" not in keys           # values come from the files
    text = " ".join(d.value.to_string() for d in at.dataframe)
    assert "0.83529" in text or "0.835286" in text
    assert any(tr("gci_cells_family", "tr")[:25] in c.value for c in at.caption)


def test_cell_counts_stay_editable():
    at = upload(mapped(), ["coarse.out", "medium.out", "fine.out"])
    for k, v in (("gci_n1", 169824), ("gci_n2", 84870), ("gci_n3", 42944)):
        widget(at, "number_input", k).set_value(v)
    at = at.run()
    assert not at.exception and not at.error
    assert widget(at, "number_input", "gci_n1").value == 169824


def test_unlabelled_files_ask_for_cell_counts_then_sort_by_them():
    at = AppTest.from_file(APP, default_timeout=240).run()
    at = upload(at, ["a.out", "b.out", "c.out"])
    assert not at.exception and not at.error
    assert any(tr("gci_need_cells", "tr")[:25] in i.value for i in at.info)
    assert not any("0.835" in d.value.to_string() for d in at.dataframe)
    # a = coarse, b = medium, c = fine data; the inputs follow the upload order
    for k, v in (("gci_n1", 42944), ("gci_n2", 84870), ("gci_n3", 169824)):
        widget(at, "number_input", k).set_value(v)
    at = at.run()
    assert not at.exception and not at.error
    text = " ".join(d.value.to_string() for d in at.dataframe)
    assert "0.83529" in text or "0.835286" in text


def test_labelled_files_without_mapped_mode_say_why_counts_are_empty():
    at = upload(AppTest.from_file(APP, default_timeout=240).run(), ["coarse.out", "medium.out", "fine.out"])
    assert not at.exception and not at.error
    assert widget(at, "number_input", "gci_n1").value is None
    assert any(tr("gci_cells_no_family", "tr")[:25] in c.value for c in at.caption)


def test_wrong_number_of_files_is_an_error():
    at = AppTest.from_file(APP, default_timeout=240).run()
    at = upload(at, ["a.out", "b.out"], src=("coarse", "medium"))
    assert any(tr("gci_files_bad", "tr")[:25] in e.value for e in at.error)


def test_new_messages_are_translated():
    for k in ("gci_upload", "gci_upload_help", "gci_cells_family", "gci_need_cells", "gci_files_bad",
              "gci_no_common", "gci_warn_unsteady", "gci_file", "gci_cells_no_family"):
        assert tr(k, "tr") and tr(k, "en") and tr(k, "tr") != tr(k, "en"), k
    assert "The three meshes need different cell counts" in ERRORS_TR
