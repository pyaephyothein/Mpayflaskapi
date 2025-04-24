using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json;

public class PaymentController : Controller
{
    private readonly string baseUrl = "https://api.stg-paymentgateway.ais.co.th/stg/service-txn-gateway/v1/cc/txns";
    private readonly string merchantId = "YOUR_MERCHANT_ID";
    private readonly string channelSecret = "YOUR_CHANNEL_SECRET";

    [HttpPost]
    public async Task<IActionResult> CreatePayment()
    {
        var payload = new
        {
            order_id = "order_001",
            product_name = "Example Product",
            service_id = "YOUR_SERVICE_ID",
            channel_type = "API",
            cust_id = "customer123",
            amount = 100.50,
            currency = "THB",
            capture = true,
            form_type = "FORM",
            skin_code = "mpay",
            is_remember = false,
            metadata = new { note = "Test transaction" },
            _3ds = new {
                _3ds_required = true,
                _3ds_url_success = "https://yourdomain.com/success",
                _3ds_url_fail = "https://yourdomain.com/fail"
            }
        };

        return await SendRequest("/payment_order", payload);
    }

    [HttpPost]
    public async Task<IActionResult> QueryTransaction([FromBody] string transactionId)
    {
        var payload = new { transaction_id = transactionId };
        return await SendRequest("/query", payload);
    }

    [HttpPost]
    public async Task<IActionResult> CancelTransaction([FromBody] string transactionId)
    {
        var payload = new {
            transaction_id = transactionId,
            cancel_reason = "User Request"
        };
        return await SendRequest("/cancel", payload);
    }

    [HttpPost]
    public async Task<IActionResult> RefundTransaction(string transactionId, decimal amount)
    {
        var payload = new {
            transaction_id = transactionId,
            amount = amount,
            refund_reason = "Customer requested refund"
        };
        return await SendRequest("/refund", payload);
    }

    private async Task<IActionResult> SendRequest(string endpoint, object payload)
    {
        string jsonPayload = JsonConvert.SerializeObject(payload);
        string nonce = Guid.NewGuid().ToString("N");
        string signature = CreateHMAC(jsonPayload, nonce, channelSecret);

        using (var client = new HttpClient())
        {
            client.DefaultRequestHeaders.Add("X-sdpg-merchant-id", merchantId);
            client.DefaultRequestHeaders.Add("X-sdpg-signature", signature);
            client.DefaultRequestHeaders.Add("X-sdpg-nonce", nonce);

            var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");
            var response = await client.PostAsync(baseUrl + endpoint, content);
            var result = await response.Content.ReadAsStringAsync();

            return Content(result, "application/json");
        }
    }

    private string CreateHMAC(string data, string nonce, string secret)
    {
        var encoding = new UTF8Encoding();
        byte[] keyByte = encoding.GetBytes(secret);
        byte[] messageBytes = encoding.GetBytes(data + nonce);
        using (var hmacsha256 = new HMACSHA256(keyByte))
        {
            byte[] hashmessage = hmacsha256.ComputeHash(messageBytes);
            return BitConverter.ToString(hashmessage).Replace("-", "").ToLower();
        }
    }
}
