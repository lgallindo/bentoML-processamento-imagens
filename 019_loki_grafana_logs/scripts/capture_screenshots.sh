#!/usr/bin/env bash
# Harness efémero: Loki :13100 + Grafana :14000 (+ push do fixture).
# Portas canónicas do curso: Loki 3100, Grafana 4000.
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel)"
LESSON="$ROOT/019_loki_grafana_logs"
OUT="$LESSON/illustrations"
BROWSE="${BROWSE:-$HOME/.claude/skills/gstack/browse/dist/browse}"
TMP="${TMPDIR:-/tmp}/bentoml-019-capture"
NETWORK="bentoml-019-net"
LOKI_IMAGE="${LOKI_IMAGE:-grafana/loki:3.3.2}"
GRAFANA_IMAGE="${GRAFANA_IMAGE:-grafana/grafana:10.4.19}"

mkdir -p "$OUT" "$TMP/grafana/datasources"

cleanup() {
  if [[ "${CAPTURE_KEEP:-0}" == "1" ]]; then
    echo "CAPTURE_KEEP=1 — containers bentoml-019-* mantidos"
    return
  fi
  docker rm -f bentoml-019-loki bentoml-019-grafana >/dev/null 2>&1 || true
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
}
trap cleanup EXIT

python3 "$LESSON/fixtures/generate_sample_log.py"

docker network create "$NETWORK" >/dev/null 2>&1 || true
docker rm -f bentoml-019-loki bentoml-019-grafana >/dev/null 2>&1 || true

echo "==> Loki :13100 (config da imagem + limites da aula)"
docker run -d --name bentoml-019-loki \
  --network "$NETWORK" \
  -p 127.0.0.1:13100:3100 \
  -v "$LESSON/monitoring/loki-config.yaml:/etc/loki/local-config.yaml:ro" \
  "$LOKI_IMAGE" \
  -config.file=/etc/loki/local-config.yaml >/dev/null

for i in $(seq 1 40); do
  if curl -fsS "http://127.0.0.1:13100/ready" >/dev/null 2>&1; then
    echo "    loki ready (${i})"
    break
  fi
  sleep 1
done
curl --fail --silent --show-error "http://127.0.0.1:13100/ready" >/dev/null
sleep 3

echo "==> push fixture → Loki"
python3 "$LESSON/scripts/push_fixture_to_loki.py" \
  --url "http://127.0.0.1:13100/loki/api/v1/push"

curl -fsS -G "http://127.0.0.1:13100/loki/api/v1/query_range" \
  --data-urlencode 'query={job="bentoml"} |= "slow"' \
  --data-urlencode "start=$(date -u -d '2 hours ago' +%s)000000000" \
  --data-urlencode "end=$(date -u +%s)000000000" \
  --data-urlencode 'limit=20' \
  | python3 -m json.tool >"$LESSON/fixtures/loki_query_slow.json"
python3 - "$LESSON/fixtures/loki_query_slow.json" <<'PY'
import json, sys
from pathlib import Path
d = json.loads(Path(sys.argv[1]).read_text())
n = sum(len(s.get("values", [])) for s in d["data"]["result"])
assert n > 0, "Loki query slow returned 0 lines"
print(f"    loki slow lines: {n}")
PY

cat >"$TMP/grafana/datasources/ds.yml" <<'YAML'
apiVersion: 1
prune: true
datasources:
  - name: Loki — BentoML logs
    uid: bentoml-loki
    type: loki
    access: proxy
    url: http://bentoml-019-loki:3100
    isDefault: true
    editable: false
YAML

echo "==> Grafana :14000"
docker run -d --name bentoml-019-grafana \
  --network "$NETWORK" \
  -p 127.0.0.1:14000:3000 \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -e GF_USERS_DEFAULT_THEME=light \
  -e GF_LOG_LEVEL=warn \
  -v "$TMP/grafana/datasources:/etc/grafana/provisioning/datasources:ro" \
  "$GRAFANA_IMAGE" >/dev/null

for i in $(seq 1 90); do
  if curl -fsS "http://127.0.0.1:14000/api/health" >/dev/null 2>&1; then
    echo "    grafana healthy (${i})"
    break
  fi
  sleep 2
done
curl --fail --silent --show-error "http://127.0.0.1:14000/api/health" >/dev/null

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

echo "==> capturas"
shot "http://127.0.0.1:13100/ready" "$OUT/01_loki_ready.png"
shot "http://127.0.0.1:13100/metrics" "$OUT/02_loki_metrics_endpoint.png"
shot "http://127.0.0.1:14000/login" "$OUT/03_grafana_login.png"
auth_browse
shot "http://127.0.0.1:14000/connections/datasources" "$OUT/04_grafana_datasources.png"
shot "http://127.0.0.1:14000/explore?orgId=1&left=%7B%22datasource%22:%22bentoml-loki%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bjob%3D%5C%22bentoml%5C%22%7D%20%7C%3D%20%5C%22inference%5C%22%22,%22queryType%22:%22range%22%7D%5D,%22range%22:%7B%22from%22:%22now-3h%22,%22to%22:%22now%22%7D%7D" \
  "$OUT/05_explore_logql_inference.png"
shot "http://127.0.0.1:14000/explore?orgId=1&left=%7B%22datasource%22:%22bentoml-loki%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bjob%3D%5C%22bentoml%5C%22,phase%3D%5C%22slow%5C%22%7D%22,%22queryType%22:%22range%22%7D%5D,%22range%22:%7B%22from%22:%22now-3h%22,%22to%22:%22now%22%7D%7D" \
  "$OUT/06_explore_phase_slow.png"

(
  cd "$LESSON"
  uv run --no-active --with matplotlib python scripts/generate_comparison_figures.py
)

python3 <<PY
from pathlib import Path
lines = Path("$LESSON/fixtures/bentoml_requests.jsonl").read_text().splitlines()[:12]
html = "<pre style='font:14px monospace;padding:16px;background:#111;color:#eee'>" + "\n".join(lines) + "</pre>"
Path("$TMP/log_preview.html").write_text(html, encoding="utf-8")
PY
python3 -m http.server 18765 --directory "$TMP" >/dev/null 2>&1 &
HTTP_PID=$!
sleep 1
shot "http://127.0.0.1:18765/log_preview.html" "$OUT/09_jsonl_sample.png" || true
kill "$HTTP_PID" 2>/dev/null || true

ls -la "$OUT"
