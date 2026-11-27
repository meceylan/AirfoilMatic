"""Texts after the 2026-11-26 Ansys runs: NACA 4412 through the mapped mesh and the use-as-drawn
mode (both Fluent 2024 R2), the journal tried and failing inside Workbench, /mesh/replace, and the
SpaceClaim / SolidWorks outputs tried by the user."""
from pathlib import Path

import pytest

from airfoilmatic.fluent import sweep_journal
from airfoilmatic.i18n import tr
from _docs import doc_text

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return doc_text(name)


@pytest.mark.parametrize("name, stale", [
    ("README.md", "SpaceClaim biçimi henüz denenmedi"),
    ("README.en.md", "the SpaceClaim format is not tried yet"),
    ("README.md", "mapped mesh için sonuç yok"),
    ("README.en.md", "there is no result for the mapped mesh"),
    ("README.md", "Workbench ve case dosyasının üzerine yazma henüz denenmedi"),
    ("README.en.md", "Workbench and case overwriting have not been tried yet"),
    ("CHANGELOG.md", "Not tried yet: Fluent inside Workbench"),
    ("CHANGELOG.md", "Henüz denenmedi: Workbench içindeki Fluent"),
])
def test_stale_lines_are_gone(name, stale):
    assert stale not in read(name)


@pytest.mark.parametrize("name", ["README.md", "README.en.md", "CHANGELOG.md"])
def test_docs_hold_the_naca4412_runs_and_mesh_replace(name):
    text = read(name)
    assert "NACA 4412" in text and "/mesh/replace" in text and "−3.98°" in text


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_journal_note_says_workbench_was_tried(lang):
    assert "Workbench" in tr("jou_note", lang, expr="aoa", iterations=1000)
    assert "current and future" in doc_text("README.md" if lang == "tr" else "README.en.md")


def test_journal_header_says_workbench_was_tried():
    assert "asks again at every angle" in sweep_journal(0, 4, 2)


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_as_drawn_edge_note_gives_the_tried_example(lang):
    text = tr("asis_edges_note", lang, ds_le="1 mm", ds_te="6.5 mm")
    assert "266" in text and "258" in text and "NACA 4412" in text
