#!/usr/bin/env bash
set -euo pipefail


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

PRED_JSONL="${1:-}"
if [[ -z "${PRED_JSONL}" ]]; then
  echo "Error: Missing input file."
  echo "Usage: bash scripts/run_eval_smoke.sh /path/to/pred_smoke.jsonl"
  exit 1
fi

echo "[INFO] Starting ViLLA smoke evaluation..."
echo "[INFO] Input file: ${PRED_JSONL}"


python "${ROOT_DIR}/score_smoke_v2.py" --pred_jsonl "${PRED_JSONL}"

echo "=================================================="
echo "[OK] Evaluation finished successfully."
echo "[INFO] Please check your output directory for the following expected artifacts:"
echo " - smoke_metrics_overall_v8ak.json"
echo " - smoke_metrics_by_split_v8ak.csv"
echo " - smoke_metrics_by_scene_v8ak.csv"
