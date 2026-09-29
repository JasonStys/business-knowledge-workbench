#!/usr/bin/env bash
# @index-begin
# @index-end
# Reproducible local/CI verification. Requires the activated project Python environment and Node 24.
set -euo pipefail
python -m ruff check server scripts tests/python
python -m ruff format --check server scripts tests/python
npm run format:check
python scripts/code_index.py --check
python -m pytest -q
python scripts/benchmark.py
npm run build
npm test
npm audit --audit-level=high
python -m pip_audit -r requirements.lock
