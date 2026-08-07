#!/usr/bin/env bash
# Resolve lab root from this script location (no hard-coded machine path)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export ROOT
# H3 download monitor (called by /loop every 10m). Accurate completion + progress.
#  - completion per file = file exists AND its .aria2 control sidecar is GONE
#    (aria2c deletes <file>.aria2 when the file is fully fetched; stat size is
#     unreliable because aria2c sparse-allocates).
#  - progress = real disk blocks (du), not apparent size.
set -u
cd "$ROOT"
LIST=scripts/h3_aria2_list.txt
[ -f "$LIST" ] || cat > "$LIST" <<'EOF'
https://www.modelscope.cn/api/v1/models/Comfy-Org/MiniMax-H3/repo?Revision=master&FilePath=diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
  dir=${ROOT}/h3_models/diffusion_models
  out=minimax_h3_fl2va_pruned_int8_convrot.safetensors
https://www.modelscope.cn/api/v1/models/Comfy-Org/MiniMax-H3/repo?Revision=master&FilePath=text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors
  dir=${ROOT}/h3_models/text_encoders
  out=qwen3vl_32b_minimax_h3_int8_convrot.safetensors
https://www.modelscope.cn/api/v1/models/Comfy-Org/MiniMax-H3/repo?Revision=master&FilePath=vae/minimax_h3_video_vae_fp16.safetensors
  dir=${ROOT}/h3_models/vae
  out=minimax_h3_video_vae_fp16.safetensors
https://www.modelscope.cn/api/v1/models/Comfy-Org/MiniMax-H3/repo?Revision=master&FilePath=vae/minimax_h3_audio_vae_fp32.safetensors
  dir=${ROOT}/h3_models/vae
  out=minimax_h3_audio_vae_fp32.safetensors
EOF

if ! pgrep -x aria2c >/dev/null; then
  echo "$(date -Iseconds) aria2c DOWN - restarting"
  nohup aria2c -j1 -x16 -s16 -k1M --file-allocation=none --console-log-level=warn \
    --summary-interval=30 --max-tries=0 --retry-wait=3 --continue=true --auto-file-renaming=false \
    -i "$LIST" >> logs/aria2_download.log 2>&1 &
fi

TOTAL_WANT=54173627952
FILES=(
  diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
  text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors
  vae/minimax_h3_video_vae_fp16.safetensors
  vae/minimax_h3_audio_vae_fp32.safetensors )
done=0
for f in "${FILES[@]}"; do
  [ -f "h3_models/$f" ] && [ ! -f "h3_models/$f.aria2" ] && done=$((done+1))
done
real=$(du -sB1 h3_models 2>/dev/null | awk '{print $1}')
python3 -c "r=$real;t=$TOTAL_WANT;d=$done;print(f'$(date -Iseconds) complete={d}/4  real={r/t*100:.1f}% ({r/1e9:.2f}GB/54.17GB)  aria2c=$(pgrep -x aria2c|head -1||echo DOWN)')"
[ "$done" = "4" ] && echo "DOWNLOAD_COMPLETE" > logs/h3_download.status || echo "downloading" > logs/h3_download.status
