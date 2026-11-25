"""Automation tab: angle sweep, Fluent journal and the polar from a report file."""
import math
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.i18n import tr

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def start(lang="tr"):
    at = AppTest.from_file(APP, default_timeout=120).run()
    if lang == "en":
        [r for r in at.radio if r.label == "Dil / Language"][0].set_value("English")
        at = at.run()
    return at


def keys_in(container, kind):
    return {w.key for w in getattr(container, kind)}


def report_bytes():
    lines = ['"polar-rfile"', '"Iteration" "alfa etc.."', '("Iteration" "alfa" "cd" "cl")']
    it = 100
    for aoa, cl, cd, amp in ((-2, -0.21, 0.0055, 0.0), (0, 0.0001, 0.0051, 0.0), (10, 1.04, 0.013, 0.02)):
        for i in range(80):
            lines.append(f"{it} {math.radians(aoa)!r} {cd!r} {cl + amp * math.sin(i)!r}")
            it += 1
    return ("\n".join(lines) + "\n").encode()


def upload_report(at, data):
    [u for u in at.file_uploader if u.key == "polar_file"][0].upload("polar.out", data, "text/plain")
    return at.run()


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_third_tab_is_automation(lang):
    at = start(lang)
    assert not at.exception
    assert [t.label for t in at.tabs][2] == tr("tab_auto", lang)


def test_sweep_and_journal_moved_from_mesh_tab_to_automation_tab():
    at = start()
    mesh, auto = at.tabs[1], at.tabs[2]
    for key in ("sweep_from", "sweep_to", "sweep_step", "jou_iter", "jou_save_every"):
        assert key in keys_in(auto, "number_input"), key
        assert key not in keys_in(mesh, "number_input"), key
    assert "jou_expr" in keys_in(auto, "text_input")
    assert any(el.proto.id.endswith("jou_download") for el in auto.get("download_button"))


def test_polar_section_shows_uploader_and_no_table_before_upload():
    at = start()
    assert "polar_file" in {u.key for u in at.tabs[2].file_uploader}
    assert not any(el.proto.id.endswith("polar_csv") for el in at.get("download_button"))


def test_uploaded_report_gives_table_csv_and_flags_oscillation():
    at = upload_report(start(), report_bytes())
    assert not at.exception and not at.error
    assert any(el.proto.id.endswith("polar_csv") for el in at.get("download_button"))
    page = " ".join(m.value for m in at.markdown) + " ".join(str(d.value) for d in at.dataframe)
    assert "1.04" in page
    assert any(tr("polar_warn_osc", "tr", angles="10").split("{")[0][:25] in w.value for w in at.warning)


def test_bad_report_shows_a_turkish_error():
    at = upload_report(start(), b"hello\n")
    assert not at.exception
    assert any("Fluent report file değil" in e.value for e in at.error)


def test_sidebar_upload_still_works_with_the_polar_uploader_on_the_page():
    at = start()
    [r for r in at.radio if r.key == "source"][0].set_value("file")
    at = at.run()
    upload = [u for u in at.file_uploader if u.key == "upload"]
    assert len(upload) == 1
