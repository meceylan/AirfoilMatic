"""Findings of the November 2026 code review (H1-H6 and the deprecated button argument)."""
import re
from pathlib import Path

import numpy as np

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
    at.session_state["af_text"] = "e387"
    at = at.run()
    by_key(at, "radio", "source").set_value("file")
    at = at.run()
    by_key(at, "radio", "source").set_value("search")
    at = at.run()
    assert not at.exception
    assert at.session_state["af_text"] == "e387"


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


# ================================================================ groups 2-4 of the review
from airfoilmatic import i18n
from airfoilmatic.fluent import expression_setup, mach_state, rarefaction
from airfoilmatic.geometry import chord_line_angle, naca4, parse_airfoil_file


def selig_text(af):
    """A Selig file of an airfoil: upper surface TE -> LE, then lower LE -> TE."""
    pts = list(zip(af.xu[::-1], af.yu[::-1])) + list(zip(af.xl[1:], af.yl[1:]))
    return ("test\n" + "\n".join(f"{x:.6f} {y:.6f}" for x, y in pts)).encode()


# ---- velocity-inlet lines in the journal setup
def test_expression_setup_gives_velocity_inlet_components():
    d = expression_setup(density=1.225, speed=51.04)
    assert d["inlet_x"] == "51.04 [m s^-1]*cos(aoa)"
    assert d["inlet_y"] == "51.04 [m s^-1]*sin(aoa)"


def test_setup_block_lists_velocity_inlet_lines():
    at = start()
    code = " ".join(c.value for c in at.code)
    assert "[m s^-1]*cos(aoa)" in code and "[m s^-1]*sin(aoa)" in code
    assert tr("jou_setup_inlet_x", "tr") in code


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_journal_texts_are_current(lang):
    note = tr("jou_note", lang, iterations=1000, expr="aoa")
    for stale in ("desteklenmiyor", "not supported yet", "dört satır", "four lines"):
        assert stale not in note
    assert "pressure-far-field" not in tr("jou_title", lang)
    assert "51.025" not in tr("jou_setup_note", lang)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_profile_help_points_to_the_sidebar_unit(lang):
    text = tr("profile_help", lang)
    assert "aşağıda seçtiğiniz" not in text and "chosen below" not in text and "aşağıdaki birim" not in text
    assert "profile_unit" not in i18n.STRINGS


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_flow_help_texts_do_not_claim_one_mode(lang):
    assert "entered separately" not in tr("fl_temp_help", lang)
    assert "ayrıca girilir" not in tr("fl_temp_help", lang)


def test_changelog_does_not_call_the_far_field_pressure_the_validated_run():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "the value used in the NACA 0012 run" not in text
    assert "NACA 0012 koşusunda kullanılan değer" not in text


@pytest.mark.parametrize("name,words", [("README.md", ("SpaceClaim", "SolidWorks", "Mach", "mm")),
                                        ("README.en.md", ("SpaceClaim", "SolidWorks", "Mach", "mm"))])
def test_readme_feature_list_is_complete(name, words):
    text = (ROOT / name).read_text(encoding="utf-8")
    features = text.split("\n## ")[1]   # first section after the title
    for w in words:
        assert w in features, w


# ---- CI matrix
def test_ci_runs_windows_and_the_lowest_streamlit():
    wf = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "windows-latest" in wf and "ubuntu-latest" in wf
    lowest = re.search(r"streamlit>=([\d.]+)", (ROOT / "requirements.txt").read_text(encoding="utf-8")).group(1)
    assert f'streamlit=={lowest}.*' in wf   # CI tests the lowest version requirements.txt allows


def test_lowest_streamlit_has_the_apptest_upload_accessor():
    # AppTest.file_uploader, used by the upload tests, came with Streamlit 1.56
    lowest = re.search(r"streamlit>=([\d.]+)", (ROOT / "requirements.txt").read_text(encoding="utf-8")).group(1)
    assert tuple(int(x) for x in lowest.split(".")) >= (1, 56)


# ---- tilt and camber measured from the true chord line
@pytest.mark.parametrize("code", ["4412", "23012", "6409"])
def test_untilted_cambered_files_are_not_reported_tilted(code):
    af = parse_airfoil_file(selig_text(naca(code)), 1.0)
    assert abs(chord_line_angle(af)) < 0.3


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_tilt_note_warns_about_strongly_cambered_noses(lang):
    # NACA 9940 read back from a file shows about 2 deg although it is not tilted
    assert "9940" in tr("note_tilt", lang, angle=1.8)


def test_tilted_file_is_still_reported():
    base = naca("0012")
    a = np.radians(3.0)
    rot = lambda x, y: (x * np.cos(a) + y * np.sin(a), -x * np.sin(a) + y * np.cos(a))
    xu, yu = rot(base.xu, base.yu)
    xl, yl = rot(base.xl, base.yl)
    pts = list(zip(xu[::-1], yu[::-1])) + list(zip(xl[1:], yl[1:]))
    af = parse_airfoil_file(("t\n" + "\n".join(f"{x:.6f} {y:.6f}" for x, y in pts)).encode(), 1.0)
    assert chord_line_angle(af) == pytest.approx(3.0, abs=0.2)


def test_library_camber_measured_from_chord_line():
    s = {x.id: x for x in lib.library()}
    assert s["ag38"].camber > 0.015 and s["ag38"].xc < 0.6
    assert s["sc20712"].camber > 0.015 and s["sc20712"].xc < 0.95


# ---- thin-air warning in Mach mode
def test_rarefaction_flags_near_vacuum_only():
    thin = mach_state(0.8, 1.0e3, 15.0, 1.0)
    normal = mach_state(0.15, 2.0e6, 15.0, 1.0)
    assert rarefaction(thin, 15.0, 1.0) > 1e-3
    assert rarefaction(normal, 15.0, 1.0) < 1e-6


def test_mach_mode_warns_for_near_vacuum():
    at = start()
    by_key(at, "radio", "flow_mode").set_value("mach")
    at = at.run()
    by_key(at, "number_input", "mach_in").set_value(0.8)
    by_key(at, "number_input", "re").set_value(1.0e3)
    at = at.run()
    assert tr("warn_rarefied", "tr").split("{")[0][:30] in " ".join(w.value for w in at.warning)


# ---- small ones
def test_symmetric_code_with_camber_position_is_refused():
    with pytest.raises(AirfoilError):
        naca4("0312")
    naca4("0012")


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_not_found_mentions_unsupported_codes(lang):
    text = tr("not_found", lang, q="23112")
    assert ("refleks" in text) if lang == "tr" else ("reflexed" in text)


def test_colon_not_allowed_in_journal_prefix():
    from airfoilmatic.fluent import sweep_journal
    with pytest.raises(ValueError):
        sweep_journal(0, 2, 1, prefix="a:b")


def test_mach_state_error_is_translated():
    with pytest.raises(ValueError) as exc:
        mach_state(0.0, 2e6, 15.0, 1.0)
    assert tr_error(exc.value, "tr") != str(exc.value)


# ---- library builder: selection size and the symmetric 6-series classics
def _builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_lib2", ROOT / "tools" / "build_airfoil_library.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("target", [200, 300, 500, 137])
def test_builder_quotas_add_up_to_the_target(target):
    b = _builder()
    q = b.quotas(target)
    assert sum(q.values()) == target
    assert set(q) == {k for k, *_ in b.FAMILIES}
    if target == 200:
        assert q == {k: n for k, _, _, n in b.FAMILIES}


def test_builder_wants_the_symmetric_six_series_classics():
    assert {"n64012", "n64015"} <= set(_builder().WANTED["naca"])


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_save_help_gives_the_tried_resume_recipe(lang):
    text = tr("jou_save_every_help", lang)
    assert ("elle" in text) if lang == "tr" else ("by hand" in text)
    assert "Yes" in text and "denenmedi" not in text and "not tried" not in text
