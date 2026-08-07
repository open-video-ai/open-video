#!/usr/bin/env bash
# Resolve lab root from this script location (no hard-coded machine path)
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
export ROOT
# Run the ported Seedance-style prompts on H3 (gap-analysis benchmark vs Seedance).
set -u; cd "$ROOT"; PY=./venv/bin/python
LOG=artifacts/verify/seedance_examples.log; mkdir -p artifacts/verify output
echo "$(date -Iseconds) START seedance-port examples (sage-enabled)" | tee -a "$LOG"
$PY scripts/h3_agent.py --prompt "$(cat prompts/seedance_ported_01_romance.txt)"       --width 1344 --height 768 --duration 10 --seed 1 2>&1 | tee -a "$LOG" | tail -2
$PY scripts/h3_agent.py --prompt "$(cat prompts/seedance_ported_03_racing.txt)"        --width 1344 --height 768 --duration 8  --seed 2 2>&1 | tee -a "$LOG" | tail -2
$PY scripts/h3_agent.py --prompt "$(cat prompts/seedance_ported_07_product_flower.txt)" --width 1344 --height 768 --duration 6  --seed 3 2>&1 | tee -a "$LOG" | tail -2
echo "$(date -Iseconds) DONE seedance-port examples" | tee -a "$LOG"
