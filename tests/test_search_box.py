"""Section search box with suggestions while typing (Altori, 2026-11-27).

One box: typing lists every library section (and common NACA codes) whose label contains the text;
a value that is not in the list (any other NACA code, a free search such as "64") is taken with
Enter and searched as before. The second list ("sections found") only appears when such a free
search has more than one match.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic import library as lib
from airfoilmatic.i18n import tr

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def start(text=None):
    at = AppTest.from_file(APP, default_timeout=240)
    if text is not None:
        at.session_state["af_text"] = text
    return at.run()


def box(at):
    return [s for s in at.sidebar.selectbox if s.key and s.key.startswith("af_box")][0]


def test_box_suggests_library_sections_and_takes_new_values():
    at = start()
    assert not at.exception
    b = box(at)
    assert b.proto.accept_new_options
    labels = b.options
    for s in lib.library()[:20]:
        assert any(s.title in l for l in labels), s.title
    assert any(l.startswith("NACA 2412") for l in labels)       # common NACA codes are suggested too
    assert any("64-012" in l or "64012" in l for l in labels)


def test_picking_a_suggestion_shows_that_section_without_a_second_list():
    at = start()
    sid = [s for s in lib.library() if s.id == "s9104"][0]
    box(at).set_value(f"{sid.title} · {sid.family_name}")
    at = at.run()
    assert not at.exception and not at.error
    assert at.session_state["af_text"] == "s9104"
    assert not any(s.key and s.key.startswith("pick_") for s in at.sidebar.selectbox)
    assert any("S9104" in m.value for m in list(at.markdown) + list(at.caption))


@pytest.mark.parametrize("text, title", [("2412", "NACA 2412"), ("23015", "NACA 23015")])
def test_any_naca_code_typed_is_drawn(text, title):
    at = start(text)
    assert not at.exception and not at.error
    assert any(title in m.value for m in list(at.markdown) + list(at.caption))


def test_free_search_lists_the_matches():
    at = start("64")
    assert not at.exception
    picks = [s for s in at.sidebar.selectbox if s.key and s.key.startswith("pick_")]
    assert picks and len(picks[0].options) > 1
    assert all("64" in o.replace("-", "").replace(" ", "") for o in picks[0].options[:5])


def test_unknown_text_still_says_not_found():
    at = start("zzqq")
    assert any(tr("not_found", "tr", q="zzqq")[:10] in e.value for e in at.error)


def test_dice_and_history_drive_the_box():
    at = start()
    [b for b in at.button if b.key == "dice"][0].click()
    at = at.run()
    rolled = at.session_state["af_text"]
    rolled_sec = lib.by_id(rolled)
    assert rolled != "4412" and box(at).value == f"{rolled_sec.title} · {rolled_sec.family_name}"
    [b for b in at.button if b.key == "hist_back"][0].click()
    at = at.run()
    assert at.session_state["af_text"] == "4412" and box(at).value == "NACA 4412"


def test_search_hint_mentions_typing():
    for lang in ("tr", "en"):
        assert tr("search_placeholder", lang) and tr("search_help", lang)
    assert "Enter" in tr("search_help", "tr") and "Enter" in tr("search_help", "en")


@pytest.mark.parametrize("name, words", [
    ("CHANGELOG.md", ("Suggestions while typing", "yazarken öneri")),
    ("README.md", ("yazarken",)), ("README.en.md", ("while typing",))])
def test_docs_describe_the_search_box(name, words):
    text = (Path(__file__).resolve().parents[1] / name).read_text(encoding="utf-8")
    for w in words:
        assert w in text, w
