#!/usr/bin/env python3
import sys
import os
import traceback
import json
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dsa.parse_xml import TransactionStore
except FileNotFoundError as e:
    print(f"ERROR: File not found - {e}")
    sys.exit(1)
except Exception:
    print("Startup failed:")
    traceback.print_exc()
    sys.exit(1)

store = TransactionStore("data/raw/modified_sms_v2.xml")
VALID_USERS = {"admin": "secret"}
PORT = 8080

class MoMoAPI(BaseHTTPRequestHandler):
    def _auth(self):
        auth = self.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            return False
        creds = base64.b64decode(auth.split()[1]).decode()
        u, p = creds.split(":", 1)
        return VALID_USERS.get(u) == p

    def _unauthorized(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="MoMoAPI"')
        self.end_headers()
        self.wfile.write(b'{"error":"Unauthorized"}')

    def _json(self, code, data):
        res = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(res)))
        self.end_headers()
        self.wfile.write(res)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        print(f"Received GET request: {self.path}")
        if not self._auth():
            return self._unauthorized()
        parts = self.path.strip("/").split("/")
        if parts[0] != "transactions":
            return self._json(404, {"error": "not found"})
        if len(parts) == 1:
            return self._json(200, {"transactions": store.get_all_transactions()})
        try:
            tid = int(parts[1])
        except:
            return self._json(400, {"error": "invalid id"})
        tx = store.get_transaction(tid)
        if not tx:
            return self._json(404, {"error": "not found"})
        self._json(200, tx)

    def do_POST(self):
        print(f"Received POST request: {self.path}")
        if not self._auth():
            return self._unauthorized()
        if self.path.strip("/") != "transactions":
            return self._json(404, {"error": "not found"})
        body = self._read_json()
        tx = store.add_transaction(body.get("body", ""))
        self._json(201, tx)

    def do_PUT(self):
        print(f"Received PUT request: {self.path}")
        if not self._auth():
            return self._unauthorized()
        parts = self.path.strip("/").split("/")
        if len(parts) != 2:
            return self._json(404, {"error":"not found"})
        try:
            tid = int(parts[1])
        except:
            return self._json(400, {"error":"invalid id"})
        body = self._read_json()
        tx = store.update_transaction(tid, body.get("body", None))
        if not tx:
            return self._json(404, {"error":"not found"})
        self._json(200, tx)

    def do_DELETE(self):
        print(f"Received DELETE request: {self.path}")
        if not self._auth():
            return self._unauthorized()
        parts = self.path.strip("/").split("/")
        if len(parts) != 2:
            return self._json(404, {"error":"not found"})
        try:
            tid = int(parts[1])
        except:
            return self._json(400, {"error":"invalid id"})
        if not store.delete_transaction(tid):
            return self._json(404, {"error":"not found"})
        self._json(200, {"deleted": tid})

if __name__ == "__main__":
    try:
        server = HTTPServer(("localhost", PORT), MoMoAPI)
        print(f"Running on http://localhost:{PORT} (user=admin, pass=secret)")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

