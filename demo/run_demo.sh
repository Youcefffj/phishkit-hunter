#!/usr/bin/env bash
# Self-contained offline demo: start the mock kit host, scan it, show the hits.
# Requires the package installed (uv pip install -e .) and the venv active,
# or run each command with a `uv run` prefix.
set -e
cd "$(dirname "$0")/.."          # repo root

rm -f captures/hits.log
python demo/mock_server.py >/dev/null 2>&1 &
SERVER=$!
trap 'kill "$SERVER" 2>/dev/null' EXIT
sleep 1

echo "$ pkhunter scan --targets demo/targets.txt"
pkhunter scan --targets demo/targets.txt
echo
echo "$ cat captures/hits.log"
cat captures/hits.log
sleep 1
