#!/usr/bin/env bash
# Self-contained offline demo: start the mock kit host, scan it, show the hits.
# Deliberate pauses keep each step readable in the recorded SVG/GIF.
# Requires the package installed (uv pip install -e .) and the venv active.
set -e
cd "$(dirname "$0")/.."          # repo root

rm -f captures/hits.log
python demo/mock_server.py >/dev/null 2>&1 &
SERVER=$!
trap 'kill "$SERVER" 2>/dev/null' EXIT
sleep 1

pause() { sleep "${1:-1.5}"; }

pause 1
echo "$ pkhunter scan --targets demo/targets.txt"
pause
pkhunter scan --targets demo/targets.txt
pause 3

echo
echo "$ cat captures/hits.log"
pause
cat captures/hits.log
pause 5          # let the final frame linger before the SVG loops
