#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -m xauusd.cli data update
.venv/bin/python -m xauusd.cli daily-run
