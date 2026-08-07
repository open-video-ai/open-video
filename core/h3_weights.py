"""H3 weight inventory — Ollama-style ``pull`` target for MiniMax H3.

Verified INT8 ConvRot package (same four files as ``scripts/install.sh``).
Network-free checks only; download is delegated to the installer.
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

# Verified byte sizes — HF HEAD + install.sh H3_SIZES (INT8 ConvRot package).
H3_INT8_FILES: dict[str, int] = {
    "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors": 20_970_379_616,
    "text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors": 27_141_342_152,
    "vae/minimax_h3_video_vae_fp16.safetensors": 5_207_808_496,
    "vae/minimax_h3_audio_vae_fp32.safetensors": 605_254_808,
}

TOTAL_INT8_BYTES = sum(H3_INT8_FILES.values())


@dataclass(frozen=True)
class WeightFileStatus:
    rel: str
    expected_bytes: int
    path: str
    present: bool
    size_bytes: int
    complete: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WeightInventory:
    model: str
    models_dir: str
    profile: str
    files: tuple[WeightFileStatus, ...]
    complete_count: int
    total_count: int
    ready: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "models_dir": self.models_dir,
            "profile": self.profile,
            "complete_count": self.complete_count,
            "total_count": self.total_count,
            "ready": self.ready,
            "files": [f.to_dict() for f in self.files],
        }

    def missing(self) -> list[WeightFileStatus]:
        return [f for f in self.files if not f.complete]


def default_models_dir(repo_root: Optional[Path] = None) -> Path:
    """Resolve models directory (Ollama-style local store).

    Order:
      1. ``OPEN_VIDEO_MODELS``
      2. ``$OPEN_VIDEO_HOME/ComfyUI/models`` or ``$OPEN_VIDEO_HOME/models``
      3. ``<repo>/ComfyUI/models``
      4. ``<repo>/models``
    """
    env = os.environ.get("OPEN_VIDEO_MODELS", "").strip()
    if env:
        return Path(env).expanduser().resolve()

    home = os.environ.get("OPEN_VIDEO_HOME", "").strip()
    if home:
        hp = Path(home).expanduser().resolve()
        for cand in (hp / "ComfyUI" / "models", hp / "models"):
            if cand.is_dir() or not (hp / "ComfyUI").exists():
                # Prefer ComfyUI/models when ComfyUI tree exists or neither exists yet
                if (hp / "ComfyUI").exists():
                    return (hp / "ComfyUI" / "models").resolve()
                return cand.resolve()
        return (hp / "ComfyUI" / "models").resolve()

    root = Path(repo_root) if repo_root else Path.cwd()
    root = root.resolve()
    comfy = root / "ComfyUI" / "models"
    if comfy.is_dir() or (root / "ComfyUI").is_dir():
        return comfy.resolve()
    return (root / "models").resolve()


def inventory_h3_int8(models_dir: Path | str) -> WeightInventory:
    """Check the verified INT8 ConvRot H3 package under ``models_dir``."""
    base = Path(models_dir)
    files: list[WeightFileStatus] = []
    for rel, expected in H3_INT8_FILES.items():
        path = base / rel
        present = path.is_file()
        size = path.stat().st_size if present else 0
        complete = present and size == expected
        files.append(
            WeightFileStatus(
                rel=rel,
                expected_bytes=expected,
                path=str(path),
                present=present,
                size_bytes=size,
                complete=complete,
            )
        )
    complete_n = sum(1 for f in files if f.complete)
    return WeightInventory(
        model="h3",
        models_dir=str(base),
        profile="int8",
        files=tuple(files),
        complete_count=complete_n,
        total_count=len(files),
        ready=complete_n == len(files),
    )


def format_inventory(inv: WeightInventory) -> str:
    lines = [
        f"[open-video] model={inv.model}  profile={inv.profile}  "
        f"{inv.complete_count}/{inv.total_count} files ready",
        f"[open-video] models_dir={inv.models_dir}",
    ]
    for f in inv.files:
        mark = "OK" if f.complete else ("partial" if f.present else "missing")
        human = _human_bytes(f.size_bytes) if f.present else "—"
        want = _human_bytes(f.expected_bytes)
        lines.append(f"  [{mark:7}] {f.rel}  ({human} / {want})")
    if inv.ready:
        lines.append("[open-video] H3 weights ready — `open-video run \"…\"` or `open-video status`")
    else:
        lines.append(
            "[open-video] pull incomplete — run `open-video pull h3` "
            "(or re-run install; aria2c resumes)"
        )
    return "\n".join(lines)


def _human_bytes(n: int) -> str:
    if n >= 1 << 30:
        return f"{n / (1 << 30):.2f} GiB"
    if n >= 1 << 20:
        return f"{n / (1 << 20):.1f} MiB"
    if n >= 1 << 10:
        return f"{n / (1 << 10):.0f} KiB"
    return f"{n} B"


def known_models() -> tuple[str, ...]:
    """Model ids that ``open-video pull`` understands today."""
    return ("h3",)
