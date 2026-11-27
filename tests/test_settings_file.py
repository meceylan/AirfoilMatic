"""Save the inputs to a JSON file and load them back (sidebar, "Settings")."""
import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.i18n import ERRORS_TR, tr
from airfoilmatic.settings import SAVED_KEYS, from_json, to_json

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_round_trip_keeps_only_known_inputs():
    state = {"re": 3.0e6, "chord": 0.5, "af_text": "s9104", "domain_kind": "rect", "line_front_axis": False,
             "dice": True, "msh_download": False, "something": 1}
    data = json.loads(to_json(state))
    assert data["inputs"] == {"re": 3.0e6, "chord": 0.5, "af_text": "s9104", "domain_kind": "rect",
                              "line_front_axis": False}
    assert data["app"] == "AirfoilMatic" and "version" in data
    assert from_json(to_json(state)) == data["inputs"]


def test_types_are_checked_and_unknown_keys_dropped():
    text = json.dumps({"app": "AirfoilMatic", "inputs": {"re": "lots", "chord": 2, "xyz": 1, "as_is": True}})
    assert from_json(text) == {"chord": 2.0, "as_is": True}


@pytest.mark.parametrize("text", ["not json", "[1, 2]", json.dumps({"app": "Other", "inputs": {}})])
def test_other_files_are_refused(text):
    with pytest.raises(ValueError) as e:
        from_json(text)
    assert str(e.value) in ERRORS_TR


def test_saved_keys_are_inputs_of_the_app():
    src = Path(APP).read_text(encoding="utf-8")
    for k in SAVED_KEYS:
        assert k == "af_text" or k.startswith("line_") or f'key="{k}"' in src, k


def test_app_saves_and_loads_the_inputs():
    at = AppTest.from_file(APP, default_timeout=240).run()
    [w for w in at.number_input if w.key == "chord"][0].set_value(0.75)
    at = at.run()
    assert any(b.proto.id.endswith("settings_download") for b in at.get("download_button"))
    saved = to_json(dict(at.session_state.filtered_state))
    at = AppTest.from_file(APP, default_timeout=240).run()
    up = [u for u in at.file_uploader if u.key == "settings_file"][0]
    up.upload("airfoilmatic_settings.json", saved.encode(), "application/json")
    at = at.run()
    assert not at.exception
    assert [w for w in at.number_input if w.key == "chord"][0].value == 0.75
    assert any(tr("settings_loaded", "tr")[:15] in s.value for s in at.sidebar.success)
