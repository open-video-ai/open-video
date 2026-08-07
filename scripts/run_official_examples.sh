#!/usr/bin/env bash
# Resolve lab root from this script location (no hard-coded machine path)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export ROOT
# Run all official MiniMax H3 examples sequentially via the agentic generator.
# Each run writes a receipt to artifacts/verify/agent_<mode>_<ts>.json + mp4 to output/.
# Usage: bash scripts/run_official_examples.sh [only=starship|baker|ramen|cityspeed]
set -u
cd "$ROOT"
PY=./venv/bin/python
ONLY="${1:-all}"
LOG=artifacts/verify/examples_run.log
mkdir -p artifacts/verify output
echo "$(date -Iseconds) START official examples (only=$ONLY)" | tee -a "$LOG"

run () {  # name mode promptfile extra...
  local name="$1" mode="$2" pf="$3"; shift 3
  [ "$ONLY" != "all" ] && [ "$ONLY" != "$name" ] && return
  echo "$(date -Iseconds) >>> $name ($mode)" | tee -a "$LOG"
  $PY scripts/h3_agent.py --prompt "$(cat "$pf")" "$@" 2>&1 | tee -a "$LOG" | tail -3
}

# 1. Official reproducible T2VA — starship bridge, 10s
run starship t2v prompts/official_t2va_starship.txt --width 1344 --height 768 --duration 10 --seed 0
# 2. Official prompt-guide Case 1 — baker, T2VA, ~5s
run baker    t2v prompts/case1_baker_t2va.txt       --width 1344 --height 768 --duration 5  --seed 0
# 3. Official reproducible FL2VA — ramen family, 8s, first-frame image
run ramen    fl2v prompts/reproducible_fl2va_ramen.txt --first-frame inputs/ramen_firstframe.png --width 1344 --height 768 --duration 8 --seed 0
# 4. Our guide-compliant cinematic example — violinist, 5s
run cityspeed t2v prompts/cinematic_cityspeed.txt   --width 1344 --height 768 --duration 5  --seed 0

echo "$(date -Iseconds) DONE official examples" | tee -a "$LOG"
