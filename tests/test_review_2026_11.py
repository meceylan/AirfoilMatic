"""Findings of the November 2026 code review (H1-H6 and the deprecated button argument)."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic import library as lib
from airfoilmatic.geometry import AirfoilError, naca
from airfoilmatic.i18n import tr, tr_error

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")


def start():
    return AppTest.from_file(APP, default_timeout=120).run()


def by_key(at, kind, key):
    found = [w for w in getattr(at, kind) if w.key == key]
    assert found, f"{kind} with key '{key}' not on the page"
    return found[0]


def by_label(at, kind, label):
    found = [w for w in getattr(at, kind) if w.label == label]
    assert found, f"{kind} labelled '{label}' not on the page"
    return found[0]


def switch_language(at, lang_label):
    [r for r in at.radio if r.label == "Dil / Language"][0].set_value(lang_label)
    return at.run()


# ---- H1: Mach-mode temperature must reach the Fluent helper
def test_mach_temperature_change_reaches_fluent_helper():
    at = start()
    by_key(at, "radio", "flow_mode").set_value("mach")
    at = at.run()
    by_key(at, "number_input", "mach_temp").set_value(100.0)
    at = at.run()
    assert not at.exception
    shown = [w for w in at.number_input if w.label == tr("fl_temp", "tr") and w.disabled]
    assert len(shown) == 1 and shown[0].value == pytest.approx(100.0)
    page = " ".join(m.value for m in at.markdown)
    assert "0.1707" not in page and "0.171" not in page


# ---- H2: undashed 6-series names are not NACA 5-digit codes
@pytest.mark.parametrize("q", ["64012", "NACA 64012", "n64012", "63010", "65010", "63015", "61012"])
def test_undashed_six_series_is_not_drawn_as_five_digit(q):
    assert lib.naca_section(q) is None
    assert all(s.source != lib.NACA_FORMULA for s in lib.search(q))


def test_five_digit_starting_with_six_is_refused_with_reason():
    with pytest.raises(AirfoilError) as exc:
        naca("64012")
    assert "6-series" in str(exc.value)
    assert tr_error(exc.value, "tr") != str(exc.value)   # translated in the Turkish UI


@pytest.mark.parametrize("code", ["23012", "23015", "21012", "24012", "25012", "0012", "4412"])
def test_ordinary_naca_codes_still_drawn(code):
    assert lib.naca_section(code) is not None


def test_library_builder_keeps_six_series_files():
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_lib", ROOT / "tools" / "build_airfoil_library.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert not mod.drawn_by_the_app("n64012")
    assert mod.drawn_by_the_app("n23012") and mod.drawn_by_the_app("naca0012")


# ---- H3: quality verdict counts the averages too
@pytest.mark.parametrize("key,val", [("q_sk_avg", 0.96), ("q_oq_avg", 0.05)])
def test_quality_verdict_counts_averages(key, val):
    at = start()
    by_key(at, "number_input", key).set_value(val)
    at = at.run()
    assert not at.exception
    assert not at.success
    assert any(w.value.startswith("Ortalama değer Ansys") for w in at.warning)


# ---- H4: a language switch keeps the Fluent speed and the y+ "used" height
def test_language_switch_keeps_fluent_speed():
    at = start()
    by_label(at, "number_input", tr("fl_speed", "tr")).set_value(55.0)
    at = at.run()
    at = switch_language(at, "English")
    assert by_label(at, "number_input", tr("fl_speed", "en")).value == pytest.approx(55.0)


def test_language_switch_keeps_yplus_used_height():
    at = start()
    by_label(at, "number_input", tr("yplus_used_dy", "tr")).set_value(2.0e-5)
    at = at.run()
    at = switch_language(at, "English")
    assert by_label(at, "number_input", tr("yplus_used_dy", "en")).value == pytest.approx(2.0e-5)


def test_fluent_speed_still_follows_a_new_reynolds_number():
    at = start()
    u1 = by_label(at, "number_input", tr("fl_speed", "tr")).value
    by_key(at, "number_input", "re").set_value(4.0e6)
    at = at.run()
    assert by_label(at, "number_input", tr("fl_speed", "tr")).value == pytest.approx(2 * u1, rel=1e-3)


# ---- H5: inputs survive a mode switch and back
def test_reynolds_survives_velocity_mode_round_trip():
    at = start()
    by_key(at, "number_input", "re").set_value(5.0e5)
    at = at.run()
    by_key(at, "radio", "flow_mode").set_value("vel")
    at = at.run()
    by_key(at, "radio", "flow_mode").set_value("re")
    at = at.run()
    assert by_key(at, "number_input", "re").value == pytest.approx(5.0e5)


def test_growth_survives_mapped_round_trip():
    at = start()
    by_key(at, "number_input", "g_infl").set_value(1.10)
    at = at.run()
    by_key(at, "radio", "mesh_mode").set_value("mapped")
    at = at.run()
    by_key(at, "radio", "mesh_mode").set_value("inflation")
    at = at.run()
    assert by_key(at, "number_input", "g_infl").value == pytest.approx(1.10)


def test_search_query_survives_file_mode_round_trip():
    at = start()
    by_key(at, "text_input", "af_query").set_value("e387")
    at = at.run()
    by_key(at, "radio", "source").set_value("file")
    at = at.run()
    by_key(at, "radio", "source").set_value("search")
    at = at.run()
    assert not at.exception
    assert by_key(at, "text_input", "af_query").value == "e387"


def test_mode_round_trips_show_no_session_state_warning():
    at = start()
    by_key(at, "radio", "flow_mode").set_value("vel")
    at = at.run()
    by_key(at, "radio", "flow_mode").set_value("mach")
    at = at.run()
    texts = " ".join(w.value for w in at.warning)
    assert "Session State API" not in texts and not at.exception


# ---- deprecated argument and README unit
def test_no_use_container_width_in_app():
    assert "use_container_width" not in (ROOT / "app.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", ["README.md", "README.en.md"])
def test_readme_does_not_fix_the_unit_to_metre(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    assert "`Units > Meter` " not in text and "set `Units > Meter` first" not in text
