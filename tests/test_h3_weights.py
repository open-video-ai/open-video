"""Unit tests for core.h3_weights inventory (no network)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from open_video.core.h3_weights import (  # noqa: E402
    H3_INT8_FILES,
    TOTAL_INT8_BYTES,
    default_models_dir,
    format_inventory,
    inventory_h3_int8,
    known_models,
)


def test_manifest_has_four_files_and_stable_total():
    assert len(H3_INT8_FILES) == 4
    assert TOTAL_INT8_BYTES == sum(H3_INT8_FILES.values())
    assert TOTAL_INT8_BYTES > 50 * (1 << 30)  # ~54 GB package


def test_inventory_missing_on_empty_dir(tmp_path: Path):
    inv = inventory_h3_int8(tmp_path)
    assert inv.model == "h3"
    assert inv.ready is False
    assert inv.complete_count == 0
    assert inv.total_count == 4
    assert len(inv.missing()) == 4
    text = format_inventory(inv)
    assert "0/4" in text
    assert "pull incomplete" in text


def test_inventory_ready_when_sizes_match(tmp_path: Path):
    for rel, size in H3_INT8_FILES.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        # sparse-ish: write exact size with seek (fast)
        with p.open("wb") as f:
            if size > 0:
                f.seek(size - 1)
                f.write(b"\0")
    inv = inventory_h3_int8(tmp_path)
    assert inv.ready is True
    assert inv.complete_count == 4
    assert inv.missing() == []
    assert "ready" in format_inventory(inv).lower()


def test_partial_file_not_complete(tmp_path: Path):
    rel = next(iter(H3_INT8_FILES))
    expected = H3_INT8_FILES[rel]
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"x" * 100)
    inv = inventory_h3_int8(tmp_path)
    st = next(f for f in inv.files if f.rel == rel)
    assert st.present is True
    assert st.complete is False
    assert st.size_bytes == 100
    assert st.expected_bytes == expected
    assert inv.ready is False


def test_known_models_includes_h3():
    assert "h3" in known_models()


def test_default_models_dir_env(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPEN_VIDEO_MODELS", str(tmp_path / "m"))
    assert default_models_dir() == (tmp_path / "m").resolve()
