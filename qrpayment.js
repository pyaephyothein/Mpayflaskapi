fetch("https://onepay-api.onrender.com/pay/qr")
  .then(res => res.json())
  .then(data => {
    if (data.qr_image_url) {
      document.getElementById("qrContainer").src = data.qr_image_url;
    }
  });