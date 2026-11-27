// Razorpay Checkout (test mode). With no keys in backend .env, mock mode skips the popup.
import { api } from "./api";

function loadRazorpay() {
  return new Promise((resolve, reject) => {
    if (window.Razorpay) return resolve();
    const s = document.createElement("script");
    s.src = "https://checkout.razorpay.com/v1/checkout.js";
    s.onload = resolve;
    s.onerror = () => reject(new Error("Could not load Razorpay"));
    document.body.appendChild(s);
  });
}

export async function payForCart(prefill = {}) {
  const co = await api("/orders/checkout", { method: "POST" });

  if (co.mock) {
    return api("/orders/verify", {
      method: "POST",
      body: {
        razorpay_order_id: co.razorpay_order_id,
        razorpay_payment_id: "pay_mock_" + Date.now(),
        razorpay_signature: "mock_signature",
      },
    });
  }

  await loadRazorpay();
  return new Promise((resolve, reject) => {
    const rzp = new window.Razorpay({
      key: co.key_id,
      amount: co.amount,
      currency: co.currency,
      order_id: co.razorpay_order_id,
      name: "ReSellIQ",
      description: "Order payment (test mode)",
      prefill,
      handler: (resp) => api("/orders/verify", { method: "POST", body: resp }).then(resolve, reject),
      modal: { ondismiss: () => reject(new Error("Payment cancelled")) },
    });
    rzp.on("payment.failed", (r) => reject(new Error(r.error.description)));
    rzp.open();
  });
}
