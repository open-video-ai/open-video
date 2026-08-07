"""Unit tests for core.resources quant selection — real shipped functions only."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from core.resources import (  # noqa: E402
    THRESH_INT8_FULL_MIB,
    THRESH_NF4_MIB,
    THRESH_W4_MIB,
    format_recommendation,
    recommend_quant,
)


def test_low_vram_selects_nf4():
    rec = recommend_quant(8 * 1024, has_nvidia=True)
    assert rec.quant == "nf4"
    assert rec.lowvram is True
    assert rec.download_profile == "nf4"
    assert "NF4" in rec.reason or "nf4" in rec.reason.lower()
    assert rec.vram_mib == 8 * 1024


def test_mid_vram_selects_w4():
    # 10 GiB sits between NF4 and W4 thresholds
    rec = recommend_quant(10 * 1024, has_nvidia=True)
    assert rec.quant == "w4"
    assert rec.lowvram is True
    assert "W4" in rec.reason or "w4" in rec.reason.lower()


def test_high_vram_selects_int8_no_lowvram():
    rec = recommend_quant(32 * 1024, has_nvidia=True)
    assert rec.quant == "int8"
    assert rec.lowvram is False
    assert rec.download_profile == "int8"
    assert rec.vram_mib == 32 * 1024


def test_borderline_int8_uses_lowvram():
    # 16 GiB: INT8 package but needs offload
    rec = recommend_quant(16 * 1024, has_nvidia=True)
    assert rec.quant == "int8"
    assert rec.lowvram is True


def test_no_nvidia_still_returns_int8_with_honest_reason():
    rec = recommend_quant(0, has_nvidia=False)
    assert rec.quant == "int8"
    assert rec.lowvram is True
    assert "no NVIDIA" in rec.reason or "unknown" in rec.reason.lower()


def test_force_quant_override():
    rec = recommend_quant(32 * 1024, has_nvidia=True, force_quant="nf4")
    assert rec.quant == "nf4"
    assert "override" in rec.reason.lower() or "user" in rec.reason.lower()


def test_two_vram_scenarios_differ():
    low = recommend_quant(8 * 1024, has_nvidia=True)
    high = recommend_quant(32 * 1024, has_nvidia=True)
    assert low.quant != high.quant
    assert low.reason != high.reason
    assert "nf4" == low.quant
    assert "int8" == high.quant


def test_format_recommendation_includes_reason():
    rec = recommend_quant(8 * 1024, has_nvidia=True)
    text = format_recommendation(rec)
    assert "quant=nf4" in text
    assert "reason:" in text
    assert str(THRESH_NF4_MIB) in rec.reason or "MiB" in rec.reason


def test_cli_probe_fixture_json():
    """Drive the real shipped module entry point with VRAM fixtures."""
    py = sys.executable
    mod = str(REPO / "core" / "resources.py")
    # low
    out_lo = subprocess.check_output(
        [py, mod, "--vram", str(8 * 1024), "--json"],
        text=True,
        cwd=str(REPO),
    )
    lo = json.loads(out_lo)
    # high
    out_hi = subprocess.check_output(
        [py, mod, "--vram", str(32 * 1024), "--json"],
        text=True,
        cwd=str(REPO),
    )
    hi = json.loads(out_hi)
    assert lo["quant"] == "nf4"
    assert hi["quant"] == "int8"
    assert lo["quant"] != hi["quant"]
    assert lo["reason"]
    assert hi["reason"]


def test_thresholds_ordering():
    assert THRESH_NF4_MIB < THRESH_W4_MIB < THRESH_INT8_FULL_MIB
