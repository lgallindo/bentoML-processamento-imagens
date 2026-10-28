#!/usr/bin/env bash
# Wrapper: export lesson 003|008 for Streamlit Community Cloud.
set -euo pipefail
ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
exec python3 "$ROOT/scripts/export_streamlit_cloud.py" "$@"
