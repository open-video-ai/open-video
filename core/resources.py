"""Host resource probe and H3 quant recommendation (Ollama-style pull-by-hardware).

Pure selection logic is network-free and unit-testable. Installer and CLI call
``recommend_quant`` / ``format_recommendation`` after probing VRAM.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Optional


# VRAM thresholds in MiB (nvidia-smi style). Tuned to docs/h3_ecosystem.md.
# < 9 GiB  → nf4   (~8 GB entry)
# < 12 GiB → w4    (~10 GB balanced)
# < 22 GiB → int8 + lowvram offload (INT8 package, Comfy --lowvram)
# >= 22 GiB → int8 (default verified package)
THRESH_NF4_MIB = 9 * 1024
THRESH_W4_MIB = 12 * 1024
THRESH_INT8_FULL_MIB = 22 * 1024

QUANTS = ("nf4", "w4", "int8")


@dataclass(frozen=True)
class QuantRecommendation:
    """Result of resource-aware H3 quant selection."""

    quant: str
    reason: str
    vram_mib: int
    lowvram: bool
    download_profile: str  # which weight set the installer should fetch
    min_vram_mib: int
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recommend_quant(
    vram_mib: int,
    *,
    has_nvidia: bool = True,
    force_quant: Optional[str] = None,
) -> QuantRecommendation:
    """Choose an H3 quant for the host.

    Parameters
    ----------
    vram_mib:
        Total GPU VRAM in MiB (0 if unknown / none).
    has_nvidia:
        False on macOS / CPU-only hosts → honest degradation recommendation.
    force_quant:
        If set to nf4|w4|int8, honor user override and explain it.
    """
    fq = (force_quant or "").strip().lower()
    if fq in ("", "auto", "default"):
        fq = ""
    if fq and fq not in QUANTS:
        raise ValueError(f"unknown quant {force_quant!r}; expected one of {QUANTS} or auto")

    if not has_nvidia or vram_mib <= 0:
        return QuantRecommendation(
            quant="int8",
            reason="no NVIDIA GPU / unknown VRAM — default INT8 package; generation skipped until GPU present",
            vram_mib=max(0, int(vram_mib)),
            lowvram=True,
            download_profile="int8",
            min_vram_mib=THRESH_INT8_FULL_MIB,
            notes="Plan/validate with `open-video \"…\" --dry-run`. H3 generation needs NVIDIA.",
        )

    v = int(vram_mib)

    if fq:
        low = fq in ("nf4", "w4") or v < THRESH_INT8_FULL_MIB
        return QuantRecommendation(
            quant=fq,
            reason=f"user override --quant {fq} (host reports {v} MiB VRAM)",
            vram_mib=v,
            lowvram=low,
            download_profile="int8" if fq == "int8" else fq,
            min_vram_mib=_min_for(fq),
            notes=_notes_for(fq, low),
        )

    if v < THRESH_NF4_MIB:
        return QuantRecommendation(
            quant="nf4",
            reason=f"{v} MiB VRAM < {THRESH_NF4_MIB} MiB → NF4 (~8 GB) tier",
            vram_mib=v,
            lowvram=True,
            download_profile="nf4",
            min_vram_mib=8 * 1024,
            notes=_notes_for("nf4", True),
        )
    if v < THRESH_W4_MIB:
        return QuantRecommendation(
            quant="w4",
            reason=f"{v} MiB VRAM < {THRESH_W4_MIB} MiB → W4 ConvRot (~10 GB) tier",
            vram_mib=v,
            lowvram=True,
            download_profile="w4",
            min_vram_mib=10 * 1024,
            notes=_notes_for("w4", True),
        )
    if v < THRESH_INT8_FULL_MIB:
        return QuantRecommendation(
            quant="int8",
            reason=f"{v} MiB VRAM < {THRESH_INT8_FULL_MIB} MiB → INT8 package with ComfyUI --lowvram",
            vram_mib=v,
            lowvram=True,
            download_profile="int8",
            min_vram_mib=THRESH_INT8_FULL_MIB,
            notes=_notes_for("int8", True),
        )
    return QuantRecommendation(
        quant="int8",
        reason=f"{v} MiB VRAM ≥ {THRESH_INT8_FULL_MIB} MiB → default INT8 ConvRot (verified package)",
        vram_mib=v,
        lowvram=False,
        download_profile="int8",
        min_vram_mib=THRESH_INT8_FULL_MIB,
        notes=_notes_for("int8", False),
    )


def _min_for(quant: str) -> int:
    return {
        "nf4": 8 * 1024,
        "w4": 10 * 1024,
        "int8": THRESH_INT8_FULL_MIB,
    }[quant]


def _notes_for(quant: str, lowvram: bool) -> str:
    bits = []
    if quant == "nf4":
        bits.append("NF4 weights: DiffSynth-Studio/MiniMax-H3-NF4 (see docs/h3_ecosystem.md).")
        bits.append("Installer may stage the verified INT8 set + --lowvram when NF4 aria list is not configured.")
    elif quant == "w4":
        bits.append("W4 weights: DmitryDB/MiniMax-H3-ComfyUI-Quants (see docs/h3_ecosystem.md).")
        bits.append("Installer may stage INT8 + --lowvram when W4 aria list is not configured.")
    else:
        bits.append("INT8 ConvRot: Comfy-Org/MiniMax-H3 (default verified ~54 GB pull).")
    if lowvram:
        bits.append("ComfyUI will start with --lowvram.")
    return " ".join(bits)


def format_recommendation(rec: QuantRecommendation) -> str:
    """Human-readable multi-line status block for install / CLI."""
    lines = [
        f"[open-video] quant={rec.quant}  lowvram={str(rec.lowvram).lower()}  "
        f"download_profile={rec.download_profile}",
        f"[open-video] reason: {rec.reason}",
    ]
    if rec.notes:
        lines.append(f"[open-video] note: {rec.notes}")
    return "\n".join(lines)


def probe_nvidia_vram_mib() -> tuple[bool, int, str]:
    """Best-effort live probe via nvidia-smi. Returns (has_nvidia, vram_mib, name)."""
    import shutil
    import subprocess

    if not shutil.which("nvidia-smi"):
        return False, 0, "none"
    try:
        name = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=8,
        ).strip().splitlines()[0].strip()
        vram_s = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=8,
        ).strip().splitlines()[0].strip()
        vram = int(float(vram_s))
        return True, vram, name or "NVIDIA"
    except Exception:
        return False, 0, "none"


def recommend_for_host(force_quant: Optional[str] = None) -> QuantRecommendation:
    """Probe host then recommend."""
    has, vram, _name = probe_nvidia_vram_mib()
    return recommend_quant(vram, has_nvidia=has, force_quant=force_quant)


def recommendation_from_mapping(data: Mapping[str, Any]) -> QuantRecommendation:
    """Rebuild a recommendation from a JSON-ish mapping (tests / install bridge)."""
    return QuantRecommendation(
        quant=str(data["quant"]),
        reason=str(data["reason"]),
        vram_mib=int(data["vram_mib"]),
        lowvram=bool(data["lowvram"]),
        download_profile=str(data["download_profile"]),
        min_vram_mib=int(data["min_vram_mib"]),
        notes=str(data.get("notes") or ""),
    )


def main(argv: Optional[list[str]] = None) -> int:
    """CLI: ``python -m core.resources [--vram N] [--no-nvidia] [--quant auto|nf4|w4|int8]``."""
    import argparse
    import json
    import sys

    p = argparse.ArgumentParser(prog="open-video recommend-quant")
    p.add_argument("--vram", type=int, default=None, help="Override VRAM MiB (fixture mode)")
    p.add_argument("--no-nvidia", action="store_true", help="Simulate no NVIDIA GPU")
    p.add_argument("--quant", default="auto", help="Force quant or auto")
    p.add_argument("--json", action="store_true", help="Emit JSON")
    args = p.parse_args(argv)

    if args.vram is not None or args.no_nvidia:
        has = not args.no_nvidia
        vram = 0 if args.no_nvidia else int(args.vram or 0)
        rec = recommend_quant(vram, has_nvidia=has, force_quant=args.quant)
    else:
        rec = recommend_for_host(force_quant=args.quant)

    if args.json:
        print(json.dumps(rec.to_dict(), indent=2, sort_keys=True))
    else:
        print(format_recommendation(rec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
