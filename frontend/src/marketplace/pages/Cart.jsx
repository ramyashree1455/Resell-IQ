import React, { useEffect, useState } from "react";
import { api, rupees } from "../api";
import { payForCart } from "../payments";

export default function Cart({ user, onPaid }) {
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [msg, setMsg] = useState(null);
  const [paying, setPaying] = useState(false);

  const load = () => api("/cart").then(setCart).catch((e) => setMsg({ type: "danger", text: e.message }));
  useEffect(() => { load(); }, []);

  const remove = async (id) => setCart(await api(`/cart/${id}`, { method: "DELETE" }));

  const pay = async () => {
    setPaying(true);
    setMsg(null);
    try {
      const orders = await payForCart({ name: user.name, email: user.email });
      setMsg({ type: "success", text: `Payment successful. ${orders.length} order(s) placed.` });
      setTimeout(onPaid, 1200);
    } catch (err) {
      setMsg({ type: "danger", text: err.message });
      load();
    } finally {
      setPaying(false);
    }
  };

  return (
    <div className="mk-stack">
      <div className="page-header"><h1 className="page-title">Your cart</h1></div>
      {msg && <div className={`alert alert-${msg.type}`}>{msg.text}</div>}
      {cart.items.length === 0 ? (
        <div className="card mk-muted">Your cart is empty. Find something in Browse.</div>
      ) : (
        <div className="card mk-stack">
          <table className="data-table">
            <thead><tr><th>Item</th><th>Price</th><th></th></tr></thead>
            <tbody>
              {cart.items.map((i) => (
                <tr key={i.listing_id}>
                  <td>{i.title}</td>
                  <td>{rupees(i.price)}</td>
                  <td><button className="btn btn-secondary" onClick={() => remove(i.listing_id)}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mk-between">
            <div className="mk-price">Total: {rupees(cart.total)}</div>
            <button className="btn btn-primary" onClick={pay} disabled={paying}>
              {paying ? "Processing..." : "Pay with Razorpay (test)"}
            </button>
          </div>
          <p className="mk-muted">Test mode: no real money moves. Without Razorpay keys, payment is simulated.</p>
        </div>
      )}
    </div>
  );
}
