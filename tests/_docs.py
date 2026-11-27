"""Text of a project document as the GitHub page holds it: a README together with its validation
page (docs/VALIDATION*.md), where the long Ansys / Fluent results moved; any other file as is."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_PAIRS = {"README.md": "docs/VALIDATION.md", "README.en.md": "docs/VALIDATION.en.md"}


def doc_text(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    if name in _PAIRS:
        text += "\n" + (ROOT / _PAIRS[name]).read_text(encoding="utf-8")
    return text
