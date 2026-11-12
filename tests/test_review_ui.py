"""Page-level regressions found in a review of app.py (run with Streamlit's AppTest)."""
import pytest
from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage

from test_app import notes, search_for, selig, start, tr, upload, widget


@pytest.fixture
def download_names(monkeypatch):
    """File names given to st.download_button, in call order (AppTest drops its media store after a run)."""
    names = []
    load = MemoryMediaFileStorage.load_and_get_id

    def spy(self, data, mimetype, kind, filename=None):
        names.append(filename)
        return load(self, data, mimetype, kind, filename)

    monkeypatch.setattr(MemoryMediaFileStorage, "load_and_get_id", spy)
    return names


def test_language_switch_keeps_the_inputs():
    """Widgets without a key got a new identity when their label was translated, so every
    input (chord, domain type, mesh method, ...) went back to its default."""
    at = start()
    widget(at, "number_input", tr("chord", "tr")).set_value(0.5)
    widget(at, "selectbox", tr("domain_type", "tr")).set_value("rect")
    at = at.run()
    widget(at, "number_input", tr("l_top", "tr")).set_value(12.0)
    widget(at, "radio", tr("mesh_method", "tr")).set_value("mapped")
    at = at.run()
    widget(at, "radio", "Dil / Language").set_value("English")
    at = at.run()
    assert not at.exception and not at.error
    assert widget(at, "number_input", tr("chord", "en")).value == 0.5
    assert widget(at, "selectbox", tr("domain_type", "en")).value == "rect"
    assert widget(at, "number_input", tr("l_top", "en")).value == 12.0
    assert widget(at, "radio", tr("mesh_method", "en")).value == "mapped"


def test_language_switch_keeps_the_uploaded_file(download_names):
    at = upload("naca2412.dat", selig())
    widget(at, "radio", "Dil / Language").set_value("English")
    at = at.run()
    assert not at.exception and not at.error
    assert widget(at, "radio", tr("source", "en")).value == "file"
    assert tr("upload_info", "en") not in [i.value for i in at.info]
    assert download_names[-1] == "AirfoilMatic_naca2412_CGrid.txt"


def test_back_after_an_unknown_search_returns_to_the_last_section():
    """With 'xyz' typed after e387, ← skipped e387 and went one section further back."""
    at = search_for(start(), "e387")
    at = search_for(at, "xyz")
    at.button(key="hist_back").click()
    at = at.run()
    assert not at.exception and not at.error
    assert at.selectbox[0].value.id == "e387"


def test_back_is_available_after_an_unknown_first_search():
    at = search_for(start(), "xyz")
    assert not at.button(key="hist_back").disabled
    at.button(key="hist_back").click()
    at = at.run()
    assert not at.exception and not at.error
    assert at.selectbox[0].value.id == "naca4412"


def test_download_name_keeps_the_whole_section_title(download_names):
    """safe_file_stem cut the title at its last dot as if it were an extension:
    "HQ 1.0/12" and "HQ 1.0/8" were both downloaded as AirfoilMatic_HQ1_CGrid.txt."""
    names = []
    for q in ("hq1012", "hq108"):
        at = search_for(start(), q)
        assert not at.exception and not at.error
        names.append(download_names[-1])
    assert names == ["AirfoilMatic_HQ1.0_12_CGrid.txt", "AirfoilMatic_HQ1.0_8_CGrid.txt"]


def test_very_high_reynolds_does_not_crash_the_yplus_box():
    """Re = 1e12: the first cell (5e-11 m) was below the y+ box's min_value of 1e-9 m."""
    at = start()
    widget(at, "number_input", tr("re", "tr")).set_value(1e12)
    at = at.run()
    assert not at.exception


def test_long_chord_at_low_reynolds_does_not_crash_the_fluent_box():
    """Re = 1000 on a 14.9 m chord needs 0.98 mm/s, below the speed box's min_value of 1 mm/s."""
    at = start()
    widget(at, "number_input", tr("chord", "tr")).set_value(14.9)
    widget(at, "number_input", tr("re", "tr")).set_value(1e3)
    at = at.run()
    assert not at.exception


def test_reupload_with_the_same_name_and_size_checks_the_direction_again():
    """The mirror box was keyed by file name and size, so a corrected file with the same name
    and length kept the tick of the reversed one and was turned backwards."""
    reversed_data, fixed_data = selig(transform=lambda x, y: (1.0 - x, y)), selig()
    assert len(reversed_data) == len(fixed_data)
    at = upload("wing.dat", reversed_data)
    assert widget(at, "checkbox", tr("mirror_x", "tr")).value
    at.file_uploader[0].upload("wing.dat", fixed_data, "application/octet-stream")
    at = at.run()
    assert not at.exception and not at.error
    assert not widget(at, "checkbox", tr("mirror_x", "tr")).value
    assert tr("note_reversed", "tr") not in notes(at)
