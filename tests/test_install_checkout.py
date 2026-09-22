"""Execute the standalone installer against reused checkouts without network/GPU."""
import re
import shlex
import subprocess
from pathlib import Path

import pytest


INSTALL = Path(__file__).resolve().parents[1] / "scripts" / "install.sh"


def run_resolver(tmp_path, *, complete, git_file=False):
    checkout = tmp_path / "existing checkout"
    (checkout / "cli").mkdir(parents=True)
    (checkout / "cli/open_video.py").write_text("# existing user source\n")
    (checkout / "local-notes.txt").write_text("uncommitted user work\n")
    if git_file:
        (checkout / ".git").write_text("gitdir: elsewhere\n")
    else:
        (checkout / ".git").mkdir()
    if complete:
        for name in ("core/resources.py", "models/h3_manifest.json",
                     "scripts/verify_h3_manifest.py", "scripts/comfyui.pin"):
            path = checkout / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture\n")
    source = INSTALL.read_text()
    functions = "\n".join(
        re.search(rf"^{name}\(\) \{{.*?^\}}", source, re.M | re.S).group()
        for name in ("load_comfyui_pin", "resolve_root")
    )
    harness = tmp_path / "standalone.sh"
    harness.write_text(f"""set -uo pipefail
OV_ROOT={shlex.quote(str(checkout))}
OV_ROOT_OVERRIDE=''
COMFYUI_DIR_OVERRIDE=''
VENV_DIR_OVERRIDE=''
MODELS_DIR_OVERRIDE=''
REPO_URL='https://example.invalid/no-network'
info() {{ :; }}
ok() {{ printf '%s\\n' "$*"; }}
warn() {{ printf '%s\\n' "$*" >&2; }}
die() {{ printf '%s\\n' "$*" >&2; exit 1; }}
have() {{ return 0; }}
git() {{ printf 'unexpected git invocation\\n' >&2; exit 99; }}
{functions}
resolve_root
""")
    result = subprocess.run(["bash", str(harness)], text=True, capture_output=True)
    assert (checkout / "local-notes.txt").read_text() == "uncommitted user work\n"
    assert (checkout / "cli/open_video.py").read_text() == "# existing user source\n"
    return result, checkout


def test_old_checkout_stops_before_setup_with_update_instruction(tmp_path):
    result, checkout = run_resolver(tmp_path, complete=False)
    assert result.returncode == 1
    assert "git pull --ff-only" in result.stderr
    assert "does not update product source automatically" in result.stderr
    assert not (checkout / ".cache").exists()
    assert not (checkout / "output").exists()


@pytest.mark.parametrize("git_file", [False, True])
def test_current_checkout_is_reused_without_git_mutation(tmp_path, git_file):
    result, checkout = run_resolver(tmp_path, complete=True, git_file=git_file)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "without updating its source" in result.stdout
    assert (checkout / ".cache").is_dir()
