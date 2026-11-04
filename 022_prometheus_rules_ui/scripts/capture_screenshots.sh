#!/usr/bin/env bash
# Harness efémero para capturas da aula 022 (/rules).
# Sobe exporter + Prometheus na rede Docker bentoml-022-net e publica
# a UI em :9112. O handout do aluno continua a citar 3000/9090.
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel)"
LESSON="$ROOT/022_prometheus_rules_ui"
OUT="$LESSON/illustrations"
FIX="$LESSON/fixtures"
TMP="${TMPDIR:-/tmp}/bentoml-022-capture"
NETWORK="bentoml-022-net"
PROM_PORT=9112

mkdir -p "$OUT" "$FIX" "$TMP/exp"

cleanup() {
  if [[ "${CAPTURE_KEEP:-0}" == "1" ]]; then
    echo "CAPTURE_KEEP=1 — containers bentoml-022-* mantidos"
    return
  fi
  docker rm -f bentoml-022-prom bentoml-022-exp >/dev/null 2>&1 || true
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cp "$ROOT/monitoring/bentoml.rules.yml" "$TMP/bentoml.rules.yml"
cp "$ROOT/monitoring/bentoml.rules.yml" "$FIX/bentoml.rules.yml"
cp "$ROOT/010_prometheus_promql/scripts/serve_sample_metrics.py" "$TMP/exp/serve.py"
# Docker precisa ouvir em 0.0.0.0 dentro do container.
sed -i 's/HTTPServer(("127.0.0.1", args.port)/HTTPServer(("0.0.0.0", args.port)/' \
  "$TMP/exp/serve.py"

cat >"$TMP/prometheus.yml" <<'YAML'
global:
  scrape_interval: 5s
  evaluation_interval: 5s
rule_files:
  - /etc/prometheus/bentoml.rules.yml
scrape_configs:
  - job_name: bentoml-imagens
    metrics_path: /metrics
    static_configs:
      - targets:
          - bentoml-022-exp:8022
        labels:
          source: synthetic
YAML

docker network create "$NETWORK" >/dev/null 2>&1 || true
docker rm -f bentoml-022-prom bentoml-022-exp >/dev/null 2>&1 || true

echo "==> exporter Docker (bentoml-022-exp:8022)"
docker run -d --name bentoml-022-exp --network "$NETWORK" \
  -v "$TMP/exp/serve.py:/serve.py:ro" \
  python:3.13-slim python /serve.py --port 8022 >/dev/null

echo "==> Prometheus Docker :${PROM_PORT}"
docker run -d --name bentoml-022-prom --network "$NETWORK" \
  -p "127.0.0.1:${PROM_PORT}:9090" \
  -v "$TMP/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  -v "$TMP/bentoml.rules.yml:/etc/prometheus/bentoml.rules.yml:ro" \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml >/dev/null

for _ in $(seq 1 40); do
  curl -fsS "http://127.0.0.1:${PROM_PORT}/-/healthy" >/dev/null 2>&1 && break
  sleep 1
done
curl --fail --silent --show-error "http://127.0.0.1:${PROM_PORT}/-/healthy" >/dev/null

echo "==> aguardar scrape UP + avaliação de regras"
for _ in $(seq 1 30); do
  health="$(curl -fsS "http://127.0.0.1:${PROM_PORT}/api/v1/targets" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['activeTargets'][0]['health'])")"
  [[ "$health" == "up" ]] && break
  sleep 1
done
sleep 5

curl -fsS "http://127.0.0.1:${PROM_PORT}/api/v1/rules" \
  | python3 -c 'import json,sys; json.dump(json.load(sys.stdin), sys.stdout, indent=2, ensure_ascii=False); print()' \
  >"$FIX/rules_api_response.json"
curl -fsS "http://127.0.0.1:${PROM_PORT}/api/v1/targets" \
  | python3 -c 'import json,sys; json.dump(json.load(sys.stdin), sys.stdout, indent=2, ensure_ascii=False); print()' \
  >"$FIX/targets_api_response.json"

python3 -c "
import json
from pathlib import Path
fix = Path('$FIX')
jobs = {t['labels'].get('job') for t in json.loads((fix/'targets_api_response.json').read_text())['data']['activeTargets']}
assert 'bentoml-imagens' in jobs, jobs
health = json.loads((fix/'targets_api_response.json').read_text())['data']['activeTargets'][0]['health']
assert health == 'up', health
groups = json.loads((fix/'rules_api_response.json').read_text())['data']['groups']
assert groups and groups[0]['name'] == 'bentoml-response-time'
print('OK targets up; rules group', groups[0]['name'])
"

echo "==> capturas Playwright"
uv run --no-active --with playwright python - <<PY
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path("$OUT")
base = "http://127.0.0.1:${PROM_PORT}"
shots = {
    "01_targets_bentoml_imagens.png": f"{base}/targets",
    "02_rules_page.png": f"{base}/rules",
    "03_alerts_page.png": f"{base}/alerts",
    "04_graph_recording_series.png": (
        f"{base}/graph?g0.expr=bentoml%3Ahttp_request_duration_seconds%3Ap95_1m&g0.tab=1"
    ),
    "05_graph_alerts_series.png": (
        f"{base}/graph?g0.expr=ALERTS%7Balertname%3D%22BentoMLResponseTimeAnomaly%22%7D&g0.tab=1"
    ),
}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    for name, url in shots.items():
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        dest = out / name
        page.screenshot(path=str(dest), full_page=True)
        print("wrote", dest, dest.stat().st_size)
    browser.close()
PY

echo "==> capturas concluídas"
ls -la "$OUT"/*.png "$FIX"/*.json "$FIX"/*.yml
