"""Regression tests for the mesh / Fluent helper review."""
import pytest

from airfoilmatic.mesh import geometric_length, n_for_growth


@pytest.mark.parametrize("r, n", [(1.1, 3), (1.1, 10), (1.2, 2), (1.3, 4), (1.05, 5)])
def test_n_for_growth_exact_length_needs_no_extra_division(r, n):
    """A length that n cells exactly fill must give n divisions, not n + 1
    (ceil of a log ratio that came out as n + 1e-15)."""
    L = geometric_length(1e-5, r, n)
    assert n_for_growth(L, 1e-5, r) == n


def test_n_for_growth_uniform_exact_length():
    # three cells of 0.1: 3 * 0.1 / 0.1 = 3.0000000000000004 in floating point
    assert n_for_growth(geometric_length(0.1, 1.0, 3), 0.1, 1.0) == 3


def test_inflation_growth_rate_shown_with_all_entered_decimals():
    """The growth input takes three decimals (format %.3f). The layer count, total and
    last layer are computed with the entered value, so the Growth Rate row the user
    types into Ansys must show it unrounded: 1.105 used to be shown as 1.1."""
    from test_app import start, table_text, widget
    from airfoilmatic.i18n import tr
    at = start()
    widget(at, "number_input", tr("growth", "tr")).set_value(1.105)
    at = at.run()
    assert not at.exception and not at.error
    assert "<td>Growth Rate</td><td>1.105</td>" in table_text(at)
