public async Task<ActionResult> PayNow()
{
    var httpClient = new HttpClient();
    var result = await httpClient.GetAsync("https://onepay-api.onrender.com/pay");
    var json = await result.Content.ReadAsStringAsync();
    var paymentResponse = JsonConvert.DeserializeObject<PaymentResponse>(json);
    
    if (paymentResponse.form_url != null)
        return Redirect(paymentResponse.form_url);
    
    return Content("Failed to generate payment link");
}
