"""Fluent journal part of the angle-of-attack sweep on the Mesh / y+ tab."""
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


def by_key(at, kind, key):
    found = [w for w in getattr(at, kind) if w.key == key]
    assert found, f"{kind} with key '{key}' not on the page"
    return found[0]


def download_labels(at):
    """AppTest has no download_button accessor; read the raw elements instead."""
    return [el.proto.label for el in at.get("download_button")]


def has_journal_download(at):
    return any(el.proto.id.endswith("jou_download") for el in at.get("download_button"))


def test_input_widgets_exist_with_defaults():
    at = start()
    assert not at.exception
    assert by_key(at, "number_input", "jou_iter").value == 1000
    assert by_key(at, "text_input", "jou_expr").value == "aoa"
    assert by_key(at, "text_input", "jou_folder").value == ""
    assert by_key(at, "number_input", "jou_save_every").value == 0
    assert not [w for w in at.checkbox if w.key == "jou_save_each"]
    keys = {w.key for w in at.text_input}
    assert not keys & {"jou_zones", "jou_lift", "jou_drag"}


def test_download_button_appears_with_defaults():
    at = start()
    assert not at.exception and not at.error
    assert has_journal_download(at)


def test_save_every_and_folder_still_give_a_download():
    at = start()
    by_key(at, "number_input", "jou_save_every").set_value(5)
    by_key(at, "text_input", "jou_folder").set_value("C:/work/fluent")
    at = at.run()
    assert not at.exception and not at.error
    assert has_journal_download(at)


def test_custom_expression_name_changes_the_setup_block():
    at = start()
    by_key(at, "text_input", "jou_expr").set_value("alpha")
    at = at.run()
    assert not at.exception and not at.error
    assert has_journal_download(at)
    assert any("cos(alpha)" in c.value for c in at.code)


def test_invalid_expression_name_shows_an_error_and_no_download():
    at = start()
    by_key(at, "text_input", "jou_expr").set_value("1aoa")
    at = at.run()
    assert not at.exception
    assert at.error
    assert not has_journal_download(at)


def test_invalid_expression_error_is_turkish_in_turkish_ui():
    at = start("tr")
    by_key(at, "text_input", "jou_expr").set_value("1aoa")
    at = at.run()
    text = " ".join(e.value for e in at.error)
    assert "may only contain" not in text and "Expression name" not in text
    assert "yalnızca" in text


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_texts_render_in_both_languages(lang):
    at = start(lang)
    assert not at.exception and not at.error
    html = " ".join(m.value for m in at.markdown)
    assert tr("jou_title", lang) in html
    assert tr("jou_note", lang, iterations=1000, expr="aoa") in " ".join(c.value for c in at.caption)
    assert by_key(at, "number_input", "jou_iter").label == tr("jou_iter", lang)
    assert by_key(at, "text_input", "jou_expr").label == tr("jou_expr", lang)
    assert by_key(at, "number_input", "jou_save_every").label == tr("jou_save_every", lang)
    assert tr("jou_download", lang) in download_labels(at)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_setup_code_block_lists_the_four_expressions(lang):
    at = start(lang)
    code = [c.value for c in at.code if "cos(aoa)" in c.value]
    assert code, "setup code block not found"
    text = code[0]
    assert "sin(aoa)" in text
    assert "cl" in text and "cd" in text
    assert "dot(Force(['wall'])" in text
    assert tr("jou_setup_cl", lang) in text
