"""Pull validates bytes and writes only to the selected weight store."""
import argparse
import hashlib
import json

import pytest
from conftest import CannedJSONHandler, serve

from open_video.cli import open_video as cli
from open_video.core import h3_weights, resources
from open_video.scripts import verify_h3_manifest as verifier


@pytest.fixture
def tiny_store(tmp_path, monkeypatch):
    root = tmp_path / "site-packages" / "open_video"
    manifest_path = root / "models" / "h3_manifest.json"
    manifest_path.parent.mkdir(parents=True)
    store = tmp_path / "weight-store"
    good = b"verified weight bytes"
    manifest = {"files": {"weights.bin": {
        "size": len(good), "sha256": hashlib.sha256(good).hexdigest(),
        "commit": "a" * 40, "url": "http://127.0.0.1:1/never-fetch"}}}
    manifest_path.write_text(json.dumps(manifest))
    monkeypatch.setattr(cli, "REPO_ROOT", root)
    monkeypatch.setattr(h3_weights, "H3_INT8_FILES", {"weights.bin": len(good)})
    monkeypatch.setattr(resources, "recommend_for_host",
                        lambda **kw: resources.recommend_quant(32768, has_nvidia=True))
    args = argparse.Namespace(model="h3", models_dir=str(store), quant="auto",
                              check_only=False, json=False)
    return root, store, good, manifest_path, manifest, args


def put_weight(store, data):
    store.mkdir(exist_ok=True)
    (store / "weights.bin").write_bytes(data)


def test_same_size_corruption_is_rejected_and_preserved(tiny_store, monkeypatch, capsys):
    _, store, good, _, _, args = tiny_store
    corrupt = b"x" * len(good)
    put_weight(store, corrupt)
    monkeypatch.setattr(verifier, "cmd_fetch", lambda args: pytest.fail("must preserve corrupt file"))
    assert cli.cmd_pull(args) == 1
    assert (store / "weights.bin").read_bytes() == corrupt
    assert "hash mismatch" in capsys.readouterr().err


def test_valid_existing_weights_are_hash_checked(tiny_store, monkeypatch, capsys):
    _, store, good, _, _, args = tiny_store
    put_weight(store, good)
    monkeypatch.setattr(verifier, "cmd_fetch", lambda args: pytest.fail("no download needed"))
    assert cli.cmd_pull(args) == 0
    assert "verified (SHA-256)" in capsys.readouterr().out


def test_real_fetch_from_read_only_package_writes_only_model_store(tiny_store):
    root, store, good, path, manifest, args = tiny_store
    requested = []

    class Handler(CannedJSONHandler):
        def do_GET(self):
            requested.append(self.path)
            self.reply(raw=good, ctype="application/octet-stream")

    url, close = serve(Handler)
    manifest["files"]["weights.bin"]["url"] = url + "/weights.bin"
    path.write_text(json.dumps(manifest))
    before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    root.chmod(0o555)
    path.parent.chmod(0o555)
    path.chmod(0o444)
    try:
        assert cli.cmd_pull(args) == 0
        assert requested == ["/weights.bin"]
        assert (store / "weights.bin").read_bytes() == good
        assert {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
        assert sorted(str(p.relative_to(root)) for p in root.rglob("*")) == ["models", "models/h3_manifest.json"]
    finally:
        path.chmod(0o644)
        path.parent.chmod(0o755)
        root.chmod(0o755)
        close()


def test_failed_fetch_is_not_overridden_by_complete_files(tiny_store, monkeypatch):
    _, store, good, _, _, args = tiny_store

    def failed_fetch(_args):
        put_weight(store, good)
        return 1

    monkeypatch.setattr(verifier, "cmd_fetch", failed_fetch)
    monkeypatch.setattr(verifier, "cmd_check", lambda args: pytest.fail("fetch failure must propagate"))
    assert cli.cmd_pull(args) == 1


def test_missing_integrity_metadata_blocks_download(tiny_store, monkeypatch):
    _, store, _, path, manifest, args = tiny_store
    del manifest["files"]["weights.bin"]["sha256"]
    path.write_text(json.dumps(manifest))
    monkeypatch.setattr(verifier, "cmd_fetch", lambda args: pytest.fail("metadata gate must run first"))
    assert cli.cmd_pull(args) == 2
    assert not store.exists()


def test_check_only_is_explicitly_size_only(tiny_store, monkeypatch, capsys):
    _, store, good, _, _, args = tiny_store
    put_weight(store, b"x" * len(good))
    args.check_only = True
    monkeypatch.setattr(verifier, "cmd_check", lambda args: pytest.fail("inventory should stay cheap"))
    assert cli.cmd_pull(args) == 0
    assert "size inventory only" in capsys.readouterr().out


def test_missing_manifest_is_an_error(tiny_store):
    _, store, _, path, _, args = tiny_store
    path.unlink()
    assert cli.cmd_pull(args) == 2
    assert not store.exists()
