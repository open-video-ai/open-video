#!/usr/bin/env bash
# Resolve lab root from this script location (no hard-coded machine path)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export ROOT
# Resilient MiniMax H3 weight download via ModelScope (China mirror).
# Loops snapshot_download until all 4 target files are present at full size,
# writing a heartbeat log and a status file. Survives transient network drops.
# Re-runnable: snapshot_download resumes partial files.
set -u
cd "$ROOT"
# Prefer active venv / PATH; no machine-specific hardcode
PY="${OPEN_VIDEO_PYTHON:-${PYTHON:-$(command -v python3 || command -v python)}}"
LOCAL="${OPEN_VIDEO_MODELS:-h3_models}"
HEART="${OPEN_VIDEO_DOWNLOAD_HEARTBEAT:-logs/h3_download_heartbeat.log}"
STATUS="${OPEN_VIDEO_DOWNLOAD_STATUS:-logs/h3_download.status}"
mkdir -p "$LOCAL" "$(dirname "$HEART")" "$(dirname "$STATUS")"

# Shared manifest: paths/sizes/URLs/hashes for the 4 H3 files (single source
# of truth, also used by install.sh and pinokio_install.js).
MANIFEST="$ROOT/models/h3_manifest.json"
H3_VERIFY="$ROOT/scripts/verify_h3_manifest.py"

# Validate the shared manifest before entering the retry loop.
"$PY" "$H3_VERIFY" paths "$MANIFEST" >/dev/null || exit 1

echo "$(date -Iseconds) START resilient H3 download loop (4 files, ~54GB)" >> "$HEART"
while true; do
  $PY - "$LOCAL" "$MANIFEST" >> "$HEART" 2>&1 <<'PY'
import json, sys
from modelscope import snapshot_download
local, manifest = sys.argv[1], sys.argv[2]
try:
    snapshot_download('Comfy-Org/MiniMax-H3',
                      allow_patterns=list(json.load(open(manifest))["files"]),
                      local_dir=local)
    print('PASS')
except Exception as e:
    print('ERR', repr(e))
PY

  # finalize: modelscope stages completed files under ._____temp; move to final paths
  while IFS= read -r path; do
    final="$LOCAL/$path"; tmp="$LOCAL/._____temp/$path"
    if [ ! -f "$final" ] && [ -f "$tmp" ]; then
      mkdir -p "$(dirname "$final")"; mv "$tmp" "$final" && echo "$(date -Iseconds) finalized $path" >> "$HEART"
    fi
  done < <($PY "$H3_VERIFY" paths "$MANIFEST")
  all_ok=1
  $PY "$H3_VERIFY" check --size-only --manifest "$MANIFEST" --models-dir "$LOCAL" >/dev/null 2>&1 || all_ok=0
  sz=$(du -sh "$LOCAL" 2>/dev/null | cut -f1)
  echo "$(date -Iseconds) total=$sz all_complete=$all_ok" >> "$HEART"
  if [ "$all_ok" = "1" ]; then
    # Sizes complete — now require full integrity verification (sha256/commit
    # from the manifest; fails closed while release metadata is pending).
    if $PY "$H3_VERIFY" check --manifest "$MANIFEST" --models-dir "$LOCAL" >> "$HEART" 2>&1; then
      echo "DOWNLOAD_COMPLETE" > "$STATUS"
      echo "$(date -Iseconds) DOWNLOAD_COMPLETE all 4 files verified" >> "$HEART"
    else
      echo "VERIFY_FAILED" > "$STATUS"
      echo "$(date -Iseconds) VERIFY_FAILED integrity check did not pass" >> "$HEART"
      exit 1
    fi
    break
  fi
  echo "downloading" > "$STATUS"
  sleep 30
done
