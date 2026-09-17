#!/usr/bin/env python3
"""Local mock host for a safe, fully offline PhishKit-Hunter demo.

Serves a few fake artifact files (no real data) so `pkhunter scan` produces
genuine hits against 127.0.0.1 — no external target is ever contacted.

    python demo/mock_server.py        # then, elsewhere: pkhunter scan ...
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FAKE = b"<!-- demo fixture: fake captured data, contains no real victim info -->\n"

# Planted artifacts under /kit/. The sentinel path is deliberately ABSENT (404),
# so the host is not treated as catch-all.
ARTIFACTS = {
    "/kit/fucked/FULLZ.html": FAKE,
    "/kit/captured.txt": FAKE,
    "/kit/visits.txt": FAKE,
    "/kit/nickel/fucked/SMS.html": FAKE,
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (http.server API)
        body = ARTIFACTS.get(self.path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):  # keep the demo output clean
        pass


if __name__ == "__main__":
    print("Mock kit host on http://127.0.0.1:8000/kit/  (Ctrl-C to stop)")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
