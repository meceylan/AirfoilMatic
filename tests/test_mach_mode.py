"""Mach + Reynolds flow input and the pressure-far-field values."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.fluent import mach_state
from airfoilmatic.i18n import tr

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_naca0012_validation_state():
    s = mach_state(0.15, 2.0e6, 15.0, 1.0)
    assert s["speed"] == pytest.approx(51.04, abs=0.01)
    assert s["pressure"] == pytest.approx(57989, abs=2)         # the gauge pressure used in the Fluent run
    assert s["density"] * s["speed"] * 1.0 / s["viscosity"] == pytest.approx(2.0e6)


def test_sea_level_pressure_gives_the_standard_reynolds_number():
    s = mach_state(0.15, 3.4946e6, 15.0, 1.0)    # the Re that standard sea-level pressure gives at M = 0.15, c = 1 m
    assert s["pressure"] == pytest.approx(101325, rel=0.01)


@pytest.mark.parametrize("bad", [(0, 1e6, 15, 1), (0.1, 0, 15, 1), (0.1, 1e6, 15, 0)])
def test_invalid_inputs_are_refused(bad):
    with pytest.raises(ValueError):
        mach_state(*bad)


def test_page_in_mach_mode_lists_the_far_field_values():
    at = AppTest.from_file(APP, default_timeout=120).run()
    [r for r in at.radio if r.key == "flow_mode"][0].set_value("mach")
    at = at.run()
    assert not at.exception and not at.error
    html = " ".join(m.value for m in at.markdown)
    assert "57989" in html and tr("fl_ff_pressure", "tr") in html
    caps = [c.value for c in at.caption]
    assert any("57989" in c for c in caps)
