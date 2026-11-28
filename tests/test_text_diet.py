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
    for k in ("profile_sc_help", "profile_sw_help"):        # the tried ones say so in their tooltip
        assert ("Denendi" if lang == "tr" else "Tried") in tr(k, lang)
    # what was not tried is written in README / docs/VALIDATION*.md, not on screen (Altori, 2026-11-28)


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


def test_no_on_screen_text_says_not_tried():
    """Altori 2026-11-28: the app does not write "not tried" on screen; the documents (README,
    docs/VALIDATION*.md) list what was and was not tried. The app still never claims an untried
    output works."""
    bad = [(k, lang) for k, v in STRINGS.items() for lang in ("tr", "en")
           if any(w in v[lang].lower() for w in ("denenmedi", "denenmemiş", "not tried", "untested"))]
    assert not bad, bad


def test_developer_card_is_at_the_top_of_the_sidebar():
    at = AppTest.from_file(APP, default_timeout=240).run()
    first = at.sidebar.children[0] if hasattr(at.sidebar, "children") else None
    side = [m.value for m in at.sidebar.markdown]
    assert side and "am-foot" in side[0]
    src = Path(APP).read_text(encoding="utf-8")
    assert src.index("dev_slot") < src.index('st.sidebar.radio("Dil / Language"')


@pytest.mark.parametrize("name, imgs", [("README.md", ("docs/img/app-geometry.png", "docs/img/app-mesh.png")),
                                         ("README.en.md", ("docs/img/app-geometry-en.png", "docs/img/app-mesh-en.png"))])
def test_readme_shows_light_theme_screenshots(name, imgs):
    root = Path(APP).parent
    text = (root / name).read_text(encoding="utf-8")
    for img in imgs:
        assert f"]({img})" in text and (root / img).stat().st_size > 50_000, img
    assert "<!--" not in text.split("## ")[0]          # the placeholder comment is gone


def test_translated_choices_are_written_back_each_run():
    """After a language switch the browser lost the shown selection of a radio whose option labels
    are translated (seen 2026-11-28 on the live app: "Airfoil Source" and "Angles" showed nothing
    selected, the value itself was kept). Writing the value back each run makes Streamlit send it."""
    src = Path(APP).read_text(encoding="utf-8")
    kept = src[src.index("KEPT_WHEN_HIDDEN = ("):src.index(")", src.index('"domain_kind"'))]
    for k in ("source", "sweep_mode", "flow_mode", "mesh_mode", "domain_kind", "f_camber"):
        assert f'"{k}"' in kept, k
