#!/usr/bin/env bash
# =============================================================================
# open-video — one-click installer (the "Ollama for video" moment)
#
#   curl -fsSL https://open-video.ai/install.sh | bash
#   # or, from a checkout:
#   ./scripts/install.sh
#
# What it does (all idempotent + resumable — safe to re-run):
#   1. OS + GPU + tool detection            (Linux/macOS, NVIDIA/CUDA)
#   2. Python venv
#   3. ComfyUI (the engine) + deps
#   4. MiniMax H3 weights via aria2c        (INT8 ConvRot, ~54 GB, resumable)
#   5. Start the ComfyUI server
#   6. First test generation                ("Welcome to OpenVideo!")
#   7. Success banner + how to use
#
# Help:  ./scripts/install.sh --help
# Docs:  https://open-video.ai   (see docs/getting-started.md)
# License: Apache-2.0 (this installer) / model weights follow their own license.
# =============================================================================

# ---------------------------------------------------------------------------
# strict-ish mode: undefined vars are errors, pipe failures propagate. We do
# NOT use `set -e` globally — an installer must control its own error paths so
# it can give actionable messages instead of dying on a mid-pipe non-zero.
# ---------------------------------------------------------------------------
set -uo pipefail

# ---------------------------------------------------------------------------
# Defaults (overridable via flags below or env vars of the same name).
# ---------------------------------------------------------------------------
OV_ROOT_OVERRIDE=""
COMFYUI_DIR_OVERRIDE=""
VENV_DIR_OVERRIDE=""
MODELS_DIR_OVERRIDE=""
SOURCE="${OPEN_VIDEO_SOURCE:-hf}"          # hf | modelscope  (download mirror)
HOST="${OPEN_VIDEO_HOST:-127.0.0.1}"
PORT="${OPEN_VIDEO_PORT:-8188}"
QUANT="${OPEN_VIDEO_QUANT:-int8}"           # int8 (default) | nf4 (low-VRAM swap, manual)
FIRST_DURATION="${OPEN_VIDEO_FIRST_DURATION:-5}"
SKIP_DOWNLOAD=0
SKIP_COMFYUI_INSTALL=0
SKIP_SERVER=0
SKIP_GENERATE=0
DRY_ONLY=0
KEEP_SERVER=0
SAGE=0
ASSUME_YES=0
REPO_URL="${OPEN_VIDEO_REPO:-https://github.com/robotlearning123/open-video.git}"

# Verified byte sizes for the 4 default H3 INT8-ConvRot files (HF == ModelScope).
# Source: HF HEAD content-length + proven sibling-repo download receipt (53,889,785,072 B total ≈ 54 GB).
declare -A H3_SIZES=(
  ["diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors"]=20970379616
  ["text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors"]=27141342152
  ["vae/minimax_h3_video_vae_fp16.safetensors"]=5207808496
  ["vae/minimax_h3_audio_vae_fp32.safetensors"]=605254808
)
NEEDED_DISK_BYTES=64000000000   # 60 GiB headroom + outputs

# ---------------------------------------------------------------------------
# Pretty logging (auto-disables color when not on a TTY).
# ---------------------------------------------------------------------------
if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
    C_BOLD=$(tput bold); C_RED=$(tput setaf 1); C_GREEN=$(tput setaf 2)
    C_YELLOW=$(tput setaf 3); C_BLUE=$(tput setaf 4); C_CYAN=$(tput setaf 6)
    C_DIM=$(tput dim); C_RESET=$(tput sgr0)
else
    C_BOLD=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""; C_CYAN=""; C_DIM=""; C_RESET=""
fi
STEP_N=0
log()  { printf '%s\n' "$*"; }
step() { STEP_N=$((STEP_N+1)); printf '\n%s[%s%d%s/%s7%s] %s%s%s\n' \
         "$C_BOLD" "$C_CYAN" "$STEP_N" "$C_RESET" "$C_CYAN" "$C_RESET" "$C_BOLD" "$*" "$C_RESET"; }
ok()   { printf '  %s✓%s %s\n' "$C_GREEN" "$C_RESET" "$*"; }
info() { printf '  %s•%s %s\n' "$C_BLUE" "$C_RESET" "$*"; }
warn() { printf '  %s!%s %s%s%s\n' "$C_YELLOW" "$C_RESET" "$C_YELLOW" "$*" "$C_RESET" >&2; }
err()  { printf '  %s✗%s %s%s%s\n' "$C_RED" "$C_RESET" "$C_RED" "$*" "$C_RESET" >&2; }
die()  { err "$*"; err "Aborting. Re-run after fixing the above — progress is saved."; exit 1; }

# Ctrl-C / kill: tell the user how to resume instead of a scary traceback.
on_interrupt() {
    printf '\n'; warn "Interrupted. Re-run $0 to resume — every step is idempotent."; exit 130; }
trap on_interrupt INT TERM

have() { command -v "$1" >/dev/null 2>&1; }

# Ask y/N unless --yes. $1 = prompt. Returns 0 on yes.
# Reads from /dev/tty so prompts still work under `curl ... | bash` (where stdin
# is the piped script, not the terminal).
confirm() {
    if [[ "$ASSUME_YES" -eq 1 ]]; then return 0; fi
    local q ans
    q=$(printf '%s [y/N] ' "$1")
    if [[ -r /dev/tty ]]; then
        read -r -p "$q" ans </dev/tty
    else
        warn "$q (no tty — assuming no)"
        return 1
    fi
    [[ "$ans" =~ ^[Yy]([Ee][Ss])?$ ]]
}

usage() {
    cat <<'EOF'
open-video installer — zero to first video, one command.

USAGE
    ./scripts/install.sh [OPTIONS]
    curl -fsSL https://open-video.ai/install.sh | bash -s -- [OPTIONS]

WHAT IT DOES
    1. Detect OS / GPU (NVIDIA+CUDA) / tools
    2. Create a Python venv
    3. Clone + install ComfyUI (the engine) and open-video deps
    4. Download MiniMax H3 weights (INT8 ConvRot, ~54 GB) via aria2c (resumable)
    5. Start the ComfyUI server (http://127.0.0.1:8188)
    6. Run a first test generation → output/welcome.mp4
    7. Print success + how to use

OPTIONS
    -y, --yes                 Non-interactive (assume yes to prompts)
        --source hf|modelscope  Weight download mirror (default: hf; env OPEN_VIDEO_SOURCE)
        --host HOST            ComfyUI bind host  (default: 127.0.0.1; env OPEN_VIDEO_HOST)
        --port PORT            ComfyUI bind port  (default: 8188;   env OPEN_VIDEO_PORT)
        --quant int8|nf4       H3 quant to fetch (default: int8). nf4 = low-VRAM (~8 GB),
                               NOTE: nf4 swaps filenames — installer currently fetches int8
                               (the open-video default); nf4 is documented in docs/h3_ecosystem.md
        --duration SEC         First test video length in seconds (default: 5)
        --root PATH            open-video checkout to install into (default: auto-detect)
        --comfyui-dir PATH     ComfyUI checkout path (default: <root>/ComfyUI)
        --venv PATH            venv path (default: <root>/.venv)
        --models-dir PATH      model weights root (default: <comfyui>/models)
        --sage                 Pass --use-sage-attention to ComfyUI (faster; needs sage attn installed)
        --skip-download        Skip H3 weight download (bring your own weights)
        --skip-comfyui-install Skip cloning/installing ComfyUI (use an existing checkout)
        --skip-server          Don't start ComfyUI (assume an external server is running)
        --skip-generate        Don't run the first test generation
        --dry-run              Orchestrator --dry-run smoke test only (no GPU time spent)
        --keep-server          Leave ComfyUI running after the install (default: stops it)
    -h, --help                 Show this help

ENVIRONMENT
    OPEN_VIDEO_SOURCE / _HOST / _PORT / _QUANT / _FIRST_DURATION / _REPO
        mirror the flags above.

EXIT CODES
    0  success (first video generated, or everything set up as requested)
    10 missing required tool / unsupported OS
    11 insufficient disk space
    20 no NVIDIA GPU detected (generation skipped; setup may still finish)
    30 ComfyUI failed to start or become healthy
    40 weight download failed after retries
    50 first generation failed (stack is up; prints the exact retry command)
    99 canceled by user
EOF
}

# ---------------------------------------------------------------------------
# arg parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes) ASSUME_YES=1; shift ;;
        --source) SOURCE="$2"; shift 2 ;;
        --host) HOST="$2"; shift 2 ;;
        --port) PORT="$2"; shift 2 ;;
        --quant) QUANT="$2"; shift 2 ;;
        --duration) FIRST_DURATION="$2"; shift 2 ;;
        --root) OV_ROOT_OVERRIDE="$2"; shift 2 ;;
        --comfyui-dir) COMFYUI_DIR_OVERRIDE="$2"; shift 2 ;;
        --venv) VENV_DIR_OVERRIDE="$2"; shift 2 ;;
        --models-dir) MODELS_DIR_OVERRIDE="$2"; shift 2 ;;
        --sage) SAGE=1; shift ;;
        --skip-download) SKIP_DOWNLOAD=1; shift ;;
        --skip-comfyui-install) SKIP_COMFYUI_INSTALL=1; shift ;;
        --skip-server) SKIP_SERVER=1; shift ;;
        --skip-generate) SKIP_GENERATE=1; shift ;;
        --dry-run) DRY_ONLY=1; shift ;;
        --keep-server) KEEP_SERVER=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) err "Unknown option: $1"; usage; exit 2 ;;
    esac
done

case "$SOURCE" in
    hf|modelscope) ;;
    *) die "--source must be 'hf' or 'modelscope' (got '$SOURCE')" ;;
esac

# ===========================================================================
# Banner
# ===========================================================================
print_banner() {
    cat <<EOF

${C_BOLD}${C_CYAN}   ___                    ____               ${C_RESET}
${C_BOLD}${C_CYAN}  / _ \ _ __   ___ _ __ / ___| _____ __ __  ${C_RESET}
${C_BOLD}${C_CYAN} | | | | '_ \ / _ \ '_ \\___ \/_-<_\ V  V / ${C_RESET}
${C_BOLD}${C_CYAN} | |_| | |_) |  __/ | | |___/ |__| \_/\_/  ${C_RESET}
${C_BOLD}${C_CYAN}  \___/| .__/ \___|_| |_|_____|           ${C_RESET}
${C_BOLD}${C_CYAN}       |_|                                ${C_RESET}

${C_BOLD}open-video${C_RESET} — open-source autonomous video generation.
${C_DIM}Engine: ComfyUI   Model: MiniMax H3 (INT8 ConvRot)   ~54 GB to download${C_RESET}
EOF
}

# ===========================================================================
# 0. Resolve paths: standalone (curl|bash) vs in-repo (./scripts/install.sh)
# ===========================================================================
resolve_root() {
    if [[ -n "$OV_ROOT_OVERRIDE" ]]; then
        OV_ROOT="$OV_ROOT_OVERRIDE"
    else
        # Script lives at <root>/scripts/install.sh. Find the repo root by
        # looking for cli/open_video.py relative to this file's dir.
        local script_dir
        script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
        if [[ -f "$script_dir/../cli/open_video.py" ]]; then
            OV_ROOT=$(cd "$script_dir/.." && pwd)
        else
            # Standalone run (e.g. curl|bash): clone the repo first.
            OV_ROOT="${OV_ROOT:-$(pwd)/open-video}"
            warn "Running standalone — cloning open-video into: $OV_ROOT"
            if [[ -d "$OV_ROOT/.git" ]]; then
                ok "Reusing existing checkout at $OV_ROOT"
            else
                if ! have git; then die "git is required to clone open-video. Install git and re-run."; fi
                git clone --depth 1 "$REPO_URL" "$OV_ROOT" \
                    || die "git clone failed. Set --root to an existing checkout or OPEN_VIDEO_REPO."
            fi
        fi
    fi
    OV_ROOT=$(cd "$OV_ROOT" && pwd) || die "root path not accessible: $OV_ROOT"
    [[ -f "$OV_ROOT/cli/open_video.py" ]] \
        || die "$OV_ROOT does not look like the open-video repo (no cli/open_video.py)."

    COMFYUI_DIR="${COMFYUI_DIR_OVERRIDE:-$OV_ROOT/ComfyUI}"
    VENV_DIR="${VENV_DIR_OVERRIDE:-$OV_ROOT/.venv}"
    MODELS_DIR="${MODELS_DIR_OVERRIDE:-$COMFYUI_DIR/models}"
    COMFYUI_LOG="$OV_ROOT/.cache/comfyui.log"
    ARIA_LIST="$OV_ROOT/.cache/aria2-h3.list"
    mkdir -p "$OV_ROOT/.cache" "$OV_ROOT/output"
    ok "open-video root:   $OV_ROOT"
    ok "ComfyUI:           $COMFYUI_DIR"
    ok "venv:              $VENV_DIR"
    ok "models:            $MODELS_DIR"
}

# ===========================================================================
# 1. Detect OS / GPU / required tools
# ===========================================================================
detect_platform() {
    step "Checking OS, GPU, and required tools"

    OS_KIND="unknown"; PKG_MGR=""
    case "$(uname -s)" in
        Linux*)
            OS_KIND="linux"
            if have apt-get; then PKG_MGR="apt"
            elif have dnf; then PKG_MGR="dnf"
            elif have yum; then PKG_MGR="yum"
            elif have pacman; then PKG_MGR="pacman"
            elif have apk; then PKG_MGR="apk"
            fi
            info "OS: Linux (pkg manager: ${PKG_MGR:-none found})" ;;
        Darwin*)
            OS_KIND="macos"
            PKG_MGR=$(have brew && echo brew || echo "")
            info "OS: macOS (brew: ${PKG_MGR:-not found})" ;;
        *) warn "OS '$(uname -s)' is not directly supported. Proceeding best-effort." ;;
    esac

    # --- tools: git, python3, curl, ffmpeg, aria2c ---
    # NOTE: the binary is `aria2c`; the OS package is `aria2`. Check the binary,
    # request the package name.
    local missing=()
    have git    || missing+=(git)
    have python3 || missing+=(python3)
    have curl   || missing+=(curl)
    have ffmpeg || missing+=(ffmpeg)
    have aria2c || missing+=(aria2)

    if [[ ${#missing[@]} -gt 0 ]]; then
        warn "Missing tools: ${missing[*]}"
        install_tools "${missing[@]}" || die "Install the missing tools (${missing[*]}) and re-run."
    fi

    # Re-check the actual binaries (aria2c, not the package name).
    local still_missing=()
    have git    || still_missing+=(git)
    have python3 || still_missing+=(python3)
    have curl   || still_missing+=(curl)
    have ffmpeg || still_missing+=(ffmpeg)
    have aria2c || still_missing+=(aria2)
    if [[ ${#still_missing[@]} -gt 0 ]]; then
        err "Still missing: ${still_missing[*]}."
        case "$OS_KIND" in
            linux)  err "Try:  sudo apt-get install -y ${still_missing[*]}" ;;
            macos)  err "Try:  brew install ${still_missing[*]}" ;;
        esac
        exit 10
    fi

    local py_vmajor py_vminor
    py_vmajor=$(python3 -c 'import sys;print(sys.version_info[0])' 2>/dev/null || echo 0)
    py_vminor=$(python3 -c 'import sys;print(sys.version_info[1])' 2>/dev/null || echo 0)
    if [[ "$py_vmajor" -lt 3 || "$py_vminor" -lt 10 ]]; then
        die "Python 3.10+ required (found ${py_vmajor}.${py_vminor})."
    fi
    ok "git $(git --version 2>&1 | awk '{print $3}' | head -1), Python ${py_vmajor}.${py_vminor}, aria2c, ffmpeg present"

    # --- GPU: NVIDIA + CUDA is the supported generation path ---
    HAVE_NVIDIA=0; GPU_NAME="none"; VRAM_MIB=0
    if have nvidia-smi; then
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        VRAM_MIB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
        if [[ -n "$GPU_NAME" ]]; then
            HAVE_NVIDIA=1
            ok "NVIDIA GPU: $GPU_NAME ($((VRAM_MIB)) MiB VRAM)"
            if have nvcc; then info "CUDA toolkit (nvcc) present"; fi
            # Driver-side CUDA is enough for PyTorch wheels (they bundle their own).
            local drv_cc
            drv_cc=$(nvidia-smi 2>/dev/null | grep -oE 'CUDA Version: [0-9.]+' | head -1)
            [[ -n "$drv_cc" ]] && info "Driver reports $drv_cc (sufficient for bundled CUDA wheels)"
            if [[ "$VRAM_MIB" -gt 0 && "$VRAM_MIB" -lt 10000 ]]; then
                warn "Only ${VRAM_MIB} MiB VRAM — INT8 (~21 GB) will need --lowvram model offloading"
                warn "or the NF4 quant (~8 GB). See docs/h3_ecosystem.md."
            fi
        fi
    elif [[ "$OS_KIND" == "macos" ]]; then
        local chip
        chip=$(uname -m)
        GPU_NAME="Apple Silicon ($chip)"
        warn "macOS detected ($chip). H3 generation on macOS is community-only (minimax-h3-mlx)"
        warn "and not wired into the CLI yet. Setup will finish; generation will be skipped."
    else
        warn "No NVIDIA GPU detected (no nvidia-smi). open-video can still plan/validate prompts,"
        warn "but H3 generation needs an NVIDIA GPU. Generation will be skipped."
    fi

    # --- disk space ---
    check_disk || exit 11
}

install_tools() {
    local tools=("$@")
    [[ -z "$PKG_MGR" ]] && { warn "No supported package manager found — cannot auto-install."; return 1; }
    if [[ "$EUID" -ne 0 ]]; then
        confirm "Install ${tools[*]} via $PKG_MGR (needs sudo)?" || return 1
    fi
    case "$PKG_MGR" in
        apt)   sudo apt-get update -y && sudo apt-get install -y "${tools[@]}" ;;
        dnf)   sudo dnf install -y "${tools[@]}" ;;
        yum)   sudo yum install -y "${tools[@]}" ;;
        pacman) sudo pacman -S --noconfirm --needed "${tools[@]}" ;;
        apk)   sudo apk add --no-cache "${tools[@]}" ;;
        brew)  brew install "${tools[@]}" ;;
        *) warn "Unknown package manager '$PKG_MGR'"; return 1 ;;
    esac
}

check_disk() {
    # df -P column 4 is in 1K-blocks; convert to bytes for comparison.
    local avail_kb avail_bytes
    avail_kb=$(df -P "$OV_ROOT" 2>/dev/null | awk 'NR==2{print $4}')
    if [[ -z "$avail_kb" ]]; then warn "Could not measure free disk — skipping space check."; return 0; fi
    avail_bytes=$((avail_kb * 1024))
    if [[ "$avail_bytes" -lt "$NEEDED_DISK_BYTES" ]]; then
        err "Not enough free disk: need ~$((NEEDED_DISK_BYTES/1024/1024/1024)) GiB, have $((avail_bytes/1024/1024/1024)) GiB on $(df -P "$OV_ROOT" | awk 'NR==2{print $6}')."
        err "Point --root (or OPEN_VIDEO_HOME) at a larger volume, or pass --skip-download."
        return 1
    fi
    ok "Free disk: ~$((avail_bytes/1024/1024/1024)) GiB (need ~60 GiB for weights + outputs)"
}

# ===========================================================================
# 2. Python venv
# ===========================================================================
make_venv() {
    step "Creating Python virtual environment"
    if [[ -x "$VENV_DIR/bin/python" ]]; then
        ok "venv already exists at $VENV_DIR (reusing)"
    else
        python3 -m venv "$VENV_DIR" || die "venv creation failed at $VENV_DIR"
        ok "venv created at $VENV_DIR"
    fi
    VENVPY="$VENV_DIR/bin/python"
    # Bootstrap pip (some distros ship venv without pip).
    if ! "$VENVPY" -m pip --version >/dev/null 2>&1; then
        "$VENVPY" -m ensurepip --upgrade >/dev/null 2>&1 || true
    fi
    "$VENVPY" -m pip install --upgrade pip wheel setuptools >/dev/null \
        || warn "pip self-upgrade failed (continuing with bundled pip)"
    info "pip: $("$VENVPY" -m pip --version 2>&1)"
}

# ===========================================================================
# 3. ComfyUI + open-video deps
# ===========================================================================
install_engine() {
    step "Installing ComfyUI (the engine) + open-video deps"

    if [[ "$SKIP_COMFYUI_INSTALL" -eq 1 ]]; then
        ok "--skip-comfyui-install: using existing ComfyUI at $COMFYUI_DIR"
        [[ -f "$COMFYUI_DIR/main.py" ]] || die "--skip-comfyui-install but no ComfyUI/main.py at $COMFYUI_DIR"
    else
        if [[ -f "$COMFYUI_DIR/main.py" ]]; then
            ok "ComfyUI already cloned at $COMFYUI_DIR (reusing)"
        else
            mkdir -p "$(dirname "$COMFYUI_DIR")"
            git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR" \
                || die "ComfyUI clone failed."
            ok "ComfyUI cloned to $COMFYUI_DIR"
        fi
    fi

    info "Installing ComfyUI Python deps (torch + transformers + ...) — this is the largest pip step"
    if ! "$VENVPY" -m pip install -r "$COMFYUI_DIR/requirements.txt" >/tmp/ov_pip_comfy.log 2>&1; then
        tail -n 20 /tmp/ov_pip_comfy.log >&2 || true
        die "pip install of ComfyUI requirements failed (log: /tmp/ov_pip_comfy.log)."
    fi
    ok "ComfyUI deps installed"
    info "torch: $("$VENVPY" -c 'import torch;print(torch.__version__)' 2>/dev/null || echo 'import failed')"

    # open-video orchestrator is stdlib-only (dependencies = [] in pyproject.toml),
    # but install it editable so the user gets the `open-video` console command.
    # Non-fatal: if the editable install fails (old setuptools, etc.), we still run
    # fine via `python cli/open_video.py`.
    if [[ -f "$OV_ROOT/pyproject.toml" ]]; then
        if "$VENVPY" -m pip install -e "$OV_ROOT" >/tmp/ov_pip_ov.log 2>&1; then
            ok "open-video installed (editable) — 'open-video' command is on the venv PATH"
        else
            warn "pip install -e . failed (log: /tmp/ov_pip_ov.log) — falling back to 'python cli/open_video.py'"
        fi
    elif [[ -f "$OV_ROOT/requirements.txt" ]]; then
        "$VENVPY" -m pip install -r "$OV_ROOT/requirements.txt" \
            || die "open-video requirements.txt install failed."
        ok "open-video deps installed"
    else
        ok "open-video orchestrator is stdlib-only (no pip deps) — nothing extra to install"
    fi

    # Smoke-test the orchestrator + H3 backend import path.
    if ! ( cd "$OV_ROOT" && "$VENVPY" cli/open_video.py list-models >/tmp/ov_models.log 2>&1 ); then
        tail -n 20 /tmp/ov_models.log >&2 || true
        die "open-video self-test failed (could not list models). See /tmp/ov_models.log"
    fi
    ok "open-video orchestrator OK ($(grep -c -E '^[[:space:]]*h3[[:space:]]' /tmp/ov_models.log 2>/dev/null || echo ?) backend(s) visible)"
}

# ===========================================================================
# 4. Download H3 weights (aria2c, resumable)
# ===========================================================================
url_for() {  # $1 = relative path under repo; honor --source
    local rel="$1"
    case "$SOURCE" in
        hf)
            echo "https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/$rel" ;;
        modelscope)
            echo "https://www.modelscope.cn/api/v1/models/Comfy-Org/MiniMax-H3/repo?Revision=master&FilePath=$rel" ;;
    esac
}

download_weights() {
    step "Downloading MiniMax H3 weights (INT8 ConvRot, ~54 GB) via aria2c"

    if [[ "$QUANT" != "int8" ]]; then
        warn "--quant $QUANT requested: this installer fetches the INT8 set (the open-video default)."
        warn "For NF4/W4 swaps, see docs/h3_ecosystem.md and place files under $MODELS_DIR manually."
    fi
    if [[ "$SKIP_DOWNLOAD" -eq 1 ]]; then
        ok "--skip-download: skipping weight fetch. Make sure the 4 files are in place under $MODELS_DIR"
        return 0
    fi

    # Build the aria2 input list, skipping any file already at full size (resume).
    : > "$ARIA_LIST"
    local pending=0 already=0
    for rel in "${!H3_SIZES[@]}"; do
        local want=${H3_SIZES[$rel]}
        local dst="$MODELS_DIR/$rel"
        local got=0
        [[ -f "$dst" ]] && got=$(stat -c%s "$dst" 2>/dev/null || stat -f%z "$dst" 2>/dev/null || echo 0)
        if [[ "$got" -eq "$want" ]]; then
            local hsize
            hsize=$(numfmt --to=iec "$want" 2>/dev/null || printf '%s bytes' "$want")
            already=$((already+1))
            ok "already complete: $rel ($hsize)"
            continue
        fi
        pending=$((pending+1))
        # aria2 input-file format: URL line, then 2-space-indented dir=/out=
        {
            url_for "$rel"
            echo "  dir=$(dirname "$dst")"
            echo "  out=$(basename "$rel")"
        } >> "$ARIA_LIST"
    done

    if [[ "$pending" -eq 0 ]]; then
        ok "All 4 H3 weight files already present at full size — nothing to download."
        return 0
    fi
    info "$already file(s) already complete; downloading $pending file(s) (~54 GB total)."
    info "Mirror: $SOURCE   (switch with --source hf|modelscope)"
    info "Resumable: re-running this script continues partial downloads. Log: tail -f $COMFYUI_LOG"
    [[ "$already" -gt 0 ]] || warn "First-time download is ~54 GB — go get coffee. This is the long step."

    local aria_opts=(
        -c                               # continue/resume partial downloads
        -x16 -s16 -k1M                   # 16 connections, 16 splits, 1 MiB pieces
        --file-allocation=none
        --max-tries=0 --retry-wait=3     # infinite retries, 3s between (survives drops)
        --auto-file-renaming=false
        --allow-overwrite=true
        --summary-interval=10            # progress line every 10s
        --console-log-level=notice
        --download-result=hide
        -i "$ARIA_LIST"
    )

    # aria2 exits 0 on full success; non-zero means at least one file incomplete.
    if ! aria2c "${aria_opts[@]}"; then
        # Verify how far we got; only hard-fail if NOTHING completed this pass AND
        # nothing is already complete.
        local any_complete=0
        for rel in "${!H3_SIZES[@]}"; do
            local dst="$MODELS_DIR/$rel"
            local got=0
            [[ -f "$dst" ]] && got=$(stat -c%s "$dst" 2>/dev/null || stat -f%z "$dst" 2>/dev/null || echo 0)
            [[ "$got" -eq "${H3_SIZES[$rel]}" ]] && any_complete=1
        done
        if [[ "$any_complete" -eq 0 ]]; then
            err "aria2c failed and no file is complete yet. Check your network/mirror."
            if [[ "$SOURCE" == "hf" ]]; then
                err "Retry with:  --source modelscope"
            else
                err "Retry with:  --source hf"
            fi
            exit 40
        fi
        warn "aria2c reported incomplete — some files finished, some didn't. Re-run to resume."
    fi

    # Final verification: every file must be at its exact expected byte size.
    verify_weights || exit 40
    ok "H3 weights complete and size-verified (~54 GB)"
}

verify_weights() {
    local bad=0
    for rel in "${!H3_SIZES[@]}"; do
        local want=${H3_SIZES[$rel]}
        local dst="$MODELS_DIR/$rel"
        local got=0
        [[ -f "$dst" ]] && got=$(stat -c%s "$dst" 2>/dev/null || stat -f%z "$dst" 2>/dev/null || echo 0)
        if [[ "$got" -ne "$want" ]]; then
            err "size mismatch: $rel — got $got, expected $want"
            bad=1
        fi
    done
    return $bad
}

# ===========================================================================
# 5. Start ComfyUI
# ===========================================================================
COMFY_PID=""

start_server() {
    step "Starting ComfyUI server on http://$HOST:$PORT"

    # If something is already serving on the port, reuse it.
    if curl -sf "http://$HOST:$PORT/system_stats" >/dev/null 2>&1; then
        ok "A server is already healthy at http://$HOST:$PORT — reusing it"
        return 0
    fi

    if [[ "$SKIP_SERVER" -eq 1 ]]; then
        warn "--skip-server: not starting ComfyUI. Assuming an external server will be at http://$HOST:$PORT"
        return 0
    fi

    [[ "$HAVE_NVIDIA" -eq 1 ]] \
        || die "ComfyUI generation needs an NVIDIA GPU. Re-run with --skip-server and --skip-generate."

    local sage_args=""
    [[ "$SAGE" -eq 1 ]] && sage_args="--use-sage-attention"

    info "Launching ComfyUI (log: $COMFYUI_LOG). First load of a 21 GB model is slow."
    mkdir -p "$(dirname "$COMFYUI_LOG")"
    : > "$COMFYUI_LOG"
    local pid_file="$OV_ROOT/.cache/comfyui.pid"
    rm -f "$pid_file"
    # Launch detached from ComfyUI's own dir so it finds models/, custom_nodes/, etc.
    # Capture the PID via a file (robust vs pipe-to-subshell read races).
    ( cd "$COMFYUI_DIR" \
        && nohup "$VENVPY" main.py --listen "$HOST" --port "$PORT" --lowvram $sage_args \
           >"$COMFYUI_LOG" 2>&1 & echo $! > "$pid_file" )
    local _i
    for _i in 1 2 3 4 5 6 7 8 9 10; do [[ -s "$pid_file" ]] && break; sleep 0.2; done
    COMFY_PID=$(tr -dc '0-9' < "$pid_file" 2>/dev/null || true)
    [[ -n "$COMFY_PID" ]] || { err "Failed to capture the ComfyUI process PID."; exit 30; }

    if ! wait_for_comfyui; then
        err "ComfyUI did not become healthy within the timeout. Last log lines:"
        tail -n 30 "$COMFYUI_LOG" >&2 || true
        if [[ "$SAGE" -eq 1 ]]; then
            warn "--sage was set; sage-attention may be missing. Retry WITHOUT --sage."
        fi
        stop_server_if_ours
        exit 30
    fi
    ok "ComfyUI healthy (PID $COMFY_PID) at http://$HOST:$PORT"
}

wait_for_comfyui() {
    local deadline=$(( $(date +%s) + 240 ))   # up to 4 min for cold start + torch import
    while [[ $(date +%s) -lt $deadline ]]; do
        if ! kill -0 "$COMFY_PID" 2>/dev/null; then
            err "ComfyUI process exited early. See $COMFYUI_LOG"
            return 1
        fi
        if curl -sf "http://$HOST:$PORT/system_stats" >/dev/null 2>&1; then
            return 0
        fi
        sleep 3
    done
    return 1
}

stop_server_if_ours() {
    if [[ "$KEEP_SERVER" -eq 1 ]]; then
        [[ -n "$COMFY_PID" ]] && ok "--keep-server: leaving ComfyUI running (PID $COMFY_PID)"
        return 0
    fi
    if [[ -n "$COMFY_PID" ]] && kill -0 "$COMFY_PID" 2>/dev/null; then
        kill "$COMFY_PID" 2>/dev/null || true
        sleep 2
        kill -9 "$COMFY_PID" 2>/dev/null || true
        ok "Stopped ComfyUI (PID $COMFY_PID)"
    fi
    rm -f "$OV_ROOT/.cache/comfyui.pid" 2>/dev/null || true
}

# ===========================================================================
# 6. First test generation
# ===========================================================================
first_generation() {
    step "First test generation — Welcome to OpenVideo!"

    if [[ "$SKIP_GENERATE" -eq 1 ]]; then
        ok "--skip-generate: not running a test generation."
        return 0
    fi
    if [[ "$HAVE_NVIDIA" -ne 1 ]]; then
        warn "No NVIDIA GPU — skipping generation. Verify the stack with:"
        warn "    (cd $OV_ROOT && $VENVPY cli/open_video.py \"a sunset\" --dry-run)"
        return 0
    fi

    # Fast smoke test first: validates orchestrator + ComfyUI wiring, no GPU time.
    info "Smoke test (--dry-run): validates the plan + ComfyUI health without spending GPU."
    if ( cd "$OV_ROOT" && "$VENVPY" cli/open_video.py "$WELCOME_PROMPT" --dry-run \
            --server "http://$HOST:$PORT" >/tmp/ov_dryrun.log 2>&1 ); then
        ok "dry-run passed — orchestrator + ComfyUI are wired correctly"
    else
        err "dry-run failed. Last log lines:"
        tail -n 20 /tmp/ov_dryrun.log >&2 || true
        stop_server_if_ours
        exit 50
    fi

    if [[ "$DRY_ONLY" -eq 1 ]]; then
        ok "--dry-run mode: stopping after the smoke test (no video generated)."
        stop_server_if_ours
        return 0
    fi

    # Real generation. First run loads ~21 GB diffusion + ~27 GB TE (slow).
    printf '\n  %sWelcome to OpenVideo! Generating your first video...%s\n' "$C_BOLD$C_GREEN" "$C_RESET"
    info "Prompt: \"$WELCOME_PROMPT\""
    info "Duration: ${FIRST_DURATION}s   Output: $OV_ROOT/output/welcome.mp4"
    warn "First generation takes a few minutes (cold model load). Subsequent runs are faster."

    local t0
    t0=$(date +%s)
    if ( cd "$OV_ROOT" && "$VENVPY" cli/open_video.py "$WELCOME_PROMPT" \
            --duration "$FIRST_DURATION" --aspect 16:9 \
            --output output/welcome.mp4 --server "http://$HOST:$PORT" \
            >/tmp/ov_generate.log 2>&1 ); then
        local elapsed=$(( $(date +%s) - t0 ))
        if [[ -f "$OV_ROOT/output/welcome.mp4" ]]; then
            ok "FIRST VIDEO GENERATED in ${elapsed}s -> $OV_ROOT/output/welcome.mp4"
        else
            warn "CLI exited 0 but no file at output/welcome.mp4 (check /tmp/ov_generate.log)"
        fi
    else
        err "Generation failed. Last log lines:"
        tail -n 30 /tmp/ov_generate.log >&2 || true
        err "The stack is up — retry generation with:"
        err "    (cd $OV_ROOT && $VENVPY cli/open_video.py \"$WELCOME_PROMPT\" \\"
        err "        --duration $FIRST_DURATION --server http://$HOST:$PORT)"
        stop_server_if_ours
        exit 50
    fi
}

# ===========================================================================
# 7. Success banner
# ===========================================================================
print_success() {
    local vid_line=""
    [[ -f "$OV_ROOT/output/welcome.mp4" ]] \
        && vid_line="  ${C_GREEN}Your first video:${C_RESET} $OV_ROOT/output/welcome.mp4"$'\n'
    # The venv python is always set by make_venv in a real run; default only
    # protects the success banner from ever crashing. Prefer the polished
    # `open-video` entry point when the editable install added it.
    local py="${VENVPY:-python3}"
    local ov_cmd
    if [[ -x "${VENV_DIR:-$OV_ROOT/.venv}/bin/open-video" ]]; then
        ov_cmd="${VENV_DIR:-$OV_ROOT/.venv}/bin/open-video"
    else
        ov_cmd="$py $OV_ROOT/cli/open_video.py"
    fi
    cat <<EOF

${C_BOLD}${C_GREEN}==============================================================${C_RESET}
${C_BOLD}${C_GREEN}  ✓ open-video is ready. Welcome to OpenVideo!${C_RESET}
${C_BOLD}${C_GREEN}==============================================================${C_RESET}

${vid_line}${C_BOLD}Generate more:${C_RESET}
  $ov_cmd "a neon koi swimming through rain, slow dolly" --duration 8 --output output/koi.mp4

${C_BOLD}Start ComfyUI again later:${C_RESET}
  cd "$COMFYUI_DIR" && $py main.py --listen $HOST --port $PORT --lowvram

${C_BOLD}Plan/validate without spending GPU:${C_RESET}
  $ov_cmd "a concept" --dry-run

${C_BOLD}Browse prompt recipes & backends:${C_RESET}
  $ov_cmd list-presets && $ov_cmd list-models

${C_BOLD}Help & docs:${C_RESET}  https://open-video.ai   (docs/getting-started.md, docs/h3_ecosystem.md)
${C_BOLD}Community:${C_RESET}     Discord / GitHub Discussions linked from the README.

${C_DIM}Re-run this installer any time to update or repair — every step is resumable.${C_RESET}
EOF
}

# ===========================================================================
# main
# ===========================================================================
main() {
    print_banner
    WELCOME_PROMPT="A cinematic shot of golden sunrise over a calm ocean, gentle waves shimmering, slow camera push-in, warm light, serene and hopeful mood, welcome to OpenVideo."

    resolve_root
    detect_platform

    make_venv
    install_engine
    download_weights

    if [[ "$DRY_ONLY" -eq 1 && "$HAVE_NVIDIA" -ne 1 ]]; then
        # No GPU + dry-only: we can still smoke-test the orchestrator without a server.
        step "First test generation — dry-run (no GPU)"
        ( cd "$OV_ROOT" && "$VENVPY" cli/open_video.py "$WELCOME_PROMPT" --dry-run \
            --server "http://$HOST:$PORT" ) || warn "dry-run needs ComfyUI; start it to validate fully."
        print_success
        return 0
    fi

    start_server
    first_generation
    stop_server_if_ours
    print_success
}

main "$@"
