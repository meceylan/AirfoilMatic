"""Warnings and notes added after the engineering audit (V0.6.5)."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.fluent import air_density, sutherland_viscosity, speed_of_sound
from airfoilmatic.i18n import tr

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def start():
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception
    return at


def box(at, label):
    return [w for w in at.number_input if w.label == label][0]


def texts(at):
    return [w.value for w in list(at.warning) + list(at.caption)]


def test_sea_level_air_properties_match_the_standard_atmosphere():
    assert air_density(15.0) == pytest.approx(1.2250, abs=2e-4)
    assert sutherland_viscosity(15.0) == pytest.approx(1.7894e-5, rel=2e-3)
    assert sutherland_viscosity(50.0) > sutherland_viscosity(15.0)
    assert air_density(50.0) < air_density(15.0)
    assert speed_of_sound(15.0) == pytest.approx(340.29, abs=0.01)


def test_no_new_warning_at_the_defaults():
    at = start()
    for key in ("warn_yplus_high", "warn_coverage_low", "warn_re_high"):
        assert tr(key, "tr") not in texts(at)


def test_high_yplus_warns_for_transition_sst():
    at = start()
    box(at, tr("y_plus", "tr")).set_value(5.0)
    at = at.run()
    assert not at.exception and tr("warn_yplus_high", "tr") in texts(at)


def test_thin_inflation_coverage_warns():
    at = start()
    box(at, tr("coverage", "tr")).set_value(0.75)
    at = at.run()
    assert not at.exception and tr("warn_coverage_low", "tr") in texts(at)


def test_reynolds_above_1e9_warns():
    at = start()
    box(at, tr("re", "tr")).set_value(2.0e9)
    at = at.run()
    assert not at.exception and tr("warn_re_high", "tr") in texts(at)


def test_other_temperature_shows_density_and_viscosity_suggestion():
    at = start()
    box(at, tr("fl_temp", "tr")).set_value(50.0)
    at = at.run()
    assert not at.exception
    assert any("50 °C" in x and "Sutherland" in x for x in texts(at))
