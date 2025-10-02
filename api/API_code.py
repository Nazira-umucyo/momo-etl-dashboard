#!/usr/bin/env python3
import json
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from dsa.parse_xml import TransactionStore

PORT = 8000
VALID_USERS = {"admin": "secret"}
store = TransactionStore("data/raw/modified_sms_v2.xml")

class MoMoAPI(BaseHTTPRequestHandler):
    def _auth(self):
        auth = self.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            return False
        try:
            creds = base64.b64decode(auth.split()[1]).decode()
            u, p = creds.split(":", 1)
        except:
            return False
        return VALID_USERS.get(u) == p

    def _unauthorized(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="MoMoAPI"')
        self.send_header("Content-Type", "application/json")
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
        if length == 0: return {}
        try:
            return json.loads(self.rfile.read(length))
        except:
            return {}

    def do_GET(self):
        if not self._auth(): return self._unauthorized()
        parts = self.path.strip("/").split("/")
        if parts[0] != "transactions":
            return self._json(404, {"error": "not found"})
        if len(parts) == 1:
            return self._json(200, {"transactions": store.transactions_list})
        try:
            tid = int(parts[1])
        except:
            return self._json(400, {"error": "invalid id"})
        tx = store.transactions_dict.get(tid)
        if not tx:
            return self._json(404, {"error": "not found"})
        self._json(200, tx)

    def do_POST(self):
        if not self._auth(): return self._unauthorized()
        if self.path.strip("/") != "transactions":
            return self._json(404, {"error": "not found"})
        body = self._read_json()
        tx = store.add_transaction(body.get("body", ""))
        self._json(201, tx)

    def do_PUT(self):
        if not self._auth(): return self._unauthorized()
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "transactions":
            return self._json(404, {"error": "not found"})
        try:
            tid = int(parts[1])
        except:
            return self._json(400, {"error": "invalid id"})
        body = self._read_json()
        tx = store.update_transaction(tid, body.get("body", ""))
        if not tx:
            return self._json(404, {"error": "not found"})
        self._json(200, tx)

    def do_DELETE(self):
        if not self._auth(): return self._unauthorized()
        parts = self.path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "transactions":
            return self._json(404, {"error": "not found"})
        try:
            tid = int(parts[1])
        except:
            return self._json(400, {"error": "invalid id"})
        if not store.delete_transaction(tid):
            return self._json(404, {"error": "not found"})
        self._json(200, {"deleted": tid})

if __name__ == "__main__":
    print(f"Running on http://localhost:{PORT} (user=admin, pass=secret)")
    HTTPServer(("localhost", PORT), MoMoAPI).serve_forever()
