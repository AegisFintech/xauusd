#!/usr/bin/env bash
set -euo pipefail
PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -m pip install -e .
"$PYTHON_BIN" -m xauusd.cli campaign --synthetic
exec "$PYTHON_BIN" -m uvicorn xauusd.dashboard:app --host 0.0.0.0 --port "${PORT:-8080}"
