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
PY=/home/robot/miniconda3/bin/python
LOCAL=h3_models
HEART=logs/h3_download_heartbeat.log
STATUS=logs/h3_download.status

declare -A WANT=(
  ["diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors"]=20970379616
  ["text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors"]=27141342152
  ["vae/minimax_h3_video_vae_fp16.safetensors"]=5207808496
  ["vae/minimax_h3_audio_vae_fp32.safetensors"]=605254808
)

echo "$(date -Iseconds) START resilient H3 download loop (4 files, ~54GB)" >> "$HEART"
while true; do
  $PY -c "
from modelscope import snapshot_download
try:
    snapshot_download('Comfy-Org/MiniMax-H3', allow_patterns=[
        'diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors',
        'text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors',
        'vae/minimax_h3_video_vae_fp16.safetensors',
        'vae/minimax_h3_audio_vae_fp32.safetensors',
    ], local_dir='$LOCAL')
    print('PASS')
except Exception as e:
    print('ERR', repr(e))
" >> "$HEART" 2>&1

  # finalize: modelscope stages completed files under ._____temp; move to final paths
  for path in "${!WANT[@]}"; do
    final="$LOCAL/$path"; tmp="$LOCAL/._____temp/$path"
    if [ ! -f "$final" ] && [ -f "$tmp" ]; then
      mkdir -p "$(dirname "$final")"; mv "$tmp" "$final" && echo "$(date -Iseconds) finalized $path" >> "$HEART"
    fi
  done
  all_ok=1
  for path in "${!WANT[@]}"; do
    got=$(stat -c%s "$LOCAL/$path" 2>/dev/null || echo 0)
    want=${WANT[$path]}
    [ "$got" = "$want" ] || all_ok=0
  done
  sz=$(du -sh "$LOCAL" 2>/dev/null | cut -f1)
  echo "$(date -Iseconds) total=$sz all_complete=$all_ok" >> "$HEART"
  if [ "$all_ok" = "1" ]; then
    echo "DOWNLOAD_COMPLETE" > "$STATUS"
    echo "$(date -Iseconds) DOWNLOAD_COMPLETE all 4 files verified" >> "$HEART"
    break
  fi
  echo "downloading" > "$STATUS"
  sleep 30
done
