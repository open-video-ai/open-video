"""State-root discipline: mutable state must never land inside an installed tree."""
import importlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from open_video.core.config import is_installed_path  # noqa: E402
from open_video.core.h3_weights import default_models_dir  # noqa: E402


def test_is_installed_path():
    assert is_installed_path(Path("/venv/lib/python3.12/site-packages/open_video"))
    assert is_installed_path(Path("/usr/lib/python3/dist-packages/open_video"))
    assert not is_installed_path(Path("/home/dev/open-video"))


def test_models_dir_never_targets_site_packages(monkeypatch):
    for var in ("OPEN_VIDEO_MODELS", "OPEN_VIDEO_LAB", "OPEN_VIDEO_HOME"):
        monkeypatch.delenv(var, raising=False)
    installed_root = Path("/venv/lib/python3.12/site-packages/open_video")
    got = default_models_dir(installed_root)
    assert "site-packages" not in got.parts
    assert got == (Path.home() / ".open-video" / "models").resolve()


def test_source_checkout_state_root_unchanged(monkeypatch):
    monkeypatch.delenv("OPEN_VIDEO_HOME", raising=False)
    import open_video.core.config as cfg
    importlib.reload(cfg)
    assert cfg.STATE_ROOT == cfg.ROOT  # source tree keeps historical behavior
    assert cfg.OUTPUT == cfg.ROOT / "output"


def test_scripts_import_has_no_filesystem_side_effects(tmp_path):
    """Importing the shipped dev scripts must not create directories (Opus P2)."""
    code = (
        "import os, sys, pathlib\n"
        f"os.chdir({str(tmp_path)!r})\n"
        f"sys.path.insert(0, {str(Path(__file__).resolve().parent.parent)!r})\n"
        "import open_video.scripts.h3_agent\n"
        "import open_video.scripts.h3_generate_benchmark\n"
        "print(sorted(p.name for p in pathlib.Path('.').iterdir()))\n"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                         timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "[]", f"import created files: {out.stdout} {out.stderr}"
