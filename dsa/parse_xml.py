#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from datetime import datetime
import re

class TransactionStore:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.transactions_list = self._parse_xml(xml_path)
        self.transactions_dict = {t["id"]: t for t in self.transactions_list}
        self.next_id = max(self.transactions_dict.keys(), default=0) + 1

    def _parse_body(self, body):
        tx = {"txid": None, "category": None, "amount": None,
              "counterparty_name": None, "counterparty_phone": None,
              "fee": None, "new_balance": None}
        if not body:
            return tx
        m = re.search(r"TxId[:\s]+(\d+)", body)
        if m:
            tx["txid"] = m.group(1)
        low = body.lower()
        if "deposit" in low:
            tx["category"] = "Deposit"
        elif "withdraw" in low:
            tx["category"] = "Withdrawal"
        elif "received" in low:
            tx["category"] = "Incoming"
        elif "transferred" in low:
            tx["category"] = "Transfer"
        elif "payment" in low:
            tx["category"] = "Payment"
        elif "airtime" in low or "token" in low:
            tx["category"] = "ServicePayment"
        m = re.search(r"(\d{3,9})\s*RWF", body)
        if m:
            tx["amount"] = int(m.group(1))
        m = re.search(r"new balance[:\s]*([\d,]+)\s*RWF", body, re.I)
        if m:
            tx["new_balance"] = int(m.group(1).replace(",", ""))
        m = re.search(r"Fee (?:was|paid)[:\s]*([\d,]+)\s*RWF", body, re.I)
        if m:
            tx["fee"] = int(m.group(1).replace(",", ""))
        return tx

    def _parse_xml(self, path):
        tree = ET.parse(path)
        root = tree.getroot()
        txs = []
        for idx, sms in enumerate(root.findall("sms"), start=1):
            rec = sms.attrib.copy()
            body = rec.get("body", "")
            tx = self._parse_body(body)
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

    def get_all_transactions(self):
        return self.transactions_list

    def get_transaction(self, tid):
        return self.transactions_dict.get(tid)

    def add_transaction(self, body):
        tx = {"id": self.next_id, "body": body, "date": datetime.utcnow().isoformat()+"Z"}
        tx.update(self._parse_body(body))
        self.transactions_list.append(tx)
        self.transactions_dict[self.next_id] = tx
        self.next_id += 1
        return tx

    def update_transaction(self, tid, body):
        if tid not in self.transactions_dict:
            return None
        tx = self.transactions_dict[tid]
        if body is not None:
            tx["body"] = body
            tx.update(self._parse_body(body))
        return tx

    def delete_transaction(self, tid):
        if tid not in self.transactions_dict:
            return False
        self.transactions_dict.pop(tid)
        self.transactions_list = [t for t in self.transactions_list if t["id"] != tid]
        return True

