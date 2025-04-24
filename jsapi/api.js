// JavaScript example to integrate mPAY ONE API v4.9 (Credit Card Payment: Payment Order, Query Status, Cancel, Refund)

const axios = require('axios');
const crypto = require('crypto');

// Configurations
const BASE_URL = 'https://api.stg-paymentgateway.ais.co.th/stg/service-txn-gateway/v1/cc/txns';
const merchantId = 'YOUR_MERCHANT_ID';
const channelSecret = 'YOUR_CHANNEL_SECRET';

// Helper to generate nonce and signature
function generateSignature(payload, nonce) {
    const dataToSign = JSON.stringify(payload) + nonce;
    const hmac = crypto.createHmac('sha256', channelSecret);
    hmac.update(dataToSign);
    return hmac.digest('hex');
}

function createHeaders(payload) {
    const nonce = crypto.randomBytes(16).toString('hex');
    const signature = generateSignature(payload, nonce);
    return {
        headers: {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-sdpg-merchant-id': merchantId,
            'X-sdpg-signature': signature,
            'X-sdpg-nonce': nonce
        }
    };
}

// 1. Create Payment Order
function createPaymentOrder() {
    const payload = {
        order_id: "order_001",
        product_name: "Example Product",
        service_id: "YOUR_SERVICE_ID",
        channel_type: "API",
        cust_id: "customer123",
        amount: 100.50,
        currency: "THB",
        capture: true,
        form_type: "FORM",
        skin_code: "mpay",
        is_remember: false,
        metadata: {
            note: "Test transaction"
        },
        "3ds": {
            "3ds_required": true,
            "3ds_url_success": "https://yourdomain.com/success",
            "3ds_url_fail": "https://yourdomain.com/fail"
        }
    };

    axios.post(`${BASE_URL}/payment_order`, payload, createHeaders(payload))
        .then(response => console.log('Create Payment:', response.data))
        .catch(error => console.error('Create Error:', error.response?.data || error.message));
}

// 2. Query Transaction Status
function queryTransactionStatus(transaction_id) {
    const payload = { transaction_id };

    axios.post(`${BASE_URL}/query`, payload, createHeaders(payload))
        .then(response => console.log('Query Status:', response.data))
        .catch(error => console.error('Query Error:', error.response?.data || error.message));
}

// 3. Cancel Transaction
function cancelTransaction(transaction_id, reason = "User request") {
    const payload = {
        transaction_id,
        cancel_reason: reason
    };

    axios.post(`${BASE_URL}/cancel`, payload, createHeaders(payload))
        .then(response => console.log('Cancel Success:', response.data))
        .catch(error => console.error('Cancel Error:', error.response?.data || error.message));
}

// 4. Refund Transaction
function refundTransaction(transaction_id, amount, reason = "Refund requested") {
    const payload = {
        transaction_id,
        amount,
        refund_reason: reason
    };

    axios.post(`${BASE_URL}/refund`, payload, createHeaders(payload))
        .then(response => console.log('Refund Success:', response.data))
        .catch(error => console.error('Refund Error:', error.response?.data || error.message));
}

// Example usage:
// createPaymentOrder();
// queryTransactionStatus("your_txn_id");
// cancelTransaction("your_txn_id");
// refundTransaction("your_txn_id", 100.50);
