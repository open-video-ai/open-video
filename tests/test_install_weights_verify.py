"""Regression: install.sh download_weights must verify pre-existing weights.

W5 — a same-size corrupt/poisoned weight file must not pass: the all-present
(pending==0) path used to return success without calling verify_weights.
No network, no GPU, no real weights — tiny files under tmp_path, driven
through the REAL scripts/verify_h3_manifest.py checker. The download_weights /
verify_weights / url_for function bodies are extracted from the real
scripts/install.sh so the test exercises shipping code, not a copy.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL_SH = REPO / "scripts" / "install.sh"
VERIFIER = REPO / "scripts" / "verify_h3_manifest.py"

# Manifest records the GOOD bytes; tests may place different same-size bytes.
GOOD = {
    "a.bin": b"good weight a",
    "sub/b.bin": b"good weight bb",
}


def _extract_functions(source: str, names) -> str:
    out = []
    for name in names:
        m = re.search(rf"^{name}\(\) \{{.*?^\}}", source, re.M | re.S)
        assert m, f"{name}() not found in install.sh"
        out.append(m.group(0))
    return "\n\n".join(out)


def _write_manifest(tmp_path: Path, specs: dict[str, bytes]) -> Path:
    manifest = {"revision": "main", "files": {}}
    for rel, content in specs.items():
        manifest["files"][rel] = {
            "url": f"https://huggingface.co/x/y/resolve/main/{rel}",
            "size": len(content),
            "commit": "a" * 40,
            "sha256": hashlib.sha256(content).hexdigest(),
        }
    m = tmp_path / "manifest.json"
    m.write_text(json.dumps(manifest))
    return m


def _place_weight(tmp_path: Path, rel: str, content: bytes) -> None:
    p = tmp_path / "weights" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)


def _run_download_weights(tmp_path: Path, *, skip_download: int = 0) -> subprocess.CompletedProcess:
    funcs = _extract_functions(
        INSTALL_SH.read_text(encoding="utf-8"),
        ("url_for", "download_weights", "verify_weights"),
    )
    harness = tmp_path / "harness.sh"
    harness.write_text(f"""\
set -uo pipefail
OV_ROOT={tmp_path}
COMFYUI_LOG={tmp_path}/comfyui.log
ARIA_LIST={tmp_path}/aria.list
MODELS_DIR={tmp_path}/weights
H3_MANIFEST={tmp_path}/manifest.json
H3_VERIFY={VERIFIER}
QUANT=int8
SOURCE=hf
SKIP_DOWNLOAD={skip_download}
step() {{ :; }}
info() {{ :; }}
ok()   {{ printf 'OK: %s\\n' "$*"; }}
warn() {{ printf 'WARN: %s\\n' "$*" >&2; }}
err()  {{ printf 'ERR: %s\\n' "$*" >&2; }}
die()  {{ printf 'DIE: %s\\n' "$*" >&2; exit 2; }}
aria2c() {{ printf 'ARIA2C_INVOKED\\n' >> "{tmp_path}/aria2c.calls"; return 1; }}

{funcs}

download_weights
""")
    return subprocess.run(["bash", str(harness)], capture_output=True, text=True)


def test_same_size_corrupt_weights_fail(tmp_path: Path):
    """All files present at manifest size but wrong sha256: must exit nonzero
    BEFORE any success message — the pending==0 early return must verify."""
    _write_manifest(tmp_path, GOOD)
    for rel, content in GOOD.items():
        _place_weight(tmp_path, rel, b"x" * len(content))  # same size, bad hash
    r = _run_download_weights(tmp_path)
    out = r.stdout + r.stderr
    assert r.returncode != 0
    assert "hash mismatch" in out
    assert "nothing to download" not in out
    assert not (tmp_path / "aria2c.calls").exists()


def test_valid_existing_weights_pass_without_network(tmp_path: Path):
    """Correct size + sha256 for every file: pending==0 path succeeds and
    aria2c is never invoked."""
    _write_manifest(tmp_path, GOOD)
    for rel, content in GOOD.items():
        _place_weight(tmp_path, rel, content)
    r = _run_download_weights(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "nothing to download" in r.stdout
    assert not (tmp_path / "aria2c.calls").exists()


def test_missing_file_download_failure_still_verifies(tmp_path: Path):
    """One valid + one missing file: aria2c runs (and fails here), then the
    final manifest check must still gate success."""
    _write_manifest(tmp_path, GOOD)
    _place_weight(tmp_path, "a.bin", GOOD["a.bin"])
    r = _run_download_weights(tmp_path)
    out = r.stdout + r.stderr
    assert (tmp_path / "aria2c.calls").exists()
    assert r.returncode != 0
    assert "missing: sub/b.bin" in out
    assert "complete and verified" not in out


def test_skip_download_remains_explicit_bypass(tmp_path: Path):
    """--skip-download is the documented bring-your-own-weights escape hatch:
    it must keep returning success without fetching or verifying."""
    _write_manifest(tmp_path, GOOD)
    for rel, content in GOOD.items():
        _place_weight(tmp_path, rel, b"x" * len(content))
    r = _run_download_weights(tmp_path, skip_download=1)
    assert r.returncode == 0
    assert "--skip-download" in r.stdout
    assert not (tmp_path / "aria2c.calls").exists()
