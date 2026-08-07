#!/usr/bin/env bash
# Rebuild the OpenVideo lab runtime on a new machine.
set -Eeuo pipefail

PRODUCT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
LAB_ROOT="${OPEN_VIDEO_LAB:-$PRODUCT_ROOT/../lab}"
COMFYUI_DIR="${OPEN_VIDEO_COMFYUI_DIR:-$LAB_ROOT/ComfyUI}"
VENV_DIR="${OPEN_VIDEO_VENV_DIR:-$LAB_ROOT/venv}"
MODELS_DIR="${OPEN_VIDEO_MODELS:-$LAB_ROOT/h3_models}"
COMFYUI_REPO_URL="https://github.com/comfyanonymous/ComfyUI.git"
# Keep this in sync with scripts/install.sh. Verify a new full SHA upstream
# before bumping it, then refresh the verified runtime freeze record.
COMFYUI_COMMIT="14b05228cef127ce529bc0c08660770d4af3e9a8"
DRY_RUN=0

usage() {
    cat <<'EOF'
OpenVideo lab restore — rebuild ComfyUI, its venv, and H3 weights.

Usage:
  scripts/lab-restore.sh [--dry-run]

Environment overrides:
  OPEN_VIDEO_LAB             Runtime root (default: ../lab)
  OPEN_VIDEO_COMFYUI_DIR     ComfyUI checkout (default: $OPEN_VIDEO_LAB/ComfyUI)
  OPEN_VIDEO_VENV_DIR        Python venv (default: $OPEN_VIDEO_LAB/venv)
  OPEN_VIDEO_MODELS          H3 weights root (default: $OPEN_VIDEO_LAB/h3_models)
EOF
}

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) die "unknown argument: $1 (use --help)" ;;
    esac
done

if [[ "$DRY_RUN" -eq 1 ]]; then
    cat <<EOF
OpenVideo lab restore plan (dry-run; no changes and no weight download)
[1/5] Create or reuse runtime root: $LAB_ROOT
[2/5] Clone or reuse ComfyUI at:
       $COMFYUI_DIR
       repository: $COMFYUI_REPO_URL
       commit:    $COMFYUI_COMMIT
[3/5] Create or reuse Python venv: $VENV_DIR
[4/5] Install ComfyUI requirements from:
       $COMFYUI_DIR/requirements.txt
       and the ModelScope dependency used by h3_download.sh
[5/5] Resume H3 weights into:
       $MODELS_DIR
       via $PRODUCT_ROOT/scripts/h3_download.sh
EOF
    exit 0
fi

command -v git >/dev/null 2>&1 || die "git is required"
command -v python3 >/dev/null 2>&1 || die "python3 is required"
[[ -x "$PRODUCT_ROOT/scripts/h3_download.sh" ]] || die "missing executable scripts/h3_download.sh"

printf '[1/5] Creating or reusing runtime root: %s\n' "$LAB_ROOT"
mkdir -p "$LAB_ROOT"

printf '[2/5] Cloning or reusing ComfyUI at pinned commit %s\n' "$COMFYUI_COMMIT"
if [[ -d "$COMFYUI_DIR/.git" ]]; then
    printf '       Reusing existing git checkout: %s\n' "$COMFYUI_DIR"
elif [[ -e "$COMFYUI_DIR" ]]; then
    die "ComfyUI path exists but is not a git checkout: $COMFYUI_DIR"
else
    mkdir -p "$(dirname "$COMFYUI_DIR")"
    git clone --depth 1 "$COMFYUI_REPO_URL" "$COMFYUI_DIR"
fi
current_comfyui_commit="$(git -C "$COMFYUI_DIR" rev-parse HEAD 2>/dev/null || true)"
if [[ "$current_comfyui_commit" != "$COMFYUI_COMMIT" ]]; then
    git -C "$COMFYUI_DIR" fetch --depth 1 origin "$COMFYUI_COMMIT"
    git -C "$COMFYUI_DIR" checkout --detach "$COMFYUI_COMMIT"
fi
[[ "$(git -C "$COMFYUI_DIR" rev-parse HEAD)" == "$COMFYUI_COMMIT" ]] \
    || die "ComfyUI checkout is not at the required commit"
[[ -f "$COMFYUI_DIR/requirements.txt" ]] || die "ComfyUI requirements.txt is missing"

printf '[3/5] Creating or reusing Python venv: %s\n' "$VENV_DIR"
if [[ -e "$VENV_DIR" && ! -x "$VENV_DIR/bin/python" ]]; then
    die "venv path exists but has no executable Python: $VENV_DIR"
fi
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    python3 -m venv "$VENV_DIR"
fi
VENV_PY="$VENV_DIR/bin/python"

printf '[4/5] Installing ComfyUI requirements and weight-download dependency\n'
"$VENV_PY" -m pip install -r "$COMFYUI_DIR/requirements.txt"
"$VENV_PY" -m pip install modelscope

printf '[5/5] Resuming H3 weight download into %s\n' "$MODELS_DIR"
OPEN_VIDEO_PYTHON="$VENV_PY" \
OPEN_VIDEO_MODELS="$MODELS_DIR" \
OPEN_VIDEO_DOWNLOAD_HEARTBEAT="$LAB_ROOT/logs/h3_download_heartbeat.log" \
OPEN_VIDEO_DOWNLOAD_STATUS="$LAB_ROOT/logs/h3_download.status" \
    "$PRODUCT_ROOT/scripts/h3_download.sh"

printf 'Lab restore complete. ComfyUI=%s venv=%s models=%s\n' \
    "$COMFYUI_DIR" "$VENV_DIR" "$MODELS_DIR"
