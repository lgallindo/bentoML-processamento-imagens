#!/usr/bin/env bash
# Harness efémero para capturas da aula 016.
# Sobe exporter :8010 + Prometheus :9100 + Grafana :14000 (Docker),
# porque no host as portas canónicas 3000/4000/9090 podem estar
# ocupadas. O handout do aluno continua a usar 3000/9090/4000.
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel)"
LESSON="$ROOT/016_grafana_dashboards"
OUT="$LESSON/illustrations"
DEMO_DIR="$ROOT/010_prometheus_promql"
BROWSE="${BROWSE:-$HOME/.claude/skills/gstack/browse/dist/browse}"
TMP="${TMPDIR:-/tmp}/bentoml-016-capture"
NETWORK="bentoml-016-net"
GRAFANA_IMAGE="${GRAFANA_IMAGE:-grafana/grafana:10.4.19}"

mkdir -p "$OUT" "$LESSON/fixtures" "$TMP/grafana/datasources" \
  "$TMP/grafana/dashboards" "$TMP/grafana/provisioning/dashboards"

cleanup() {
  if [[ "${CAPTURE_KEEP:-0}" == "1" ]]; then
    echo "CAPTURE_KEEP=1 — containers bentoml-016-* mantidos"
    return
  fi
  docker rm -f bentoml-016-prom bentoml-016-grafana >/dev/null 2>&1 || true
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
  if [[ -n "${EXPORTER_PID:-}" ]]; then
    kill "$EXPORTER_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "==> exporter sintético :8010"
pkill -f 'serve_sample_metrics.py --port 8010' 2>/dev/null || true
(
  cd "$DEMO_DIR"
  uv run --no-active python scripts/serve_sample_metrics.py --port 8010
) &
EXPORTER_PID=$!
sleep 1
curl --fail --silent --show-error "http://127.0.0.1:8010/metrics" >/dev/null

cp "$ROOT/monitoring/bentoml.rules.yml" "$TMP/bentoml.rules.yml"
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
          - host.docker.internal:8010
        labels:
          source: synthetic
YAML

docker network create "$NETWORK" >/dev/null 2>&1 || true
docker rm -f bentoml-016-prom bentoml-016-grafana >/dev/null 2>&1 || true

echo "==> Prometheus Docker :9100"
docker run -d --name bentoml-016-prom \
  --network "$NETWORK" \
  --add-host=host.docker.internal:host-gateway \
  -p 127.0.0.1:9100:9090 \
  -v "$TMP/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  -v "$TMP/bentoml.rules.yml:/etc/prometheus/bentoml.rules.yml:ro" \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml >/dev/null

for _ in $(seq 1 30); do
  curl -fsS "http://127.0.0.1:9100/-/healthy" >/dev/null 2>&1 && break
  sleep 1
done
curl --fail --silent --show-error "http://127.0.0.1:9100/-/healthy" >/dev/null

cat >"$TMP/grafana/datasources/ds.yml" <<'YAML'
apiVersion: 1
prune: true
datasources:
  - name: Prometheus — BentoML Imagens
    uid: bentoml-prometheus
    type: prometheus
    access: proxy
    url: http://bentoml-016-prom:9090
    isDefault: true
    editable: false
YAML
cat >"$TMP/grafana/provisioning/dashboards/provider.yml" <<'YAML'
apiVersion: 1
providers:
  - name: bentoml-016
    orgId: 1
    folder: ""
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
YAML
cp "$ROOT/monitoring/grafana/dashboards/bentoml-health.json" \
  "$TMP/grafana/dashboards/bentoml-health.json"

echo "==> Grafana Docker :14000 ($GRAFANA_IMAGE)"
docker run -d --name bentoml-016-grafana \
  --network "$NETWORK" \
  -p 127.0.0.1:14000:3000 \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -e GF_USERS_DEFAULT_THEME=light \
  -e GF_LOG_LEVEL=warn \
  -v "$TMP/grafana/datasources:/etc/grafana/provisioning/datasources:ro" \
  -v "$TMP/grafana/provisioning/dashboards:/etc/grafana/provisioning/dashboards:ro" \
  -v "$TMP/grafana/dashboards:/var/lib/grafana/dashboards:ro" \
  "$GRAFANA_IMAGE" >/dev/null

echo "==> esperar Grafana (migrações podem demorar em disco lento)"
for i in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:14000/api/health" >/dev/null 2>&1; then
    echo "    healthy após ${i}s"
    break
  fi
  sleep 2
done
curl --fail --silent --show-error "http://127.0.0.1:14000/api/health" >/dev/null

echo "==> aguardar scrape + tráfego sintético"
sleep 25

shot() {
  local url="$1"
  local dest="$2"
  "$BROWSE" goto "$url" >/dev/null
  sleep 1
  "$BROWSE" screenshot --viewport "$dest"
  echo "    wrote $dest"
}

auth_browse() {
  local jar="$TMP/cookies.txt"
  curl -sS -c "$jar" -b "$jar" \
    -X POST "http://127.0.0.1:14000/login" \
    -H "Content-Type: application/json" \
    -d '{"user":"admin","password":"admin"}' >/dev/null
  local sess exp
  sess="$(awk -F'\t' '$6=="grafana_session"{print $7}' "$jar")"
  exp="$(awk -F'\t' '$6=="grafana_session_expiry"{print $7}' "$jar")"
  "$BROWSE" goto "http://127.0.0.1:14000/login" >/dev/null
  "$BROWSE" cookie "grafana_session=$sess" >/dev/null
  "$BROWSE" cookie "grafana_session_expiry=$exp" >/dev/null
}

echo "==> capturas Prometheus /metrics"
shot 'http://127.0.0.1:9100/graph?g0.expr=up%7Bjob%3D%22bentoml-imagens%22%7D&g0.tab=0' \
  "$OUT/01_prometheus_graph_up.png"
shot 'http://127.0.0.1:9100/graph?g0.expr=sum%20by%20(endpoint)%20(rate(bentoml_service_request_total%5B1m%5D))&g0.tab=0' \
  "$OUT/02_prometheus_graph_rate.png"
shot 'http://127.0.0.1:8010/metrics' "$OUT/09_metrics_raw_text.png"
curl -sS "http://127.0.0.1:8010/metrics" | head -n 80 \
  >"$LESSON/fixtures/metrics_sample_head.txt"

echo "==> capturas Grafana"
shot 'http://127.0.0.1:14000/login' "$OUT/03_grafana_login.png"
auth_browse
shot 'http://127.0.0.1:14000/?orgId=1' "$OUT/04_grafana_home.png"
shot 'http://127.0.0.1:14000/connections/datasources' "$OUT/05_grafana_datasources.png"
shot 'http://127.0.0.1:14000/d/bentoml-health-016/bentoml-saude-aula-016?orgId=1&from=now-30m&to=now&refresh=10s' \
  "$OUT/06_grafana_dashboard_health.png"
shot 'http://127.0.0.1:14000/explore?orgId=1&left=%7B%22datasource%22:%22bentoml-prometheus%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22up%7Bjob%3D%5C%22bentoml-imagens%5C%22%7D%22%7D%5D,%22range%22:%7B%22from%22:%22now-15m%22,%22to%22:%22now%22%7D%7D' \
  "$OUT/07_grafana_explore_up.png"

echo "==> figuras matplotlib (se ainda não existirem)"
(
  cd "$LESSON"
  uv run --no-active --with matplotlib python scripts/generate_comparison_figures.py
  uv run --no-active --with matplotlib python scripts/generate_dashboard_schematic.py
)

echo "==> capturas em $OUT"
ls -la "$OUT"
