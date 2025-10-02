import re
import xml.etree.ElementTree as ET
from datetime import datetime

class TransactionStore:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.transactions_list = []
        self.transactions_dict = {}
        self._load_xml()

    def parse_body(self, body: str):
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

    def _load_xml(self):
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        for idx, sms in enumerate(root.findall("sms"), start=1):
            rec = sms.attrib.copy()
            body = rec.get("body", "")
            tx = self.parse_body(body)
            try:
                ts = int(rec.get("date", "0")) // 1000
                date = datetime.utcfromtimestamp(ts).isoformat() + "Z"
            except:
                date = rec.get("readable_date")
            record = {
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
            }
            self.transactions_list.append(record)
            self.transactions_dict[idx] = record

    def add_transaction(self, body_text):
        new_id = max(self.transactions_dict.keys(), default=0) + 1
        tx = {"id": new_id, "body": body_text, "date": datetime.utcnow().isoformat() + "Z"}
        tx.update(self.parse_body(body_text))
        self.transactions_list.append(tx)
        self.transactions_dict[new_id] = tx
        return tx

    def update_transaction(self, tid, body_text):
        tx = self.transactions_dict.get(tid)
        if not tx:
            return None
        tx["body"] = body_text
        tx.update(self.parse_body(body_text))
        return tx

    def delete_transaction(self, tid):
        if tid not in self.transactions_dict:
            return False
        self.transactions_dict.pop(tid)
        self.transactions_list = [t for t in self.transactions_list if t["id"] != tid]
        return True
