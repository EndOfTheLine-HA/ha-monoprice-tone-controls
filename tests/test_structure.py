"""Repository checks for the tone-controls stopgap."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "custom_components" / "monoprice"


def test_metadata():
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    # The point of this repository: it keeps the core domain so existing amp and
    # tone-control entities are reused as they are.
    assert manifest["domain"] == "monoprice"
    # Hassfest rejects an exact pin of a package Home Assistant core depends on.
    assert manifest["requirements"] == ["pymonoprice>=0.6.1"]
    assert manifest["version"] == project["project"]["version"]


def test_english_translation_matches_source_strings():
    strings = json.loads((PACKAGE / "strings.json").read_text(encoding="utf-8"))
    english = json.loads(
        (PACKAGE / "translations" / "en.json").read_text(encoding="utf-8")
    )
    assert english == strings


def test_matrix_code_is_not_shipped():
    """The HDMI matrix belongs to No Hassle AV (nohassle_av) now."""
    for name in ("matrix.py", "select.py", "button.py", "binary_sensor.py"):
        assert not (PACKAGE / name).exists(), name


def test_no_em_dashes_in_user_facing_text():
    files = [ROOT / "README.md", ROOT / "AUDIT.md", PACKAGE / "strings.json"]
    for path in files:
        assert chr(0x2014) not in path.read_text(encoding="utf-8"), path.name
