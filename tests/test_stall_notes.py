"""Lessons of the 2026-11-25 stall study (Fluent 2024 R2, NACA 0012, SST k-ω): a steady solution that
oscillates is not always stall (URANS at 16.99° settled to attached flow), full-turbulence SST gives
stall late, and a transient report file counts time steps, not iterations."""
import math
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from airfoilmatic.i18n import tr
from airfoilmatic.polar import is_transient, read_report
from _docs import doc_text

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")


def report_text(first="Iteration", aoa=16.99, n=120, amp=0.0):
    lines = ['"urans-rfile"', f'"{first}" "alfa etc.."', f'("{first}" "alfa" "cd" "cl" "flow-time")']
    for i in range(n):
        lines.append(f"{i} {math.radians(aoa)!r} 0.0453 {1.4585 + amp * math.sin(i)!r} {i * 2e-4!r}")
    return ("\n".join(lines) + "\n").encode()


def test_transient_report_is_recognised():
    assert is_transient(read_report(report_text("Time Step")))
    assert not is_transient(read_report(report_text("Iteration")))


def upload(data):
    at = AppTest.from_file(APP, default_timeout=120).run()
    [u for u in at.file_uploader if u.key == "polar_file"][0].upload("urans.out", data, "text/plain")
    return at.run()


def page(at):
    return (" ".join(m.value for m in at.markdown) + " ".join(c.value for c in at.caption)
            + " ".join(str(list(d.value.columns)) for d in at.dataframe))


def test_transient_report_table_counts_time_steps():
    at = upload(report_text("Time Step"))
    assert not at.exception and not at.error
    text = page(at)
    assert tr("polar_steps", "tr") in text
    assert tr("polar_iters", "tr") not in text
    assert any(c.value == tr("polar_transient", "tr") for c in at.caption)


def test_steady_report_table_still_counts_iterations():
    at = upload(report_text("Iteration"))
    text = page(at)
    assert tr("polar_iters", "tr") in text
    assert not any(c.value == tr("polar_transient", "tr") for c in at.caption)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_oscillation_warning_points_to_urans(lang):
    text = tr("polar_warn_osc", lang, angles="16.99")
    assert "URANS" in text and "16.99°" in text


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_model_note_says_sst_gives_stall_late(lang):
    text = tr("polar_model_note", lang)
    assert "SST k-ω" in text and "16.99°" in text and "1.09" in text


def test_model_note_shown_under_the_polar():
    at = upload(report_text("Iteration"))
    assert any(c.value == tr("polar_model_note", "tr") for c in at.caption)


@pytest.mark.parametrize("name", ["README.md", "README.en.md", "CHANGELOG.md"])
def test_docs_hold_the_stall_result(name):
    text = doc_text(name)
    assert "16.99°" in text and "URANS" in text
