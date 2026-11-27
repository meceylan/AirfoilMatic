"""Version 0.6.7 (Altori, 2026-11-27): the entries added after the v0.6.6 tag move to their own
section; the 0.6.6 section keeps what the tag had (the Fluent journal and the review fixes)."""
from pathlib import Path

from airfoilmatic import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_version_and_readme_titles():
    assert __version__ == "0.6.7"
    for name in ("README.md", "README.en.md"):
        assert (ROOT / name).read_text(encoding="utf-8").splitlines()[0].startswith("# AirfoilMatic V0.6.7 Beta")


def test_changelog_sections():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    heads = [l for l in text.splitlines() if l.startswith("## ")]
    assert heads[:4] == ["## V0.6.7 Beta", "## V0.6.7 Beta (Türkçe)", "## V0.6.6 Beta", "## V0.6.6 Beta (Türkçe)"]
    s067 = text.split("## V0.6.7 Beta (Türkçe)")[0]
    s066 = text.split("## V0.6.6 Beta\n")[1].split("## V0.6.6 Beta (Türkçe)")[0]
    for t in ("Faster mesh building", "Suggestions while typing", "Fluent mesh file (.msh) from the app", "Section library: 300"):
        assert t in s067 and t not in s066, t
    for t in ("Fluent journal.", "Fixes from a code review"):
        assert t in s066 and t not in s067, t
    tr067 = text.split("## V0.6.7 Beta (Türkçe)")[1].split("## V0.6.6 Beta\n")[0]
    assert "Mesh kurma ve testler hızlandı" in tr067 and "Profil aramasında yazarken öneri" in tr067
