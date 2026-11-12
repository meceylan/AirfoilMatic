"""V0.7.0: domain sizes in chords, temperature for Mach, free-stream turbulence decay, alpha sweep."""
import math

import numpy as np
import pytest

from airfoilmatic import fluent
from airfoilmatic.fluent import (alpha_sweep, decayed_tu, inlet_tu_for, max_reachable_tu, speed_of_sound,
                                 BETA_SST, BETA_STAR)
from airfoilmatic.i18n import tr
from test_app import start, widget


# ------------------------------------------------------------------ speed of sound
def test_speed_of_sound_matches_the_old_constant_at_15_degrees():
    assert speed_of_sound(15.0) == pytest.approx(fluent.SPEED_OF_SOUND, abs=0.01)
    assert speed_of_sound(-56.5) == pytest.approx(295.07, abs=0.05)   # ISA at 11 km
    with pytest.raises(ValueError):
        speed_of_sound(-300.0)


# ------------------------------------------------------------------ turbulence decay
def _integrate(tu0, re_x, vr, steps=200000):
    """Direct integration of dk/dt = -b* k w, dw/dt = -b w^2 in non-dimensional form
    (U = 1, x = c = 1, nu = 1/Re_x), the reference for the closed form."""
    nu = 1.0 / re_x
    k = 1.5 * tu0**2
    w = k / (nu * vr)
    dt = 1.0 / steps
    for _ in range(steps):   # RK2
        k1, w1 = -BETA_STAR * k * w, -BETA_SST * w * w
        km, wm = k + 0.5 * dt * k1, w + 0.5 * dt * w1
        k, w = k + dt * (-BETA_STAR * km * wm), w + dt * (-BETA_SST * wm * wm)
    return math.sqrt(2.0 * k / 3.0)


@pytest.mark.parametrize("tu0, re_x, vr", [(0.01, 3e7, 10), (0.01, 3e7, 100), (0.002, 1e6, 10), (0.05, 5e5, 1)])
def test_decay_closed_form_matches_the_k_omega_equations(tu0, re_x, vr):
    assert decayed_tu(tu0, re_x, vr) == pytest.approx(_integrate(tu0, re_x, vr), rel=1e-3)


def test_no_distance_or_huge_viscosity_ratio_means_no_decay():
    assert decayed_tu(0.01, 0.0, 10) == pytest.approx(0.01)
    assert decayed_tu(0.01, 3e7, 1e12) == pytest.approx(0.01, rel=1e-4)


def test_validation_case_numbers():
    """Re 2e6, inlet 15c ahead of the 0.3c split -> 14.7c to the LE. 1% at the inlet keeps
    only about 0.14% (ratio 10) or 0.43% (ratio 100) at the airfoil."""
    re_x = 2e6 * 14.7
    assert 100 * decayed_tu(0.01, re_x, 10) == pytest.approx(0.139, abs=0.003)
    assert 100 * decayed_tu(0.01, re_x, 100) == pytest.approx(0.432, abs=0.005)


@pytest.mark.parametrize("goal", [0.0005, 0.001, 0.003])
def test_inlet_tu_for_is_the_inverse(goal):
    re_x, vr = 3e7, 100
    tu_in = inlet_tu_for(goal, re_x, vr)
    assert decayed_tu(tu_in, re_x, vr) == pytest.approx(goal, rel=1e-6)


def test_unreachable_goal_gives_none_and_the_maximum_is_the_peak():
    re_x, vr = 3e7, 10
    peak = max_reachable_tu(re_x, vr)
    grid = np.linspace(1e-4, 0.5, 20000)
    assert peak == pytest.approx(max(decayed_tu(t, re_x, vr) for t in grid), rel=1e-4)
    assert inlet_tu_for(1.01 * peak, re_x, vr) is None
    assert inlet_tu_for(0.99 * peak, re_x, vr) is not None


# ------------------------------------------------------------------ alpha sweep
def test_alpha_sweep_includes_both_ends_and_unit_vectors():
    rows = alpha_sweep(-4, 16, 2, 30.0)
    assert [r["aoa"] for r in rows] == list(range(-4, 17, 2))
    for r in rows:
        a = math.radians(r["aoa"])
        assert r["ux"] == pytest.approx(30 * math.cos(a)) and r["uy"] == pytest.approx(30 * math.sin(a))
        d, l = np.array(r["drag"]), np.array(r["lift"])
        assert np.linalg.norm(d) == pytest.approx(1) and np.dot(d, l) == pytest.approx(0, abs=1e-12)
    assert [r["aoa"] for r in alpha_sweep(0, 1, 0.3, 1)] == [0, 0.3, 0.6, 0.9]
    assert [r["aoa"] for r in alpha_sweep(0, 0.3, 0.1, 1)] == [0, 0.1, 0.2, 0.3]


@pytest.mark.parametrize("args", [(0, 10, 0), (5, 0, 1), (0, 1000, 0.1)])
def test_alpha_sweep_rejects_bad_input(args):
    with pytest.raises(ValueError):
        alpha_sweep(*args, 10.0)


# ------------------------------------------------------------------ the page
def test_domain_scales_with_the_chord():
    """A 10 m chord used to get a 15 m inlet radius (1.5c); now it gets 15c = 150 m."""
    at = start()
    widget(at, "number_input", tr("chord", "tr")).set_value(10.0)
    at = at.run()
    assert not at.exception and not at.error
    assert any(tr("domain_in_m", "tr", r=150.0, w=200.0) == c.value for c in at.sidebar.caption)


def test_fluent_helper_shows_decay_mach_and_sweep():
    at = start()
    assert not at.exception and not at.error
    text = "\n".join(m.value for m in at.markdown)
    assert tr("tu_at_le", "tr") in text and tr("fl_sound", "tr") in text and "340.29 m/s" in text
    assert any(c.label == tr("sweep_csv", "tr") for c in at.get("download_button"))
    widget(at, "number_input", tr("fl_temp", "tr")).set_value(-56.5)
    at = at.run()
    assert "295.07 m/s" in "\n".join(m.value for m in at.markdown)


def test_bad_sweep_shows_one_error_not_a_traceback():
    at = start()
    widget(at, "number_input", tr("sweep_to", "tr")).set_value(-10.0)
    at = at.run()
    assert not at.exception
    assert len(at.error) == 1


@pytest.mark.parametrize("tu_in, row", [(0.2, (0.12, 0.19, 0.20)), (0.5, (0.14, 0.35, 0.48)), (1.0, (0.14, 0.43, 0.84))])
def test_matches_the_table_used_in_the_naca0012_validation(tu_in, row):
    """Table of the NACA 0012 validation setup (inlet 14.7c ahead of the LE, Re 2e6)."""
    got = tuple(round(100 * decayed_tu(tu_in / 100, 2e6 * 14.7, vr), 2) for vr in (10, 100, 1000))
    assert got == row


def test_zero_angle_prints_no_negative_zero():
    r = alpha_sweep(0, 0, 1, 10.0)[0]
    assert f"{r['lift'][0]:.6f}" == "0.000000"
