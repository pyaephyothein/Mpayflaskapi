from flask import Flask, jsonify, request,redirect

import requests
import uuid
import json
import hmac
import hashlib
from datetime import datetime, timedelta
import sqlite3
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Configure the Values 

MERCHANT_ID = "your marchant id"
CHANNEL_SECRET = "your_channel_secret"
SERVICE_ID = "your_service_id"
PAYMENT_URL = "https://api.stg-paymentgateway.ais.co.th/stg/service-txn-gateway/v1/cc/txns/payment_order"
QR_PAYMENT_URL = "https://api.stg-paymentgateway.ais.co.th/stg/service-txn-gateway/v1/qrcode/txns/payment_order"

# Database setup 

DB_PATH = 'payment.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute ('''
                    CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_id TEXT,
            order_id TEXT,
            amount TEXT,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit
    conn.close()

init_db()

def log_payment(txn_id, order_id, amount, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PAYMENT (txn_id, order_id, amount, status) VALUE (?,?,?,?)",
                   (txn_id, order_id, amount, status))
    conn.commit
    conn.close()

def update_payment_status (txn_id, ordet_id, amount, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("Update Payment SET status = ? WHERE txn_id = ?", (status, txn_id) )
    conn.commit
    conn.close()

def generate_signature(secret, body, nonce):
    message = body + nonce
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest().upper()
    return signature

@app.route ("/")
def home():
    return "Welcome to mPay One API Page"

@app.route ('/pay', methods=['GET'])
def initate_payment():
    txn_id = "T" + datetime.now().strftime("%Y%m%d%H%M%S%f")
    nonce = uuid.uuid4().hex
    order_id = "ORDER001"

    payload = {
        "service_id": SERVICE_ID,
        "txn_id": txn_id,
        "amount": "100.00",
        "currency": "THB",
        "cust_id": "CUST001",
        "order_id": order_id
    }

    body_json = json.dumps(payload, separators=(',', ':'))
    signature = generate_signature(CHANNEL_SECRET,body_json, nonce)

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-sdpg-merchant-id": MERCHANT_ID,
        "X-sdpg-signature": signature,
        "X-sdpg-nonce": nonce
    }

    response = request.post (QR_PAYMENT_URL, headers=headers, data=body_json)

    if response.status_code == 200:
        res_data = response.json()
        log_payment(txn_id, order_id, "100.00", res_data.get("status", "pending"))
        return jsonify(res_data)
    else:
        return jsonify({"error": "QR Payment initiation failed", "status_code": response.status_code})
    
@app.route ('/cancel_pending', methods = ['POST'])
def cancel_pending_orders():
    cutoff_time = datetime.now() - timedelta(minutes=30)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT txn_id FROM payments WHERE status = 'pending' AND created_at <?", (cutoff_time))
    to_cancel = cursor.fetchall()
    for txn_id in to_cancel:
        update_payment_status(txn_id[0], 'cancelled')
        conn.close()
        return jsonify({"cancelled_txns": [txn[0] for txn in to_cancel]})
    
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5000)

