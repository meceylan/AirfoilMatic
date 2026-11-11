"""The Streamlit app itself, run headless with Streamlit's AppTest.

These tests click through app.py the way a user would and fail on any uncaught
exception, so a crash in the page cannot slip past the core-module tests.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.i18n import tr

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def start(lang="tr"):
    at = AppTest.from_file(APP, default_timeout=120).run()
    if lang == "en":
        widget(at, "radio", "Dil / Language").set_value("English")
        at = at.run()
    return at


def widget(at, kind, label):
    found = [w for w in getattr(at, kind) if w.label == label]
    assert found, f"{kind} '{label}' not on the page"
    return found[0]


def labels(at, kind):
    return [w.label for w in getattr(at, kind)]


def table_text(at):
    return "\n".join(m.value for m in at.markdown)


@pytest.mark.parametrize("lang", ["tr", "en"])
@pytest.mark.parametrize("domain", ["c_grid", "rect"])
@pytest.mark.parametrize("mode", ["inflation", "mapped"])
def test_app_runs_in_every_mode(lang, domain, mode):
    at = start(lang)
    at.selectbox[0].set_value(domain)
    at = at.run()
    widget(at, "radio", tr("mesh_method", lang)).set_value(mode)
    at = at.run()
    assert not at.exception and not at.error


def test_reynolds_below_range_shows_an_error_instead_of_crashing():
    """Velocity input: U = 0.01 m/s on a 1 m chord is Re = 685, below the range of the
    skin-friction correlation. The y+ correction box used to raise an uncaught ValueError."""
    at = start()
    widget(at, "radio", tr("flow_input", "tr")).set_value("vel")
    at = at.run()
    widget(at, "number_input", tr("velocity", "tr")).set_value(0.01)
    at = at.run()
    assert not at.exception
    assert len(at.error) == 1
    assert tr("yplus_used_dy", "tr") not in labels(at, "number_input")   # nothing to correct without a plan


def test_wake_growth_input_only_in_mapped_mode():
    """In inflation mode the wake axis ends at the far-field size, which fixes its
    progression; the growth input had no effect on the table."""
    at = start()
    assert tr("wake_growth", "tr") not in labels(at, "number_input")
    assert tr("ds_te", "tr") in labels(at, "number_input")
    widget(at, "radio", tr("mesh_method", "tr")).set_value("mapped")
    at = at.run()
    assert tr("wake_growth", "tr") in labels(at, "number_input")


def test_low_reynolds_inflation_table_names_the_split_line_as_small_end():
    at = start()
    widget(at, "number_input", tr("re", "tr")).set_value(1.0e5)
    at = at.run()
    assert not at.exception and not at.error
    small_ends = [row[tr("col_small", "tr")] for df in at.dataframe for row in df.value.to_dict("records")]
    assert small_ends == [tr("end_le", "tr"), tr("end_split", "tr"), tr("end_te", "tr")]


def test_fluent_table_lists_the_viscosity_used_for_reynolds():
    at = start()
    widget(at, "radio", tr("flow_input", "tr")).set_value("vel")
    at = at.run()
    widget(at, "number_input", tr("viscosity", "tr")).set_value(3.126e-5)
    at = at.run()
    assert not at.exception
    assert tr("fl_visc", "tr") in table_text(at) and "3.126e-05 Pa·s" in table_text(at)


# ------------------------------------------------------------------ uploaded files

import numpy as np

from airfoilmatic.geometry import naca


def selig(code="2412", n=61, transform=lambda x, y: (x, y), fmt="{:.6f} {:.6f}"):
    a = naca(code, n_points=n)
    x, y = transform(np.concatenate([a.xu[::-1], a.xl[1:]]), np.concatenate([a.yu[::-1], a.yl[1:]]))
    return "\n".join(fmt.format(p, q) for p, q in zip(x, y)).encode()


def upload(name, data, lang="tr"):
    at = start(lang)
    widget(at, "radio", tr("source", lang)).set_value("file")
    at = at.run()
    at.file_uploader[0].upload(name, data, "application/octet-stream")
    return at.run()


def notes(at):
    return [m.value for m in list(at.info) + list(at.warning)]


def test_upload_plain_file():
    at = upload("naca2412.dat", selig())
    assert not at.exception and not at.error
    assert not widget(at, "checkbox", tr("mirror_x", "tr")).value
    assert notes(at) == []


def test_upload_reversed_file_is_mirrored_and_says_so():
    at = upload("backwards.dat", selig(transform=lambda x, y: (1.0 - x, y)))
    assert not at.exception and not at.error
    box = widget(at, "checkbox", tr("mirror_x", "tr"))
    assert box.value
    assert tr("note_mirrored", "tr") in notes(at)
    box.uncheck()                       # the user insists on the file's direction
    at = at.run()
    assert not at.exception
    assert tr("note_reversed", "tr") in notes(at)


def test_upload_coarse_file_warns():
    at = upload("coarse.dat", selig(n=7))
    assert not at.exception and not at.error
    assert tr("note_few_points", "tr", n=7, need=12) in notes(at)


def test_upload_tilted_file_reports_the_angle():
    c, s = np.cos(np.radians(5.0)), np.sin(np.radians(5.0))
    at = upload("tilted.dat", selig(transform=lambda x, y: (x * c + y * s, -x * s + y * c)))
    assert not at.exception and not at.error
    assert any("+5.0°" in n for n in notes(at))


def test_upload_excel_csv_with_decimal_commas():
    at = upload("Ölçü kanadı.csv", selig(fmt="{:.6f};{:.6f}").replace(b".", b","))
    assert not at.exception and not at.error


@pytest.mark.parametrize("data", [b"", b"NACA 0012\n", bytes(range(256)) * 8,
                                  b"t,value\n" + b"\n".join(b"%d,%d" % (i, i * i) for i in range(50))])
def test_upload_of_something_else_shows_one_error(data):
    at = upload("other.dat", data)
    assert not at.exception
    assert len(at.error) == 1
