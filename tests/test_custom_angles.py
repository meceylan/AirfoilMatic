"""Angle sweep from the user's own list of angles (e.g. 1.3, 2.8, 6.8), next to the even range."""
import math
import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.fluent import alpha_sweep, angle_rows, parse_angles, sweep_journal
from airfoilmatic.i18n import ERRORS_TR, tr

APP = str(Path(__file__).resolve().parents[1] / "app.py")

DECIMAL = "Use a dot for decimals (1.5) and separate angles with a space, ; or a comma and a space"
NOT_NUMBER = "Angles must be numbers, separated by a space, ; or a comma"
EMPTY = "Enter at least one angle"
RANGE = "Angles must be between -180 and 180 degrees"
SAME_NAME = "Two angles get the same file name: keep angles at least 0.01° apart"


@pytest.mark.parametrize("text, angles", [
    ("1.3, 2.8, 6.8", [1.3, 2.8, 6.8]),
    ("1.3 2.8 6.8", [1.3, 2.8, 6.8]),
    ("1.3;2.8; 6.8", [1.3, 2.8, 6.8]),
    ("6.8, 1.3, 2.8, 1.3", [1.3, 2.8, 6.8]),       # sorted, repeats dropped
    ("  -4,-2, 0 ,4.01 ", [-4.0, -2.0, 0.0, 4.01]),
    ("-0", [0.0]),
])
def test_parse_angles(text, angles):
    assert parse_angles(text) == angles


def test_parse_angles_never_gives_negative_zero():
    assert math.copysign(1, parse_angles("-0")[0]) == 1


@pytest.mark.parametrize("text, msg", [
    ("", EMPTY), ("  ,; ", EMPTY),
    ("1,3", DECIMAL), ("0,2,4", DECIMAL), ("1.3, 2,8", DECIMAL),
    ("abc", NOT_NUMBER), ("1.3, x", NOT_NUMBER), ("nan", NOT_NUMBER), ("inf", NOT_NUMBER), ("1e400", NOT_NUMBER),
    ("190", RANGE), ("-181", RANGE),
])
def test_parse_angles_rejects(text, msg):
    with pytest.raises(ValueError, match=re.escape(msg)):
        parse_angles(text)


def test_too_many_angles():
    with pytest.raises(ValueError, match=r"Too many angles \(more than 361\)"):
        parse_angles(" ".join(str(i / 10) for i in range(362)))


def test_angle_rows_match_the_even_sweep():
    even = alpha_sweep(-2, 4, 3, 51.04)
    own = angle_rows([-2, 1, 4], 51.04)
    assert own == even


def test_journal_from_a_list():
    text = sweep_journal(None, None, None, angles=[1.3, 2.8, 6.8], iterations=500)
    assert 'definition "1.3 [deg]"' in text and 'definition "2.8 [deg]"' in text
    assert 'definition "6.8 [deg]"' in text
    assert text.count("/solve/iterate 500") == 3
    assert "Angles: 1.3, 2.8, 6.8 (own list), count 3." in text
    assert "airfoilmatic_aoa_06p80" in text and "(3/3)" in text


def test_journal_list_with_two_angles_on_one_file_name():
    with pytest.raises(ValueError, match=re.escape(SAME_NAME)):
        sweep_journal(None, None, None, angles=[1.301, 1.302])


def test_new_errors_have_turkish_text():
    for msg in (DECIMAL, NOT_NUMBER, EMPTY, RANGE, SAME_NAME):
        assert msg in ERRORS_TR


# ---------------------------------------------------------------- app
def start():
    return AppTest.from_file(APP, default_timeout=120).run()


def widget(at, kind, key):
    return [w for w in getattr(at, kind) if w.key == key][0]


def page_text(at):
    return " ".join(m.value for m in at.markdown) + " ".join(str(d.value) for d in at.dataframe)


def own_list(at, text):
    widget(at, "radio", "sweep_mode").set_value("list")
    at = at.run()
    widget(at, "text_input", "sweep_list").set_value(text)
    return at.run()


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_mode_radio_has_both_labels(lang):
    at = start()
    if lang == "en":
        [r for r in at.radio if r.label == "Dil / Language"][0].set_value("English")
        at = at.run()
    mode = widget(at, "radio", "sweep_mode")
    assert mode.label == tr("sweep_mode", lang)
    assert mode.options == [tr("sweep_mode_range", lang), tr("sweep_mode_list", lang)]


def test_own_list_gives_table_and_journal():
    at = own_list(start(), "1.3, 2.8, 6.8")
    assert not at.exception and not at.error
    auto = at.tabs[2]
    assert "sweep_from" not in {w.key for w in auto.number_input}
    text = page_text(at)
    assert "1.3" in text and "2.8" in text and "6.8" in text
    assert any(el.proto.id.endswith("jou_download") for el in at.get("download_button"))


def test_own_list_with_a_decimal_comma_shows_a_turkish_error():
    at = own_list(start(), "1,3")
    assert not at.exception
    assert any(ERRORS_TR[DECIMAL] in e.value for e in at.error)
    assert not any(el.proto.id.endswith("jou_download") for el in at.get("download_button"))


def test_range_inputs_kept_after_trying_the_list():
    at = start()
    widget(at, "number_input", "sweep_from").set_value(-6.0)
    at = own_list(at.run(), "1.3")
    widget(at, "radio", "sweep_mode").set_value("range")
    at = at.run()
    assert widget(at, "number_input", "sweep_from").value == -6.0
    widget(at, "radio", "sweep_mode").set_value("list")
    at = at.run()
    assert widget(at, "text_input", "sweep_list").value == "1.3"
