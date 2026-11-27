"""Notes from the 2026-11-25 pressure-far-field study (Fluent 2024 R2): M 0.15 did not converge,
M 0.3 and 0.5 did, with the whole outer boundary as pressure-far-field."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.i18n import tr
from _docs import doc_text

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def mach_page(mach):
    at = AppTest.from_file(APP, default_timeout=120).run()
    [r for r in at.radio if r.key == "flow_mode"][0].set_value("mach")
    at = at.run()
    [w for w in at.number_input if w.key == "mach_in"][0].set_value(mach)
    return at.run()


def low_mach_shown(at):
    head = tr("warn_ff_low_mach", "tr", m=0.15)[:40]
    return any(w.value.startswith(head[:30]) for w in at.warning)


def test_low_mach_in_mach_mode_points_to_velocity_inlet():
    at = mach_page(0.15)
    assert not at.exception
    assert low_mach_shown(at)


@pytest.mark.parametrize("mach", [0.3, 0.5])
def test_no_low_mach_note_from_mach_0_3(mach):
    at = mach_page(mach)
    assert not at.exception
    assert not low_mach_shown(at)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_low_mach_note_states_what_was_tried(lang):
    text = tr("warn_ff_low_mach", lang, m=0.15)
    for needle in ("velocity-inlet", "0.15", "0.3", "0.5", "2024 R2"):
        assert needle in text


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_far_field_note_asks_for_the_whole_outer_boundary(lang):
    text = tr("fl_ff_note", lang)
    assert "outlet" in text and "Time Scale Factor" in text and "0.2" in text


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_named_selection_text_covers_far_field(lang):
    assert "pressure-far-field" in tr("named_sel", lang)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_far_field_note_reports_the_tried_operating_pressure_and_time_scale(lang):
    text = tr("fl_ff_note", lang)
    assert "denenmedi" not in text and "not tried" not in text
    assert "Operating Pressure 0" in text and "Time Scale Factor 1" in text


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_journal_note_says_a_far_field_sweep_was_tried(lang):
    note = doc_text("README.md" if lang == "tr" else "README.en.md")
    assert "M 0.3" in note and "2…8°" in note


def test_journal_header_says_a_far_field_sweep_was_tried():
    from airfoilmatic.fluent import sweep_journal
    text = sweep_journal(2, 8, 2)
    assert "pressure-far-field case, M 0.3" in text


@pytest.mark.parametrize("name", ["README.md", "README.en.md", "CHANGELOG.md"])
def test_docs_say_a_far_field_sweep_was_tried(name):
    text = doc_text(name)
    assert "M 0.3, 2…8°" in text
