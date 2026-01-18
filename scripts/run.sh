#!/usr/bin/env bash
# Author: eric vanoverbeke
# Date: 2026-01-18
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

for arg in "$@"; do
  if [[ "${arg}" == "--test-data" ]]; then
    export APP_TEST_DATA=1
    export APP_DATA_DIR="${ROOT_DIR}/data-test"
  fi
done

PYTHON_BIN="python3"
if [[ -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
fi

"${PYTHON_BIN}" -m uvicorn app.main:app --host 127.0.0.1 --port 9999
