// Razorpay Checkout (test mode) for ReSellIQ.
// Usage in a React component:
//   import { payForCart } from '../api/payments'
//   await payForCart({ name: user.name, email: user.email })
import client from './client'   // your shared axios instance with the auth header

function loadRazorpayScript() {
  return new Promise((resolve, reject) => {
    if (window.Razorpay) return resolve()
    const s = document.createElement('script')
    s.src = 'https://checkout.razorpay.com/v1/checkout.js'
    s.onload = resolve
    s.onerror = () => reject(new Error('Could not load Razorpay'))
    document.body.appendChild(s)
  })
}

export async function payForCart(prefill = {}) {
  // 1. backend turns the cart into orders + a Razorpay order
  const { data: co } = await client.post('/orders/checkout')

  // Mock mode (no Razorpay keys in .env): skip the popup, pretend it succeeded
  if (co.mock) {
    const { data } = await client.post('/orders/verify', {
      razorpay_order_id: co.razorpay_order_id,
      razorpay_payment_id: 'pay_mock_' + Date.now(),
      razorpay_signature: 'mock_signature',
    })
    return data
  }

  // 2. open the Razorpay popup
  await loadRazorpayScript()
  return new Promise((resolve, reject) => {
    const rzp = new window.Razorpay({
      key: co.key_id,
      amount: co.amount,            // paise
      currency: co.currency,
      order_id: co.razorpay_order_id,
      name: 'ReSellIQ',
      description: 'Order payment (test mode)',
      prefill,
      // 3. after payment, the backend checks the signature and marks orders paid
      handler: async (resp) => {
        try {
          const { data } = await client.post('/orders/verify', resp)
          resolve(data)
        } catch (e) { reject(e) }
      },
      modal: { ondismiss: () => reject(new Error('Payment cancelled')) },
    })
    rzp.on('payment.failed', (r) => reject(new Error(r.error.description)))
    rzp.open()
  })
}
