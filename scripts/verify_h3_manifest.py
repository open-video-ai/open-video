#!/usr/bin/env python3
"""Shared H3 weight manifest tool — single source of truth for installers.

Reads models/h3_manifest.json (paths, byte sizes, HF URLs, release
commit/sha256) so scripts/install.sh, scripts/h3_download.sh and
scripts/pinokio_install.js stop duplicating the file/size/URL policy.

Commands:
  paths  MANIFEST                      one relative path per line
  size   MANIFEST REL                  expected byte size for REL
  url    MANIFEST REL                  download URL (pinned to commit when set)
  check  --manifest M --models-dir D   verify files; fails closed (exit 2)
                                       when sha256/commit metadata is missing
  fetch  --manifest M --models-dir D   curl-download missing/incomplete files

Exit codes: 0 ok · 1 verification/fetch failure · 2 manifest metadata missing.
Stdlib only — installers may run this before project deps are installed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

EXIT_BAD = 1
EXIT_NEEDS_METADATA = 2


def load_manifest(path: str) -> dict:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise SystemExit(f"error: {path} has no 'files' entries")
    for rel, spec in files.items():
        if not isinstance(spec.get("size"), int) or spec["size"] <= 0:
            raise SystemExit(f"error: {path}: '{rel}' missing positive integer 'size'")
        if not spec.get("url"):
            raise SystemExit(f"error: {path}: '{rel}' missing 'url'")
    return manifest


def resolve_url(manifest: dict, spec: dict) -> str:
    """URL pinned to the recorded HF commit when one is set, else as stored."""
    url = spec["url"]
    commit = spec.get("commit")
    if commit:
        revision = manifest.get("revision", "main")
        url = url.replace(f"/resolve/{revision}/", f"/resolve/{commit}/", 1)
    return url


def missing_metadata(manifest: dict) -> list[str]:
    return [
        rel
        for rel, spec in manifest["files"].items()
        if not spec.get("sha256") or not spec.get("commit")
    ]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cmd_paths(args) -> int:
    for rel in load_manifest(args.manifest)["files"]:
        print(rel)
    return 0


def cmd_size(args) -> int:
    print(load_manifest(args.manifest)["files"][args.rel]["size"])
    return 0


def cmd_url(args) -> int:
    manifest = load_manifest(args.manifest)
    print(resolve_url(manifest, manifest["files"][args.rel]))
    return 0


def cmd_check(args) -> int:
    manifest = load_manifest(args.manifest)
    root = Path(args.models_dir)

    if not args.size_only:
        # Fail closed: refuse to "verify" on size alone while release
        # sha256/commit metadata is still pending (NEEDS_INPUT).
        missing = missing_metadata(manifest)
        if missing:
            for rel in missing:
                print(f"integrity metadata missing (sha256/commit): {rel}", file=sys.stderr)
            print(
                f"error: {args.manifest} has no release sha256/commit — "
                "cannot verify integrity. Fill the published values first.",
                file=sys.stderr,
            )
            return EXIT_NEEDS_METADATA

    bad = 0
    for rel, spec in manifest["files"].items():
        path = root / rel
        if not path.is_file():
            print(f"missing: {rel}", file=sys.stderr)
            bad = EXIT_BAD
            continue
        got = path.stat().st_size
        if got != spec["size"]:
            print(f"size mismatch: {rel} — got {got}, expected {spec['size']}", file=sys.stderr)
            bad = EXIT_BAD
            continue
        want_hash = spec.get("sha256")
        if not args.size_only and want_hash:
            if sha256_of(path) != want_hash:
                print(f"hash mismatch: {rel}", file=sys.stderr)
                bad = EXIT_BAD
    return bad


def cmd_fetch(args) -> int:
    manifest = load_manifest(args.manifest)
    root = Path(args.models_dir)
    bad = 0
    for rel, spec in manifest["files"].items():
        dst = root / rel
        if dst.is_file() and dst.stat().st_size == spec["size"]:
            print(f"complete: {rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        url = resolve_url(manifest, spec)
        print(f"fetch: {rel}")
        rc = subprocess.run(
            ["curl", "-L", "--fail", "--retry", "5", "-C", "-", "-o", str(dst), url]
        ).returncode
        if rc != 0:
            print(f"fetch failed: {rel} (curl exit {rc})", file=sys.stderr)
            bad = EXIT_BAD
            continue
        got = dst.stat().st_size
        if got != spec["size"]:
            print(f"size mismatch: {rel} — got {got}, expected {spec['size']}", file=sys.stderr)
            bad = EXIT_BAD
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("paths")
    p.add_argument("manifest")
    p.set_defaults(func=cmd_paths)

    p = sub.add_parser("size")
    p.add_argument("manifest")
    p.add_argument("rel")
    p.set_defaults(func=cmd_size)

    p = sub.add_parser("url")
    p.add_argument("manifest")
    p.add_argument("rel")
    p.set_defaults(func=cmd_url)

    p = sub.add_parser("check")
    p.add_argument("--manifest", required=True)
    p.add_argument("--models-dir", required=True)
    p.add_argument("--size-only", action="store_true",
                   help="presence+size only (resume bookkeeping, not integrity)")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("fetch")
    p.add_argument("--manifest", required=True)
    p.add_argument("--models-dir", required=True)
    p.set_defaults(func=cmd_fetch)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
