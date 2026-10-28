#!/usr/bin/env bash
# Harness lean: pytest por aula sem uv sync e sem pipe para tail.
# Uso: scripts/lean_pytest_lessons.sh [003|005|006|008|all]
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
FALLBACK_PY="${ROOT}/003_ks_drift_alert_streamlit/.venv/bin/python"
WAVE="${1:-all}"

declare -A LESSONS=(
  [003]="003_ks_drift_alert_streamlit"
  [005]="005_ks_anomaly_detection_streamlit"
  [006]="006_ks_input_output_streamlit"
  [008]="008_psi_drift_alert_streamlit"
)

pick_py() {
  local dir="$1"
  local py="${dir}/.venv/bin/python"
  # Prefer aula venv only if pytest importa depressa; senão fallback 003.
  if [[ -x "$py" ]] && "$py" -c "import pytest" 2>/dev/null; then
    echo "$py"
    return
  fi
  echo "$FALLBACK_PY"
}

run_one() {
  local key="$1"
  local dir="${ROOT}/${LESSONS[$key]}"
  local py
  py="$(pick_py "$dir")"
  if [[ ! -x "$py" ]]; then
    echo "FAIL ${key}: nenhum Python (.venv) disponível" >&2
    return 127
  fi
  echo "==== pytest ${key} (${LESSONS[$key]}) via ${py} ===="
  (
    cd "$dir"
    PYTHONPATH=. PYTHONUNBUFFERED=1 "$py" -m pytest tests/ -q --tb=line
  )
}

keys=()
if [[ "$WAVE" == "all" ]]; then
  keys=(003 005 006 008)
else
  keys=("$WAVE")
fi

status=0
for k in "${keys[@]}"; do
  if [[ -z "${LESSONS[$k]+x}" ]]; then
    echo "aula desconhecida: $k" >&2
    exit 2
  fi
  if run_one "$k"; then
    echo "==== PASS ${k} ===="
  else
    status=$?
    echo "==== FAIL ${k} exit=${status} ===="
  fi
done
exit "$status"
