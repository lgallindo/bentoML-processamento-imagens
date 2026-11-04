#!/usr/bin/env bash
# Harness: Elasticsearch :9200 + capturas (sem Kibana — disco).
set -euo pipefail
ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel)"
LESSON="$ROOT/018_elasticsearch_logs"
OUT="$LESSON/illustrations"
BROWSE="${BROWSE:-$HOME/.claude/skills/gstack/browse/dist/browse}"
TMP="${TMPDIR:-/tmp}/bentoml-018-capture"
ES_URL="${ES_URL:-http://127.0.0.1:9200}"

mkdir -p "$OUT" "$TMP" "$LESSON/fixtures"

cleanup() {
  if [[ "${CAPTURE_KEEP:-0}" == "1" ]]; then
    echo "CAPTURE_KEEP=1 — ES container mantido se existir"
    return
  fi
  # não mata ES externo; só o nosso nome
  true
}
trap cleanup EXIT

python3 "$LESSON/fixtures/generate_sample_log.py"

if ! curl -fsS "$ES_URL" >/dev/null 2>&1; then
  echo "==> subindo elasticsearch:8.18.0 em :9200"
  docker rm -f bentoml-018-es >/dev/null 2>&1 || true
  docker run -d --name bentoml-018-es \
    -p 127.0.0.1:9200:9200 \
    -e discovery.type=single-node \
    -e xpack.security.enabled=false \
    -e ES_JAVA_OPTS='-Xms512m -Xmx512m' \
    elasticsearch:8.18.0 >/dev/null
fi

echo "==> esperar ES"
for i in $(seq 1 60); do
  if curl -fsS "$ES_URL" >/dev/null 2>&1; then
    echo "    es up (${i})"
    break
  fi
  sleep 2
done
curl --fail --silent --show-error "$ES_URL" >/dev/null

python3 "$LESSON/scripts/bulk_index_fixture.py" --url "$ES_URL"

# Save query results as fixtures
curl -fsS "$ES_URL/_cluster/health?pretty" >"$LESSON/fixtures/cluster_health.json"
curl -fsS -H 'Content-Type: application/json' \
  "$ES_URL/bentoml-requests/_search?pretty" \
  -d '{"query":{"term":{"phase":"slow"}},"size":5}' \
  >"$LESSON/fixtures/search_phase_slow.json"
curl -fsS -H 'Content-Type: application/json' \
  "$ES_URL/bentoml-requests/_search?pretty" \
  -d '{"size":0,"aggs":{"by_phase":{"terms":{"field":"phase"}}}}' \
  >"$LESSON/fixtures/agg_by_phase.json"

# HTML pages for browse screenshots
python3 <<PY
import json
from pathlib import Path
tmp = Path("$TMP")
health = Path("$LESSON/fixtures/cluster_health.json").read_text()
slow = Path("$LESSON/fixtures/search_phase_slow.json").read_text()
agg = Path("$LESSON/fixtures/agg_by_phase.json").read_text()
css = "body{font:14px/1.4 ui-monospace,monospace;background:#0b1020;color:#e8eefc;padding:20px} h1{font:600 18px sans-serif;color:#9fd0ff} pre{white-space:pre-wrap}"
(tmp/"health.html").write_text(f"<html><head><style>{css}</style></head><body><h1>GET /_cluster/health</h1><pre>{health}</pre></body></html>", encoding="utf-8")
(tmp/"search_slow.html").write_text(f"<html><head><style>{css}</style></head><body><h1>POST /bentoml-requests/_search — phase:slow</h1><pre>{slow}</pre></body></html>", encoding="utf-8")
(tmp/"agg.html").write_text(f"<html><head><style>{css}</style></head><body><h1>Aggregation by phase</h1><pre>{agg}</pre></body></html>", encoding="utf-8")
print("html ok")
PY

python3 -m http.server 18766 --directory "$TMP" >/dev/null 2>&1 &
HTTP_PID=$!
sleep 1

shot() {
  "$BROWSE" goto "$1" >/dev/null
  sleep 1
  "$BROWSE" screenshot --viewport "$2"
  echo "    wrote $2"
}

shot "$ES_URL" "$OUT/01_es_root.png"
shot "http://127.0.0.1:18766/health.html" "$OUT/02_cluster_health.png"
shot "http://127.0.0.1:18766/search_slow.html" "$OUT/05_search_phase_slow.png"
shot "http://127.0.0.1:18766/agg.html" "$OUT/06_agg_by_phase.png"

# JSONL preview
python3 <<PY
from pathlib import Path
lines = Path("$LESSON/fixtures/bentoml_requests.jsonl").read_text().splitlines()[:10]
html = "<pre style='font:13px monospace;padding:16px;background:#111;color:#eee'>" + "\n".join(lines) + "</pre>"
Path("$TMP/jsonl.html").write_text(html, encoding="utf-8")
PY
shot "http://127.0.0.1:18766/jsonl.html" "$OUT/09_jsonl_sample.png"

kill "$HTTP_PID" 2>/dev/null || true

(
  cd "$LESSON"
  uv run --no-active --with matplotlib python scripts/generate_comparison_figures.py
)

ls -la "$OUT"
