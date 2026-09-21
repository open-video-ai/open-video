"""CLI availability checks for advertised optional capabilities."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_no_unavailable_serve_extra():
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    assert "serve = [" not in text
