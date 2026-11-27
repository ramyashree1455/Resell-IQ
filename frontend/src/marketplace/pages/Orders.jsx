import React, { useEffect, useState } from "react";
import { api, rupees } from "../api";

const STATUS_CLASS = { placed: "alert-warning", paid: "alert-info", shipped: "alert-info",
                       delivered: "alert-success", cancelled: "alert-danger" };

function Status({ s }) {
  return <span className={`alert ${STATUS_CLASS[s] || ""}`} style={{ padding: "2px 10px", display: "inline-block" }}>{s}</span>;
}

function ReviewForm({ order, onDone }) {
  const [rating, setRating] = useState(5);
  const [text, setText] = useState("");
  const [err, setErr] = useState("");
  const submit = async (e) => {
    e.preventDefault();
    try {
      await api("/reviews", { method: "POST", body: { order_id: order.id, rating, text } });
      onDone();
    } catch (x) { setErr(x.message); }
  };
  return (
    <form className="mk-stack" onSubmit={submit}>
      <div className="mk-stars">
        {[1, 2, 3, 4, 5].map((n) => (
          <button type="button" key={n} onClick={() => setRating(n)}>{n <= rating ? "★" : "☆"}</button>
        ))}
      </div>
      <input className="form-input" placeholder="How was the seller?" value={text} onChange={(e) => setText(e.target.value)} />
      {err && <div className="alert alert-danger">{err}</div>}
      <button className="btn btn-primary">Submit review</button>
    </form>
  );
}

export default function Orders({ user }) {
  const [purchases, setPurchases] = useState([]);
  const [sales, setSales] = useState([]);
  const [titles, setTitles] = useState({});
  const [reviewing, setReviewing] = useState(null);
  const [reviewed, setReviewed] = useState(new Set());
  const [msg, setMsg] = useState(null);

  const load = async () => {
    try {
      const [p, s] = await Promise.all([api("/orders"), api("/orders/sales")]);
      setPurchases(p);
      setSales(s);
      // fetch listing titles once (sold listings are still readable)
      const ids = [...new Set([...p, ...s].map((o) => o.listing_id))].filter((id) => !titles[id]);
      const found = await Promise.all(ids.map((id) => api(`/listings/${id}`).catch(() => null)));
      setTitles((t) => ({ ...t, ...Object.fromEntries(found.filter(Boolean).map((l) => [l.id, l.title])) }));
    } catch (e) { setMsg({ type: "danger", text: e.message }); }
  };
  useEffect(() => { load(); }, []);

  const setStatus = async (o, status) => {
    try {
      await api(`/orders/${o.id}/status`, { method: "PATCH", body: { status } });
      load();
    } catch (e) { setMsg({ type: "danger", text: e.message }); }
  };

  const name = (o) => titles[o.listing_id] || `Listing #${o.listing_id}`;

  return (
    <div className="mk-stack">
      <div className="page-header"><h1 className="page-title">Orders</h1></div>
      {msg && <div className={`alert alert-${msg.type}`}>{msg.text}</div>}

      <div className="card mk-stack">
        <h3 className="card-title">My purchases</h3>
        {purchases.length === 0 ? <p className="mk-muted">No purchases yet.</p> : (
          <table className="data-table">
            <thead><tr><th>Item</th><th>Amount</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              {purchases.map((o) => (
                <React.Fragment key={o.id}>
                  <tr>
                    <td>{name(o)}</td>
                    <td>{rupees(o.amount)}</td>
                    <td><Status s={o.status} /></td>
                    <td>
                      {o.status === "placed" && <button className="btn btn-secondary" onClick={() => setStatus(o, "cancelled")}>Cancel</button>}
                      {o.status === "shipped" && <button className="btn btn-primary" onClick={() => setStatus(o, "delivered")}>Mark received</button>}
                      {o.status === "delivered" && !reviewed.has(o.id) && (
                        <button className="btn btn-secondary" onClick={() => setReviewing(reviewing === o.id ? null : o.id)}>Review seller</button>
                      )}
                      {reviewed.has(o.id) && <span className="mk-muted">Reviewed ✓</span>}
                    </td>
                  </tr>
                  {reviewing === o.id && (
                    <tr><td colSpan={4}>
                      <ReviewForm order={o} onDone={() => { setReviewed(new Set([...reviewed, o.id])); setReviewing(null); }} />
                    </td></tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {(user.role === "seller" || sales.length > 0) && (
        <div className="card mk-stack">
          <h3 className="card-title">My sales</h3>
          {sales.length === 0 ? <p className="mk-muted">No sales yet.</p> : (
            <table className="data-table">
              <thead><tr><th>Item</th><th>Amount</th><th>Buyer</th><th>Status</th><th>Action</th></tr></thead>
              <tbody>
                {sales.map((o) => (
                  <tr key={o.id}>
                    <td>{name(o)}</td>
                    <td>{rupees(o.amount)}</td>
                    <td>User #{o.buyer_id}</td>
                    <td><Status s={o.status} /></td>
                    <td>{o.status === "paid" && <button className="btn btn-primary" onClick={() => setStatus(o, "shipped")}>Mark shipped</button>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
