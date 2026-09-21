"""Shared H3 weight manifest + verifier tests (no network, no weights)."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "models" / "h3_manifest.json"
VERIFIER = REPO / "scripts" / "verify_h3_manifest.py"

# Byte sizes previously duplicated across install.sh / h3_download.sh /
# core/h3_weights.py — the manifest must carry the same values.
KNOWN_SIZES = {
    "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors": 20_970_379_616,
    "text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors": 27_141_342_152,
    "vae/minimax_h3_video_vae_fp16.safetensors": 5_207_808_496,
    "vae/minimax_h3_audio_vae_fp32.safetensors": 605_254_808,
}


def run(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFIER), *argv],
        capture_output=True, text=True,
    )


def test_manifest_structure():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = manifest["files"]
    assert set(files) == set(KNOWN_SIZES)
    for rel, spec in files.items():
        assert spec["url"].endswith(f"/{rel}")
        assert spec["url"].startswith("https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/")
        assert spec["size"] == KNOWN_SIZES[rel]
        # Integrity metadata is required schema; values are published and
        # asserted non-null in test_manifest_integrity_metadata.
        assert "sha256" in spec and "commit" in spec
        if spec["sha256"] is not None:
            assert re.fullmatch(r"[0-9a-f]{64}", spec["sha256"])
        if spec["commit"] is not None:
            assert re.fullmatch(r"[0-9a-f]{7,40}", spec["commit"])


def test_manifest_integrity_metadata():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for rel, spec in manifest["files"].items():
        assert re.fullmatch(r"[0-9a-f]{64}", spec["sha256"] or "")
        assert re.fullmatch(r"[0-9a-f]{7,40}", spec["commit"] or "")
        assert f"/resolve/{spec['commit']}/" in spec["url"]


def test_installers_consume_shared_manifest():
    install = (REPO / "scripts" / "install.sh").read_text(encoding="utf-8")
    download = (REPO / "scripts" / "h3_download.sh").read_text(encoding="utf-8")
    pinokio = (REPO / "scripts" / "pinokio_install.js").read_text(encoding="utf-8")

    for text in (install, download, pinokio):
        assert "h3_manifest.json" in text
        assert "verify_h3_manifest.py" in text

    # no leftover duplicated file/size tables in the installers
    assert "H3_SIZES" not in install
    assert "declare -A WANT" not in download
    for size in KNOWN_SIZES.values():
        assert str(size) not in install
        assert str(size) not in download
    # pinokio must not keep hard-coded per-file curl downloads
    assert "huggingface.co/Comfy-Org/MiniMax-H3/resolve" not in pinokio


def _write_manifest(tmp_path: Path, sha256=None, commit="a" * 40) -> Path:
    content = b"tiny weight bytes"
    (tmp_path / "models" / "w").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "models" / "w").write_bytes(content)
    spec = {
        "url": "https://huggingface.co/x/y/resolve/main/models/w",
        "size": len(content),
        "commit": commit,
        "sha256": hashlib.sha256(content).hexdigest() if sha256 is None else sha256,
    }
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps({"revision": "main", "files": {"models/w": spec}}))
    return m


def test_check_passes_with_matching_file(tmp_path):
    m = _write_manifest(tmp_path)
    r = run("check", "--manifest", str(m), "--models-dir", str(tmp_path))
    assert r.returncode == 0, r.stderr


def test_check_rejects_missing_wrong_size_wrong_hash(tmp_path):
    m = _write_manifest(tmp_path)
    d = tmp_path / "empty"
    d.mkdir()
    assert run("check", "--manifest", str(m), "--models-dir", str(d)).returncode == 1

    m2 = _write_manifest(tmp_path)
    spec = json.loads(m2.read_text())["files"]["models/w"]
    spec["size"] += 1
    m2.write_text(json.dumps({"revision": "main", "files": {"models/w": spec}}))
    assert run("check", "--manifest", str(m2), "--models-dir", str(tmp_path)).returncode == 1

    m3 = _write_manifest(tmp_path, sha256="0" * 64)
    r = run("check", "--manifest", str(m3), "--models-dir", str(tmp_path))
    assert r.returncode == 1 and "hash mismatch" in r.stderr


def test_check_fails_closed_on_missing_metadata(tmp_path):
    m = _write_manifest(tmp_path, sha256=None)
    spec = json.loads(m.read_text())["files"]["models/w"]
    spec["sha256"] = None
    m.write_text(json.dumps({"revision": "main", "files": {"models/w": spec}}))

    r = run("check", "--manifest", str(m), "--models-dir", str(tmp_path))
    assert r.returncode == 2
    assert "integrity metadata missing" in r.stderr

    # --size-only remains available for resume bookkeeping
    r = run("check", "--size-only", "--manifest", str(m), "--models-dir", str(tmp_path))
    assert r.returncode == 0


def test_data_commands_and_commit_pinning(tmp_path):
    m = _write_manifest(tmp_path)
    r = run("paths", str(m))
    assert r.returncode == 0 and r.stdout.strip() == "models/w"
    assert run("size", str(m), "models/w").stdout.strip() == str(
        len(b"tiny weight bytes"))

    spec = json.loads(m.read_text())["files"]["models/w"]
    pinned = "b" * 40
    spec["commit"] = pinned
    m.write_text(json.dumps({"revision": "main", "files": {"models/w": spec}}))
    r = run("url", str(m), "models/w")
    assert f"/resolve/{pinned}/" in r.stdout
