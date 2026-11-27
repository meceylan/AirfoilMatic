"""Inflation-mode sizes that the app derives from the inputs (moved from app.py to mesh.py).

TE surface element: at least 0.003c and 1.5x the last inflation layer (Ansys 2024 R2 failed at a
sharp TE whenever the TE element was smaller than the last layer: NACA 0012, Re 2e6, 3 mm TE vs
4.3 mm last layer failed, ~5.8 mm worked). Defeature Size = smallest element / 50 and Curvature
Min Size = smallest / 5, both rounded to one significant digit; a blunt TE's face counts with a
quarter of its height.
"""
import pytest

from airfoilmatic.mesh import FAR_FIELD_SIZE, INFL_MIN_TE, INFL_TE_FACTOR, inflation_sizes, plan_inflation


def test_constants_kept():
    assert (INFL_MIN_TE, INFL_TE_FACTOR, FAR_FIELD_SIZE) == (0.003, 1.5, 0.5)


def test_sharp_te_takes_one_and_a_half_last_layers():
    infl = plan_inflation(2e6, 1.0, y_plus=1.0, growth=1.15, coverage=1.5)     # last layer 4.34 mm
    s = inflation_sizes(infl, ds_le=0.001, ds_te=0.001, chord=1.0)
    assert s.ds_te == pytest.approx(1.5 * infl.last_layer)
    assert s.smallest == pytest.approx(0.001)
    assert s.defeature == 2e-05 and s.curvature_min == 2e-04
    assert s.far_field == 0.5


def test_minimum_te_element_and_chord_scaling():
    infl = plan_inflation(1e5, 2.0, y_plus=1.0, growth=1.2, coverage=1.0)
    s = inflation_sizes(infl, ds_le=0.0005, ds_te=0.0001, chord=2.0)
    assert s.ds_te == pytest.approx(max(0.003, 1.5 * infl.last_layer / 2.0))
    assert s.smallest == pytest.approx(0.0005 * 2.0)
    assert s.far_field == 1.0


def test_blunt_te_face_counts():
    infl = plan_inflation(2e6, 1.0, y_plus=1.0, growth=1.15, coverage=1.5)
    s = inflation_sizes(infl, ds_le=0.001, ds_te=0.001, chord=1.0, te_gap=0.002)
    assert s.smallest == pytest.approx(0.0005)
    assert s.defeature == 1e-05 and s.curvature_min == 1e-04


def test_app_no_longer_holds_these_rules():
    from pathlib import Path
    text = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    for name in ("INFL_MIN_TE =", "INFL_TE_FACTOR =", "FAR_FIELD_SIZE =", "smallest / 50", "smallest / 5"):
        assert name not in text, name
