#!/usr/bin/env bash
# Self-contained offline demo: start the mock kit host, scan it, show the hits.
# Deliberate pauses keep each step readable in the recorded SVG/GIF.
# Requires the package installed (uv pip install -e .) and the venv active.
set -e
cd "$(dirname "$0")/.."          # repo root

mkdir -p captures
# Clear only previous demo captures (localhost artifacts + log) so each run
# shows fresh hits — never touches real captures from other hosts.
rm -f captures/http127.0.0.1*kit* captures/hits.log 2>/dev/null || true

# Free the port in case a previous run left a server behind.
if command -v lsof >/dev/null 2>&1; then
    lsof -ti tcp:8000 | xargs kill 2>/dev/null || true
fi

python demo/mock_server.py >/dev/null 2>&1 &
SERVER=$!
trap 'kill "$SERVER" 2>/dev/null' EXIT

# Wait until the mock host actually accepts connections before scanning.
for _ in $(seq 1 40); do
    if python - <<'PY' 2>/dev/null
import socket, sys
s = socket.socket(); s.settimeout(0.3)
try:
    s.connect(("127.0.0.1", 8000)); s.close()
except Exception:
    sys.exit(1)
PY
    then
        break
    fi
    sleep 0.2
done

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
