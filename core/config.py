"""open-video global configuration."""
import os
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent  # open-video/
LIBRARY = ROOT / "library"
BACKENDS = ROOT / "backends"
ENGINES = ROOT / "engines"
JUDGES = ROOT / "judges"
TEMPLATES = ROOT / "templates"
BENCH = ROOT / "bench"
OUTPUT = ROOT / "output"
ARTIFACTS = ROOT / "artifacts"

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
