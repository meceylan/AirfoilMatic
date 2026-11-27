"""Shorter on-screen texts (review 2026-11-27): what the user does now and the values to type stay;
tried / not tried stays as one clause; the run numbers live in README + docs/VALIDATION*.md."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.i18n import STRINGS, tr

APP = str(Path(__file__).resolve().parents[1] / "app.py")

LIMITS = {"msh_note": 70, "jou_note": 80, "jou_setup_note": 70, "profile_help": 35, "polar_note": 45,
          "gci_note": 45, "infl_edges_note": 110, "howto_infl": 140, "q_explain": 90, "fl_ff_note": 70,
          "infl_note": 60, "tu_note": 55, "named_sel": 60, "fluent_note": 60, "jou_save_every_help": 65,
          "auto_steps": 45}


@pytest.mark.parametrize("key, limit", LIMITS.items())
def test_texts_are_short(key, limit):
    assert len(STRINGS[key]["tr"].split()) <= limit, (key, len(STRINGS[key]["tr"].split()))


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_spaceclaim_and_solidworks_are_tried_profile_dm_is_not(lang):
    sc = tr("download_sc_help", lang)
    assert ("denenmedi" not in sc) and ("not tried" not in sc)
    ph = tr("profile_help", lang)
    assert ("SpaceClaim" in ph and "SolidWorks" in ph)
    assert ("DesignModeler TXT henüz denenmedi" in ph) if lang == "tr" else ("DesignModeler TXT not tried yet" in ph)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_mesh_and_journal_notes_say_what_was_tried(lang):
    word = "denendi" if lang == "tr" else "tried"
    for k in ("msh_note", "jou_note", "jou_setup_note", "polar_note", "fl_ff_note"):
        assert word in tr(k, lang).lower(), k
    assert "VALIDATION" in tr("msh_note", lang)
    jn = tr("jou_note", lang, expr="aoa", iterations=500)
    assert "500" in jn and "aoa" in jn and "Workbench" in jn


def test_named_selection_uses_mach_at_least_0_3():
    assert "M ≥ 0.3" in tr("named_sel", "tr") and "M ≥ 0.3" in tr("named_sel", "en")


def test_profile_download_steps_moved_to_button_tooltips():
    for k in ("profile_dm_help", "profile_sw_help", "profile_sc_help"):
        assert tr(k, "tr") and tr(k, "en")
    at = AppTest.from_file(APP, default_timeout=240).run()
    helps = {b.proto.id.split("-")[-1] if False else b.proto.id: b.proto.help for b in at.get("download_button")}
    assert any("Curve Through XYZ Points" in h for h in helps.values())
    assert any("File → Open" in h for h in helps.values())


def test_automation_intro_is_not_shown_twice():
    at = AppTest.from_file(APP, default_timeout=240).run()
    assert not any(tr("auto_intro", "tr")[:30] in c.value for c in at.caption)
