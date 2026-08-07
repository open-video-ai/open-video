"""open-video global configuration."""
import os
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent  # open-video/ (source) or site-packages/open_video (wheel)
LIBRARY = ROOT / "library"
BACKENDS = ROOT / "backends"
ENGINES = ROOT / "engines"
JUDGES = ROOT / "judges"
TEMPLATES = ROOT / "templates"
BENCH = ROOT / "bench"


def is_installed_path(p: Path) -> bool:
    """True when ``p`` lives inside an installed package tree (site/dist-packages)."""
    return any(part in ("site-packages", "dist-packages") for part in p.parts)


# Mutable state (outputs, artifacts, model fallbacks) must never land inside an
# installed package tree. Source checkout keeps the historical repo-relative
# behavior; a wheel install defaults to ~/.open-video (override: OPEN_VIDEO_HOME).
DEFAULT_STATE_HOME = Path.home() / ".open-video"
_home = os.environ.get("OPEN_VIDEO_HOME", "").strip()
if _home:
    STATE_ROOT = Path(_home).expanduser()
elif is_installed_path(ROOT):
    STATE_ROOT = DEFAULT_STATE_HOME
else:
    STATE_ROOT = ROOT
OUTPUT = STATE_ROOT / "output"
ARTIFACTS = STATE_ROOT / "artifacts"

# Engine defaults
COMFYUI_SERVER = os.environ.get("OPEN_VIDEO_COMFYUI", "http://127.0.0.1:8188")

# Model defaults
DEFAULT_MODEL = os.environ.get("OPEN_VIDEO_MODEL", "h3")
DEFAULT_RESOLUTION = (1344, 768)  # 16:9, 768px short edge
DEFAULT_STEPS = 20
DEFAULT_SAMPLER = "res_multistep"
DEFAULT_SCHEDULER = "simple"

# Quality loop defaults
DEFAULT_QUALITY_BAR = 0.7
DEFAULT_N_FRAMES_JUDGE = 5
DEFAULT_JUDGE_TIMEOUT_S = 30

# Output settings
DEFAULT_FPS = 24
DEFAULT_ASPECTS = ("16:9", "9:16", "1:1", "4:3", "3:4", "21:9")

# Recipe-in-render (the #1 growth lever — embed full recipe in every output)
EMBED_RECIPE_METADATA = True  # embed prompt+model+settings+seed in output MP4 metadata
