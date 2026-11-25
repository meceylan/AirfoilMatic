"""Polar from a Fluent report file (Automation tab)."""
import math

import numpy as np
import pytest

from airfoilmatic.polar import guess_columns, polar, polar_csv, read_report


def report_text(blocks, columns=("alfa", "cd", "cl"), start=1000, name="ladson-b-rfile"):
    """A report file like Fluent 2024 R2 writes it. ``blocks`` = [(angle_deg, [(cl, cd), ...]), ...];
    the angle column is in radians, as an expression report of a [deg] expression is."""
    lines = [f'"{name}"', '"Iteration" "alfa etc.."', "(" + " ".join(f'"{c}"' for c in ("Iteration",) + columns) + ")"]
    it = start
    for aoa, values in blocks:
        for cl, cd in values:
            row = {"alfa": math.radians(aoa), "cl": cl, "cd": cd}
            lines.append(" ".join([str(it)] + [repr(row[c]) for c in columns]))
            it += 1
    return ("\n".join(lines) + "\n").encode()


def steady(cl, cd, n=80):
    return [(cl, cd)] * n


def wavy(cl, cd, amp, n=80):
    return [(cl + amp * math.sin(i), cd) for i in range(n)]


def test_reads_the_fluent_header_and_rows():
    rep = read_report(report_text([(-4, steady(-0.42, 0.0064, 3))]))
    assert rep.name == "ladson-b-rfile"
    assert rep.columns == ["Iteration", "alfa", "cd", "cl"]
    assert rep.rows.shape == (3, 4)
    assert rep.rows[0, 0] == 1000


def test_columns_are_found_by_name_whatever_their_order():
    cols = ["Iteration", "cd", "cl", "alfa"]
    assert guess_columns(cols) == dict(angle="alfa", cl="cl", cd="cd")
    assert guess_columns(["Iteration", "aoa-rep", "lift-coef", "drag-coef"])["angle"] == "aoa-rep"
    assert guess_columns(["Iteration", "x", "y"]) == dict(angle=None, cl=None, cd=None)


def test_one_row_per_angle_with_mean_of_last_n():
    data = report_text([(-4, steady(-0.42, 0.0064)), (0, steady(0.0001, 0.0051)), (4, steady(0.42, 0.0063))])
    rows = polar(read_report(data), "alfa", "cl", "cd", last_n=50)
    assert [r.aoa for r in rows] == pytest.approx([-4, 0, 4])
    assert rows[2].cl == pytest.approx(0.42) and rows[2].cd == pytest.approx(0.0063)
    assert rows[2].cl_range == pytest.approx(0.0) and rows[2].status == "steady"
    assert rows[0].iterations == 80
    assert rows[2].ld == pytest.approx(0.42 / 0.0063)


def test_oscillating_angle_is_flagged_and_averaged():
    rows = polar(read_report(report_text([(10, wavy(1.05, 0.014, 0.02))])), "alfa", "cl", "cd", last_n=50)
    r = rows[0]
    assert r.status == "oscillating"
    assert r.cl_range == pytest.approx(0.04, abs=0.002)
    assert abs(r.cl - 1.05) < 0.005   # the mean, not the last value


def test_settled_within_tolerance_is_steady():
    rows = polar(read_report(report_text([(6, wavy(0.628, 0.0079, 1e-5))])), "alfa", "cl", "cd", last_n=50)
    assert rows[0].status == "steady"


def test_block_shorter_than_n_is_marked_short():
    rows = polar(read_report(report_text([(4.25, steady(0.448, 0.0065, 4)), (-4, steady(-0.42, 0.0064))])),
                 "alfa", "cl", "cd", last_n=50)
    short = [r for r in rows if r.aoa == pytest.approx(4.25)][0]
    assert short.status == "short" and short.iterations == 4


def test_repeated_iterations_keep_the_later_lines():
    """A sweep continued from a saved case writes some iteration numbers again."""
    first = report_text([(0, steady(0.5, 0.01, 60))], start=1000).decode()
    again = report_text([(0, steady(0.0001, 0.0051, 60))], start=1030).decode().split("\n", 3)[3]
    rows = polar(read_report((first + again).encode()), "alfa", "cl", "cd", last_n=50)
    assert len(rows) == 1
    assert rows[0].iterations == 90          # 1000 ... 1089, no double counting
    assert rows[0].cl == pytest.approx(0.0001)


def test_angle_run_again_later_uses_the_latest_block():
    data = report_text([(0, steady(0.0002, 0.0052)), (16, wavy(0.4, 0.2, 0.3)), (0, steady(0.0001, 0.0051))])
    rows = polar(read_report(data), "alfa", "cl", "cd", last_n=50)
    assert [r.aoa for r in rows] == pytest.approx([0, 16])
    assert rows[0].cl == pytest.approx(0.0001) and rows[0].repeats == 2


def test_angle_in_degrees_when_asked():
    lines = report_text([(4, steady(0.42, 0.0063))]).decode().split("\n")
    body = [" ".join([p[0], "4.0", p[2], p[3]]) for p in (l.split() for l in lines[3:] if l)]
    data = ("\n".join(lines[:3] + body) + "\n").encode()
    rows = polar(read_report(data), "alfa", "cl", "cd", angle_unit="deg", last_n=50)
    assert rows[0].aoa == pytest.approx(4.0)


def test_csv_has_one_line_per_angle():
    rows = polar(read_report(report_text([(-2, steady(-0.21, 0.0055)), (2, steady(0.21, 0.0054))])),
                 "alfa", "cl", "cd", last_n=50)
    lines = polar_csv(rows).strip().splitlines()
    assert lines[0].startswith("alpha_deg,")
    assert len(lines) == 3 and lines[1].startswith("-2")


def test_alphabetical_columns_do_not_mix_cl_and_cd():
    data = report_text([(4, steady(0.42, 0.0063))], columns=("cl", "alfa", "cd"))
    r = polar(read_report(data), "alfa", "cl", "cd", last_n=50)[0]
    assert r.cl == pytest.approx(0.42) and r.cd == pytest.approx(0.0063)


@pytest.mark.parametrize("data,msg", [
    (b"", "no header"),
    (b"hello\nworld\n", "no header"),
    (b'"r"\n"Iteration" "a"\n("Iteration" "alfa" "cd" "cl")\n', "no data rows"),
])
def test_bad_files_give_clear_errors(data, msg):
    with pytest.raises(ValueError, match=msg):
        read_report(data)


def test_unknown_column_is_an_error():
    rep = read_report(report_text([(0, steady(0.0, 0.005, 3))]))
    with pytest.raises(ValueError, match="not in the report file"):
        polar(rep, "alpha", "cl", "cd")


def test_crlf_and_trailing_blank_lines():
    data = report_text([(2, steady(0.21, 0.0054, 60))]).replace(b"\n", b"\r\n") + b"\r\n\r\n"
    assert polar(read_report(data), "alfa", "cl", "cd", last_n=50)[0].cl == pytest.approx(0.21)


def test_error_messages_are_translated():
    from airfoilmatic.i18n import tr_error
    for data in (b"", b'"r"\n"Iteration" "a"\n("Iteration" "alfa" "cd" "cl")\n'):
        with pytest.raises(ValueError) as exc:
            read_report(data)
        assert tr_error(exc.value, "tr") != str(exc.value)
    rep = read_report(report_text([(0, steady(0.0, 0.005, 3))]))
    with pytest.raises(ValueError) as exc:
        polar(rep, "alpha", "cl", "cd")
    assert tr_error(exc.value, "tr") != str(exc.value)
