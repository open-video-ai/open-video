"""Shared test scaffolding: repo-root import path + local HTTP server helper."""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class CannedJSONHandler(BaseHTTPRequestHandler):
    """Base handler: silenced logging + a one-call reply helper."""

    def reply(self, obj=None, raw: bytes = None, ctype="application/json"):
        data = raw if raw is not None else json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        return json.loads(self.rfile.read(int(self.headers["Content-Length"])))

    def log_message(self, *a):
        pass


def serve(handler_cls):
    """Start an ephemeral-port HTTP server on a daemon thread.

    Returns (base_url, close_fn)."""
    server = HTTPServer(("127.0.0.1", 0), handler_cls)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    def close():
        server.shutdown()
        server.server_close()

    return f"http://127.0.0.1:{server.server_port}", close
