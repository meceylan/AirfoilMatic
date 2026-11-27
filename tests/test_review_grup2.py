"""Findings of the independent review of 2026-11-27, group 2 (usability, texts, small fixes)."""
import ast
import math
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.fluent import alpha_sweep, parse_angles
from airfoilmatic.gci import gci
from airfoilmatic.geometry import AirfoilError, naca
from airfoilmatic.i18n import ERRORS_TR, tr
from airfoilmatic.polar import guess_columns, merge_reports, polar, read_report

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")


def start():
    return AppTest.from_file(APP, default_timeout=240).run()


def w(at, kind, key):
    return [x for x in getattr(at, kind) if x.key == key][0]


# ---------------------------------------------------------------- app
def test_uploaded_file_survives_a_search_round_trip():
    at = start()
    w(at, "radio", "source").set_value("file")
    at = at.run()
    w(at, "file_uploader", "upload").upload("myfoil.dat", _naca_dat(), "text/plain")
    at = at.run()
    assert not at.exception
    w(at, "radio", "source").set_value("search")
    at = at.run()
    w(at, "radio", "source").set_value("file")
    at = at.run()
    assert not at.exception
    assert not any(tr("upload_info", "tr")[:20] in i.value for i in at.info)
    assert any("myfoil" in c.value for c in at.sidebar.caption)


def _naca_dat():
    af = naca("2412")
    lines = ["NACA2412"] + [f"{x:.6f} {y:.6f}" for x, y in zip(np.r_[af.xu[::-1], af.xl[1:]],
                                                                np.r_[af.yu[::-1], af.yl[1:]])]
    return "\n".join(lines).encode()


def test_dice_warning_goes_away_after_a_new_section():
    at = start()
    w(at, "slider", "f_thick").set_value((0, 2))
    at = at.run()
    w(at, "button", "dice").click()
    at = at.run()
    assert any(tr("dice_empty", "tr")[:20] in x.value for x in at.sidebar.warning)
    w(at, "slider", "f_thick").set_value((0, 40))
    at.session_state["af_text"] = "0012"
    at = at.run()
    assert not any(tr("dice_empty", "tr")[:20] in x.value for x in at.sidebar.warning)


def test_low_mach_warning_is_one_short_line():
    at = start()
    w(at, "radio", "flow_mode").set_value("mach")
    at = at.run()
    warns = [x.value for x in at.warning if x.value.startswith(tr("warn_ff_low_mach", "tr", m=0.15)[:30])]
    assert warns and len(warns[0]) < 200
    assert tr("warn_ff_low_mach", "tr", m=0.15) in " ".join(e.label + " " for e in at.expander) + \
        " ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)


def test_split_line_boxes_are_disabled_in_as_drawn_mode():
    at = start()
    w(at, "radio", "source").set_value("file")
    at = at.run()
    w(at, "file_uploader", "upload").upload("foil.dat", _naca_dat(), "text/plain")
    w(at, "checkbox", "as_is").set_value(True)
    at = at.run()
    boxes = [c for c in at.checkbox if c.key.startswith("line_")]
    assert boxes and all(c.disabled for c in boxes)


def test_gci_shows_the_absolute_band_and_warns_on_small_ratios():
    at = start()
    for k, v in dict(gci_n1=18000, gci_n2=15000, gci_n3=4500, gci_cl1=6.044444, gci_cl2=6.033333, gci_cl3=5.877778).items():
        w(at, "number_input", k).set_value(v)
    at = at.run()
    assert not at.exception
    assert any(x.value.startswith(tr("gci_ratio", "tr", r=1.0)[:10]) for x in at.warning)
    cols = [c for d in at.dataframe for c in d.value.columns]
    assert tr("gci_band", "tr") in cols


def test_gci_names_the_columns_it_read():
    at = start()
    up = w(at, "file_uploader", "gci_files")
    for s in ("coarse", "medium", "fine"):
        up.upload(f"{s}.out", (ROOT / "tests" / "data" / "gci_naca4412" / f"{s}.out").read_bytes(), "text/plain")
    at = at.run()
    assert any("alpha" in c.value and "cl" in c.value for c in at.caption)


# ---------------------------------------------------------------- core
def test_gci_band_is_absolute():
    g = gci([18000, 8000, 4500], [6.063, 5.972, 5.863])
    assert g.band == pytest.approx(g.gci_fine * 6.063)
    z = gci([18000, 8000, 4500], [0.0, 0.002, 0.005])     # Cl = 0 on the fine mesh: % is meaningless
    assert math.isinf(z.gci_fine) and math.isfinite(z.band) and z.band > 0


@pytest.mark.parametrize("cols, want", [
    (["Iteration", "cl-alpha-report", "cdconv", "cd", "cl", "alpha"], dict(angle="alpha", cl="cl", cd="cd")),
    (["Iteration", "cdconv", "cd-1", "cl", "aoa"], dict(angle="aoa", cl="cl", cd="cd-1")),
    (["Iteration", "clconv", "cl", "cd", "alfa"], dict(angle="alfa", cl="cl", cd="cd")),
])
def test_column_guess_skips_convergence_and_lift_slope_columns(cols, want):
    assert guess_columns(cols) == want


def test_nan_rows_are_skipped():
    rep = read_report('"r"\n"Iteration" "x"\n("Iteration" "alpha" "cd" "cl")\n'
                      + "\n".join(f"{i} 0.0 {'nan' if i == 50 else 0.01} 0.4" for i in range(1, 101)))
    assert np.isfinite(rep.rows).all() and len(rep.rows) == 99
    assert polar(rep, "alpha", "cl", "cd")[0].cd == pytest.approx(0.01)


def test_one_file_per_report_definition_is_joined_on_the_iteration():
    head = '"{n}"\n"Iteration" "x"\n("Iteration" "{n}")\n'
    files = [read_report(head.format(n=n) + "\n".join(f"{i} {v}" for i in range(1, 101)))
             for n, v in (("cl", 0.4), ("cd", 0.01), ("alpha", 0.0))]
    rows = polar(merge_reports(files), "alpha", "cl", "cd")
    assert len(rows) == 1 and rows[0].cl == pytest.approx(0.4) and rows[0].cd == pytest.approx(0.01)


def test_range_sweep_stays_within_180_degrees():
    with pytest.raises(ValueError) as e:
        alpha_sweep(0, 1000, 3, 1.0)
    assert str(e.value) in ERRORS_TR


def test_own_angles_are_rounded_as_the_journal_writes_them():
    assert parse_angles("1.23456, 2") == [1.2346, 2.0]


def test_five_digit_code_needs_a_design_lift_digit():
    with pytest.raises(AirfoilError) as e:
        naca("01012")
    assert str(e.value) in ERRORS_TR


def test_library_docstring_matches_the_library():
    from airfoilmatic import library as lib
    assert f"{len(lib.library())} files" in lib.__doc__


def test_every_literal_error_message_is_translated():
    missing = []
    for path in (ROOT / "airfoilmatic").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and node.exc.args:
                arg = node.exc.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value not in ERRORS_TR:
                    missing.append((path.name, arg.value))
    assert not missing, missing


def test_ci_runs_the_python_of_streamlit_cloud():
    text = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "3.14" in text


# ---------------------------------------------------------------- docs
@pytest.mark.parametrize("name, words", [("README.md", ("burunda", "0.73")), ("README.en.md", ("at the nose", "0.73"))])
def test_s9104_numbers_say_where_they_apply(name, words):
    text = (ROOT / name).read_text(encoding="utf-8")
    for x in words:
        assert x in text, x


def test_changelog_lists_the_group2_fixes():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    for w in ("Usability fixes from the code review", "Kod incelemesinden kullanım düzeltmeleri",
              "cl-alpha-report", "Python 3.14", "±"):
        assert w in text, w


def test_deferred_mesh_downloads_produce_the_files():
    """The .msh and the family ZIP are written by Streamlit's deferred download (a callable for
    ``data``, run when the button is clicked): run that path with the app's own writers."""
    import io
    import zipfile
    from streamlit.runtime.media_file_manager import MediaFileManager
    from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage
    from airfoilmatic.blockmesh import build_cgrid, family_zip, mesh_family, read_fluent_msh, to_fluent_msh
    from airfoilmatic.geometry import split_at
    from airfoilmatic.mesh import plan_mesh
    from airfoilmatic.topology import build_domain
    af = split_at(naca("0012"))
    d = build_domain(af, "c_grid", r_inlet=15.0, l_wake=20.0)
    m = build_cgrid(d, af, plan_mesh(d, af, 2.0e6, refine=0.5))
    storage = MemoryMediaFileStorage("/media")
    mgr = MediaFileManager(storage)
    fid = mgr.add_deferred(lambda m=m: to_fluent_msh(m, title="t"), "text/plain", "c", file_name="a.msh")
    url = mgr.execute_deferred(fid)
    text = storage.get_file(url.split("/")[-1].split(".")[0]).content.decode()
    assert len(read_fluent_msh(text)[0]) == len(m.nodes)
    fam = mesh_family(d, af, 1.0e5)
    fid = mgr.add_deferred(lambda f=fam: family_zip(f, "p", title="t"), "application/zip", "c", file_name="f.zip")
    url = mgr.execute_deferred(fid)
    data = storage.get_file(url.split("/")[-1].split(".")[0]).content
    assert sorted(zipfile.ZipFile(io.BytesIO(data)).namelist()) == ["p_coarse.msh", "p_fine.msh", "p_medium.msh"]
