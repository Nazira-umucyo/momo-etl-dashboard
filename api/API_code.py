import json
import base64
import re
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

XML_PATH = "data/raw/modified_sms_v2.xml"
PORT = 8000
VALID_USERS = {"admin": "secret"}

def parse_body(body: str):
    tx = {
        "txid": None,
        "category": None,
        "amount": None,
        "counterparty_name": None,
        "counterparty_phone": None,
        "fee": None,
        "new_balance": None
    }

    if not body:
        return tx

    m = re.search(r"TxId[:\s]+(\d+)", body)
    if m: tx["txid"] = m.group(1)

    body_lower = body.lower()
    if "deposit" in body_lower:
        tx["category"] = "Deposit"
    elif "withdraw" in body_lower:
        tx["category"] = "Withdrawal"
    elif "received" in body_lower:
        tx["category"] = "Incoming"
    elif "transferred" in body_lower:
        tx["category"] = "Transfer"
    elif "payment" in body_lower:
        tx["category"] = "Payment"
    elif "airtime" in body_lower or "token" in body_lower:
        tx["category"] = "ServicePayment"

    m = re.search(r"(\d{3,9})\s*RWF", body)
    if m: tx["amount"] = int(m.group(1))

    m = re.search(r"new balance[:\s]*([\d,]+)\s*RWF", body, re.I)
    if m: tx["new_balance"] = int(m.group(1).replace(",", ""))

    m = re.search(r"Fee (?:was|paid)[:\s]*([\d,]+)\s*RWF", body, re.I)
    if m: tx["fee"] = int(m.group(1).replace(",", ""))

    return tx

def parse_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    txs = []
    for idx, sms in enumerate(root.findall("sms"), start=1):
        rec = sms.attrib.copy()
        body = rec.get("body", "")
        tx = parse_body(body)
        try:
            ts = int(rec.get("date", "0")) // 1000
            date = datetime.utcfromtimestamp(ts).isoformat() + "Z"
        except:
            date = rec.get("readable_date")
        txs.append({
            "id": idx,
            "txid": tx["txid"],
            "category": tx["category"],
            "amount": tx["amount"],
            "counterparty_name": tx["counterparty_name"],
            "counterparty_phone": tx["counterparty_phone"],
            "fee": tx["fee"],
            "new_balance": tx["new_balance"],
            "date": date,
            "body": body
        })
    return txs

transactions_list = parse_xml(XML_PATH)
transactions_dict = {t["id"]: t for t in transactions_list}

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
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        if not self._auth(): return self._unauthorized()
        parts = self.path.strip("/").split("/")
        if parts[0] != "transactions":
            return self._json(404, {"error": "not found"})
        if len(parts) == 1:
            return self._json(200, {"transactions": transactions_list})
        try:
            tid = int(parts[1])
        except:
            return self._json(400, {"error": "invalid id"})
        tx = transactions_dict.get(tid)
        if not tx: return self._json(404, {"error": "not found"})
        self._json(200, tx)

    def do_POST(self):
        if not self._auth(): return self._unauthorized()
        if self.path.strip("/") != "transactions":
            return self._json(404, {"error": "not found"})
        body = self._read_json()
        new_id = max(transactions_dict.keys(), default=0) + 1
        tx = {"id": new_id, "body": body.get("body", ""), "date": datetime.utcnow().isoformat()+"Z"}
        tx.update(parse_body(tx["body"]))
        transactions_list.append(tx)
        transactions_dict[new_id] = tx
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
        tx = transactions_dict.get(tid)
        if not tx: return self._json(404, {"error": "not found"})
        body = self._read_json()
        if "body" in body:
            tx["body"] = body["body"]
            tx.update(parse_body(body["body"]))
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
        if tid not in transactions_dict:
            return self._json(404, {"error": "not found"})
        transactions_dict.pop(tid)
        global transactions_list
        transactions_list = [t for t in transactions_list if t["id"] != tid]
        self._json(200, {"deleted": tid})

if __name__ == "__main__":
    print(f"Running on http://localhost:{PORT} (user=admin, pass=secret)")
    HTTPServer(("localhost", PORT), MoMoAPI).serve_forever()
