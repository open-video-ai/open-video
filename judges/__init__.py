"""open-video judge plugins — community-contributed quality assessors.

Each judge implements the QualityJudge interface from core/judge.py. Plugins:
- vision.py: VLM-based judge (calls a vision model on extracted frames)
- (future) videoscore.py: TIGER-AI-Lab VideoScore integration
- (future) human.py: human-in-the-loop judge
- (future) tournament.py: best-of-N tournament judge

Auto-discovery: drop a .py file in judges/ implementing QualityJudge → it's available.
"""
import importlib, pkgutil
from open_video.core.judge import QualityJudge

JUDGES = {}
for _, name, _ in pkgutil.iter_modules(__path__):
    try:
        mod = importlib.import_module(f"judges.{name}")
        if hasattr(mod, "Judge"):
            JUDGES[mod.Judge.id] = mod.Judge()
    except Exception:
        pass  # graceful: broken plugins don't crash the system
