MoMo API Documentation

Base URL: http://localhost:8000

Authentication:

All endpoints require Basic Authentication.

Header: Authorization: Basic <base64(username:password)>

Default credentials: user: admin
pass: secret

Unauthorized requests return: {"error": "Unauthorized"}
HTTP Status Code: 401

1. Get All Transactions

Endpoint: GET /transactions

Request Example (cURL): curl -u admin:secret http://localhost:8000/transactions

Response Example (200 OK): {
  "transactions": [
    {
      "id": 1,
      "txid": "12345",
      "category": "Deposit",
      "amount": 5000,
      "counterparty_name": null,
      "counterparty_phone": null,
      "fee": 0,
      "new_balance": 10000,
      "date": "2025-10-02T10:00:00Z",
      "body": "TxId:12345 Deposit 5000 RWF new balance 10000 RWF"
    }
  ]
}
Error Codes:

401 Unauthorized → Invalid credentials

404 Not Found → Invalid path

2. Get Single Transaction

Endpoint: GET /transactions/<id>

Request Example (cURL): curl -u admin:secret http://localhost:8000/transactions/1

Response Example (200 OK): {
  "id": 1,
  "txid": "12345",
  "category": "Deposit",
  "amount": 5000,
  "counterparty_name": null,
  "counterparty_phone": null,
  "fee": 0,
  "new_balance": 10000,
  "date": "2025-10-02T10:00:00Z",
  "body": "TxId:12345 Deposit 5000 RWF new balance 10000 RWF"
}
Error Codes:

400 Invalid ID → Non-integer ID

404 Not Found → Transaction not found

401 Unauthorized → Invalid credentials

3. Create Transaction

Endpoint: POST /transactions

Request Headers: Content-Type: application/json
Authorization: Basic <base64(username:password)>

Request Example (cURL): curl -u admin:secret -X POST http://localhost:8000/transactions \
-H "Content-Type: application/json" \
-d '{"body": "TxId:67890 Withdrawal 2000 RWF Fee 50 RWF new balance 8000 RWF"}'

Response Example (201 Created): {
  "id": 2,
  "txid": "67890",
  "category": "Withdrawal",
  "amount": 2000,
  "fee": 50,
  "new_balance": 8000,
  "date": "2025-10-02T10:05:00Z",
  "body": "TxId:67890 Withdrawal 2000 RWF Fee 50 RWF new balance 8000 RWF"
}
Error Codes:

401 Unauthorized → Invalid credentials

404 Not Found → Wrong path

4. Update Transaction

Endpoint: PUT /transactions/<id>

Request Headers: Content-Type: application/json
Authorization: Basic <base64(username:password)>

Request Example (cURL): curl -u admin:secret -X PUT http://localhost:8000/transactions/2 \
-H "Content-Type: application/json" \
-d '{"body": "TxId:67890 Withdrawal 2500 RWF Fee 50 RWF new balance 7500 RWF"}'

Response Example (200 OK): {
  "id": 2,
  "txid": "67890",
  "category": "Withdrawal",
  "amount": 2500,
  "fee": 50,
  "new_balance": 7500,
  "date": "2025-10-02T10:05:00Z",
  "body": "TxId:67890 Withdrawal 2500 RWF Fee 50 RWF new balance 7500 RWF"
}
Error Codes:

400 Invalid ID → Non-integer ID

404 Not Found → Transaction not found or wrong path

401 Unauthorized → Invalid credentials

5. Delete Transaction

Endpoint: DELETE /transactions/<id>

Request Example (cURL): curl -u admin:secret -X DELETE http://localhost:8000/transactions/2

Response Example (200 OK): {
  "deleted": 2
}
Error Codes:

400 Invalid ID → Non-integer ID

404 Not Found → Transaction not found or wrong path

401 Unauthorized → Invalid credentials

Notes

All endpoints require Basic Auth.

id is auto-incremented when creating new transactions.

Transaction data is stored in memory; restarting the server reloads from the XML file.

For production, Basic Auth is not secure. Consider JWT or OAuth2.
