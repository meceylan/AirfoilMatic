"""Layout fixes of the review 2026-11-27 (group B): short card labels, the main download near the
top of the Geometry tab, Automation sections as headings, the journal inputs before what they set."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic import ui
from airfoilmatic.i18n import tr

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")
SRC = (ROOT / "app.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("key", ["flow_re", "flow_mach", "flow_vel", "method_inflation", "method_mapped"])
def test_card_options_are_short(key):
    for lang in ("tr", "en"):
        assert len(tr(key, lang)) <= 12, (key, lang, tr(key, lang))


def test_card_labels_do_not_break_inside_words():
    css = ui.css()
    assert "keep-all" in css


def test_main_download_comes_right_after_the_close_up():
    i_zoom = SRC.index('fitted_chart(fig_zoom')
    i_dl = SRC.index('key="dl_main"')
    i_full = SRC.index('st.subheader(t("full_title"))')
    assert i_zoom < i_dl < i_full


def test_automation_sections_are_headings():
    for k in ("sweep_title", "jou_title", "polar_title", "gci_title"):
        assert f'st.subheader(t("{k}"))' in SRC, k


def test_journal_inputs_come_before_the_setup_lines_and_download_is_primary():
    assert SRC.index('key="jou_iter"') < SRC.index("st.code(") < SRC.index('key="jou_download"')
    at = AppTest.from_file(APP, default_timeout=240).run()
    assert not at.exception
    btn = [b for b in at.get("download_button") if b.proto.id.endswith("jou_download")][0]
    assert btn.proto.type == "primary"
    code = [c for c in at.code if "aoa" in c.value][0]
    assert code.proto.wrap_lines


def test_mesh_file_download_is_primary():
    at = AppTest.from_file(APP, default_timeout=240).run()
    mode = [w for w in at.radio if w.key == "mesh_mode"][0]
    mode.set_value(mode.options[1])
    at = at.run()
    btn = [b for b in at.get("download_button") if b.proto.id.endswith("msh_download")][0]
    assert btn.proto.type == "primary"


def test_gci_manual_entry_is_folded_until_needed():
    at = AppTest.from_file(APP, default_timeout=240).run()
    labels = [e.label for e in at.expander]
    assert tr("gci_manual", "tr") in labels
    assert tr("gci_manual", "tr") and tr("gci_manual", "en")
