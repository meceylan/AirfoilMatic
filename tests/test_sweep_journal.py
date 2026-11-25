import re

import pytest

from airfoilmatic.fluent import expression_setup, sweep_journal


def lines_of(text):
    return text.split("\n")


def body_of(text):
    return [l for l in lines_of(text) if not l.startswith("; ") and l]


def test_single_angle_reproduces_tested_lines():
    text = sweep_journal(6, 6, 2, iterations=10, folder="C:/Users/etkin/Desktop/airfoilmatik deneme",
                         prefix="naca0012")
    assert body_of(text) == [
        '/file/set-tui-version "24.2"',
        "/file/confirm-overwrite? no",
        '(display "\\n=== AirfoilMatic: alpha 6.00 deg (1/1) ===\\n")',
        '/define/named-expressions/edit aoa definition "6 [deg]" q',
        "/solve/iterate 10",
        '/file/write-case-data "C:/Users/etkin/Desktop/airfoilmatik deneme/naca0012_aoa_06p00"',
        '(display "\\n=== AirfoilMatic: sweep done ===\\n")',
    ]


def test_edit_line_exact_for_six_degrees():
    assert '/define/named-expressions/edit aoa definition "6 [deg]" q' in lines_of(sweep_journal(6, 6, 1))


def test_custom_expression_name():
    text = sweep_journal(3, 3, 1, expression=" alpha_1 ")
    assert '/define/named-expressions/edit alpha_1 definition "3 [deg]" q' in lines_of(text)


@pytest.mark.parametrize("bad", ["1aoa", "a oa", "aoa()", "a-b", "", "a.b", "ç"])
def test_expression_name_validation(bad):
    with pytest.raises(ValueError) as exc:
        sweep_journal(0, 2, 1, expression=bad)
    assert str(exc.value) == ("Expression name may only contain letters, digits and _ "
                              "and must not start with a digit")


@pytest.mark.parametrize("angle,text", [
    (6, "6"), (-2, "-2"), (0.5, "0.5"), (12.25, "12.25"), (0, "0"), (-0.00001, "0"),
    (-0.5, "-0.5"), (10, "10"), (0.1 + 0.2, "0.3"),
])
def test_compact_angle_format(angle, text):
    j = sweep_journal(angle, angle, 1)
    assert f'definition "{text} [deg]" q' in j
    assert "-0 [deg]" not in j


def test_ordered_angle_blocks():
    body = body_of(sweep_journal(0, 2, 2, iterations=5))[2:]
    kinds = [re.sub(r"alpha .*", "alpha", l) if l.startswith("(display") else l for l in body]
    assert kinds == [
        '(display "\\n=== AirfoilMatic: alpha',
        '/define/named-expressions/edit aoa definition "0 [deg]" q',
        "/solve/iterate 5",
        '(display "\\n=== AirfoilMatic: alpha',
        '/define/named-expressions/edit aoa definition "2 [deg]" q',
        "/solve/iterate 5",
        '/file/write-case-data "airfoilmatic_aoa_02p00"',
        '(display "\\n=== AirfoilMatic: sweep done ===\\n")',
    ]


def test_no_far_field_or_force_vector_lines():
    cmds = body_of(sweep_journal(-4, 8, 4))
    assert not any("pressure-far-field" in l or "force-vector" in l or "report-definitions" in l for l in cmds)


def test_confirm_overwrite_once_after_tui_version_before_first_marker():
    text = sweep_journal(0, 4, 2)
    lines = lines_of(text)
    assert lines.count("/file/confirm-overwrite? no") == 1
    i = lines.index("/file/confirm-overwrite? no")
    assert lines[i - 1] == '/file/set-tui-version "24.2"'
    assert i < next(k for k, l in enumerate(lines) if l.startswith("(display"))
    assert any(l.startswith("; ") and "overwriting a case file" in l and "not been tried" in l for l in lines)


def test_tiny_negative_angle_is_zero_without_sign():
    text = sweep_journal(-0.001, -0.001, 1, save_every=1, prefix="a")
    assert "alpha -0.00" not in text
    assert "a_aoa_m00p00" not in text


def test_negative_zero_rounding_label_in_name():
    text = sweep_journal(-0.004, -0.004, 1, save_every=1, prefix="a")
    assert "alpha 0.00 deg" in text
    assert '"a_aoa_00p00"' in text


def test_step_too_small_gives_name_collision_error():
    with pytest.raises(ValueError, match="Angle step too small: two angles get the same file name"):
        sweep_journal(0, 0.05, 0.001)


def test_dots_in_prefix_become_underscores_in_file_name():
    text = sweep_journal(6, 6, 1, prefix="AirfoilMatic_HQ1.0_12_CGrid")
    assert '"AirfoilMatic_HQ1_0_12_CGrid_aoa_06p00"' in text


def test_non_ascii_folder_rejected():
    with pytest.raises(ValueError, match="Folder must contain only ASCII characters"):
        sweep_journal(0, 2, 1, folder="C:/Users/x/Masaüstü")


def test_prefix_error_message_is_fixed():
    with pytest.raises(ValueError) as exc:
        sweep_journal(0, 2, 1, prefix="bad prefix")
    assert str(exc.value) == "File name prefix may only contain letters, digits and _ . -"


def test_angle_order_and_count():
    text = sweep_journal(-4, 16, 2)
    markers = re.findall(r"alpha (-?\d+\.\d+) deg \((\d+)/(\d+)\)", text)
    assert len(markers) == 11
    angles = [float(m[0]) for m in markers]
    assert angles == sorted(angles)
    assert angles[0] == -4.0 and angles[-1] == 16.0
    assert markers[0][1:] == ("1", "11") and markers[-1][1:] == ("11", "11")
    assert text.count("/define/named-expressions/edit") == 11


def test_save_every_one_writes_every_angle():
    text = sweep_journal(-4, 0, 2, save_every=1, folder="D:/run", prefix="a")
    writes = [l for l in lines_of(text) if l.startswith("/file/write-case-data")]
    assert writes == [
        '/file/write-case-data "D:/run/a_aoa_m04p00"',
        '/file/write-case-data "D:/run/a_aoa_m02p00"',
        '/file/write-case-data "D:/run/a_aoa_00p00"',
    ]


def test_default_writes_once_with_last_angle():
    text = sweep_journal(10, 15, 2.5, folder="D:/run", prefix="a")
    writes = [l for l in lines_of(text) if l.startswith("/file/write-case-data")]
    assert writes == ['/file/write-case-data "D:/run/a_aoa_15p00"']
    assert text.index(writes[0]) < text.index("sweep done")
    assert "12p50" not in text and "10p00" not in text


def writes_of(text):
    return [l.split("_aoa_")[1].rstrip('"') for l in lines_of(text) if l.startswith("/file/write-case-data")]


def test_save_every_k_angles_and_always_the_last():
    # 10 angles (-4 ... 14), every 5th angle -> 5th and 10th
    assert writes_of(sweep_journal(-4, 14, 2, save_every=5)) == ["04p00", "14p00"]
    # 11 angles (-4 ... 16), every 5th -> 5th, 10th and the last (11th)
    assert writes_of(sweep_journal(-4, 16, 2, save_every=5)) == ["04p00", "14p00", "16p00"]
    # every 3rd of 4 angles
    assert writes_of(sweep_journal(0, 6, 2, save_every=3)) == ["04p00", "06p00"]


def test_save_every_zero_or_larger_than_count_saves_only_the_last():
    assert writes_of(sweep_journal(0, 6, 2, save_every=0)) == ["06p00"]
    assert writes_of(sweep_journal(0, 6, 2, save_every=10)) == ["06p00"]


def test_save_written_right_after_its_angle_iterates():
    lines = lines_of(sweep_journal(0, 4, 2, iterations=7, save_every=2))
    i = lines.index('/file/write-case-data "airfoilmatic_aoa_02p00"')
    assert lines[i - 1] == "/solve/iterate 7"
    assert lines[i - 2] == '/define/named-expressions/edit aoa definition "2 [deg]" q'


@pytest.mark.parametrize("bad", [-1, 1.5, "2", None, True])
def test_save_every_validation(bad):
    with pytest.raises(ValueError, match="Save interval must be a whole number of 0 or more"):
        sweep_journal(0, 2, 1, save_every=bad)


def test_save_each_parameter_is_gone():
    with pytest.raises(TypeError):
        sweep_journal(0, 2, 1, save_each=True)


def test_header_explains_save_interval_and_resume():
    header = " ".join(l for l in sweep_journal(-4, 16, 2, save_every=5).splitlines() if l.startswith(";"))
    assert "every 5 angles" in header
    assert "To continue a stopped sweep" in header
    assert "one iteration by hand" in header and "create new file" in header and "Yes" in header
    assert "not tried yet; the" not in header   # tried in Fluent 2024 R2 on 2026-11-25
    assert "upper limit" in header and "Convergence Conditions" in header
    assert "last value of each block" not in header


def test_folder_backslashes_converted_and_trailing_stripped():
    text = sweep_journal(0, 0, 1, save_every=1, folder="C:\\Users\\me\\run\\\\")
    assert '"C:/Users/me/run/airfoilmatic_aoa_00p00"' in text


def test_empty_folder_gives_bare_name():
    assert '/file/write-case-data "airfoilmatic_aoa_00p00"' in lines_of(sweep_journal(0, 0, 1, save_every=1))


@pytest.mark.parametrize("bad", [0, -5, 1.5, "10", None, True])
def test_iterations_validation(bad):
    with pytest.raises(ValueError):
        sweep_journal(0, 2, 1, iterations=bad)


@pytest.mark.parametrize("kwargs", [dict(prefix="my case"), dict(prefix=""), dict(folder='C:/a"b')])
def test_bad_names_rejected(kwargs):
    with pytest.raises(ValueError):
        sweep_journal(0, 2, 1, **kwargs)


def test_angle_arguments_validated():
    with pytest.raises(ValueError):
        sweep_journal(0, 2, 0)
    with pytest.raises(ValueError):
        sweep_journal(5, 2, 1)


def test_removed_parameters_are_gone():
    for kw in ("zones", "lift", "drag"):
        with pytest.raises(TypeError):
            sweep_journal(0, 2, 1, **{kw: "x"})


def test_ascii_only_and_trailing_newline():
    text = sweep_journal(-4, 4, 2, version="1.2.3", save_every=1, folder="a\\b")
    text.encode("ascii")
    assert text.endswith("\n") and not text.endswith("\n\n")
    assert "\r" not in text
    assert "AirfoilMatic 1.2.3 - angle-of-attack sweep journal for Ansys Fluent (2D)" in text
    assert text.startswith("; ")


def test_iterations_in_every_block():
    assert sweep_journal(0, 4, 2, iterations=50).count("/solve/iterate 50") == 3


def test_header_describes_case_requirements():
    header = " ".join(l for l in sweep_journal(-2, 2, 2).splitlines() if l.startswith(";"))
    for needle in ("named expression aoa", "cos(aoa)", "sin(aoa)", "expression report", "at least one iteration",
                   "Ok to overwrite?", "standalone", "Workbench", "File > Read > Journal", "3-angle sweep", "not been tried yet"):
        assert needle in header


def test_expression_setup_reproduces_verified_strings():
    d = expression_setup(density=0.7011, speed=51.025)
    assert d == {
        "flow_x": "cos(aoa)",
        "flow_y": "sin(aoa)",
        "inlet_x": "51.025 [m s^-1]*cos(aoa)",
        "inlet_y": "51.025 [m s^-1]*sin(aoa)",
        "cl": "dot(Force(['wall']), vector(-sin(aoa), cos(aoa), 0)) / "
              "(0.5 * 0.7011 [kg m^-3] * (51.025 [m s^-1])^2 * 1 [m^2])",
        "cd": "dot(Force(['wall']), vector(cos(aoa), sin(aoa), 0)) / "
              "(0.5 * 0.7011 [kg m^-3] * (51.025 [m s^-1])^2 * 1 [m^2])",
        "clconv": "dot(Force(['wall']), vector(-sin(aoa), cos(aoa), 0)) / "
                  "(0.5 * 0.7011 [kg m^-3] * (51.025 [m s^-1])^2 * 1 [m^2]) + 1",
    }


def test_clconv_is_cl_plus_one():
    d = expression_setup("alpha", 1.225, 30, chord=2.0, wall="airfoil")
    assert d["clconv"] == d["cl"] + " + 1"


def test_expression_setup_options_and_validation():
    d = expression_setup("alpha", 1.225, 30, chord=2.0, depth=0.5, wall="airfoil")
    assert d["flow_x"] == "cos(alpha)"
    assert "Force(['airfoil'])" in d["cl"] and "* 1 [m^2]" in d["cl"]
    assert "(30 [m s^-1])^2" in d["cd"]
    for kw in (dict(expression="1a"), dict(wall="a b"), dict(density=0), dict(speed=-1), dict(chord=0),
               dict(depth=float("nan"))):
        with pytest.raises(ValueError):
            expression_setup(**{**dict(density=1.2, speed=10), **kw})
