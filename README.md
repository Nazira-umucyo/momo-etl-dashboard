# Team 3 – MoMo ETL Dashboard

## Project Overview
Team 3 is building an enterprise-level application designed to process Mobile Money (MoMo) SMS transaction data.  
The system features:

- **Data Extraction**: Import and parse transaction data from XML files  
- **Data Cleaning & Categorization**: Automatically clean and categorize transactions  
- **Database Storage**: Store processed data in a secure relational database  

This project is part of a continuous assessment to practice collaborative workflows, backend data processing, and system design.

---

## Team Members
- Allan Tumusime  
- Nazira Umucyo  
- Linda Queen Sheja  
- Davy Mugire
- UWENAYO Alain Pacifique

---

## Entity Relationship Diagram
https://github.com/Nazira-umucyo/momo-etl-dashboard/blob/main/image/momo_sms%20photo.png

---
## architecture diagram
https://github.com/Nazira-umucyo/momo-etl-dashboard/blob/main/docs/architecture%20diagram.jpg

## Scrum Board
We are using GitHub Projects to manage our workflow.  
👉 [View our Scrum Board](https://github.com/users/Nazira-umucyo/projects/1/views/1)

---

## Repository Organization



## API Setup Instructions

1. **Clone the repository:**

```bash

    Create a Python virtual environment (recommended):

python3 -m venv venv

venv\Scripts\activate      

    Install required packages (standard library only):

This project uses only Python’s standard library. No extra packages are required.

    Run the API server:

cd api
chmod +x API_code.py      
./API_code.py

The server will run on:

http://localhost:8000

Default credentials:

user: admin
pass: secret

API Documentation
Authentication

All endpoints require Basic Authentication:

Authorization: Basic <base64(username:password)>

Default credentials:

user: admin
pass: secret

Unauthorized requests return:

{"error": "Unauthorized"}

Endpoints
1. Get All Transactions

    Method: GET

    URL: /transactions

    Request Example:

curl -u admin:secret http://localhost:8000/transactions

    Response Example (200 OK):

{
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

2. Get Single Transaction

    Method: GET

    URL: /transactions/<id>

    Request Example:

curl -u admin:secret http://localhost:8000/transactions/1

    Response Example (200 OK):

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

3. Create Transaction

    Method: POST

    URL: /transactions

    Headers: Content-Type: application/json

    Request Example:

curl -u admin:secret -X POST http://localhost:8000/transactions \
-H "Content-Type: application/json" \
-d '{"body": "TxId:67890 Withdrawal 2000 RWF Fee 50 RWF new balance 8000 RWF"}'

    Response Example (201 Created):

{
  "id": 2,
  "txid": "67890",
  "category": "Withdrawal",
  "amount": 2000,
  "fee": 50,
  "new_balance": 8000,
  "date": "2025-10-02T10:05:00Z",
  "body": "TxId:67890 Withdrawal 2000 RWF Fee 50 RWF new balance 8000 RWF"
}

4. Update Transaction

    Method: PUT

    URL: /transactions/<id>

    Request Example:

curl -u admin:secret -X PUT http://localhost:8000/transactions/2 \
-H "Content-Type: application/json" \
-d '{"body": "TxId:67890 Withdrawal 2500 RWF Fee 50 RWF new balance 7500 RWF"}'

    Response Example (200 OK):

{
  "id": 2,
  "txid": "67890",
  "category": "Withdrawal",
  "amount": 2500,
  "fee": 50,
  "new_balance": 7500,
  "date": "2025-10-02T10:05:00Z",
  "body": "TxId:67890 Withdrawal 2500 RWF Fee 50 RWF new balance 7500 RWF"
}

5. Delete Transaction

    Method: DELETE

    URL: /transactions/<id>

    Request Example:

curl -u admin:secret -X DELETE http://localhost:8000/transactions/2

    Response Example (200 OK):

{
  "deleted": 2
}

Notes

    All endpoints require Basic Auth.

    id is auto-incremented when creating new transactions.

    Transaction data is stored in memory; restarting the server reloads from the XML file.

    Basic Auth is insecure for production. Recommended alternatives:

        JWT (JSON Web Tokens)

        OAuth2
