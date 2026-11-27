import React, { useEffect, useState } from "react";
import { api, imageUrl, rupees } from "../api";

const EMPTY = { q: "", category: "", min_price: "", max_price: "", grade: "", location: "" };

export default function Browse({ user, onNeedLogin, onOpenChat }) {
  const [filters, setFilters] = useState(EMPTY);
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [msg, setMsg] = useState(null);       // {type, text}
  const [loading, setLoading] = useState(false);

  const search = async (f = filters) => {
    setLoading(true);
    const params = new URLSearchParams(Object.entries(f).filter(([, v]) => v !== ""));
    try {
      setItems(await api(`/listings?${params}`));
    } catch (err) {
      setMsg({ type: "danger", text: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { search(); }, []);

  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });

  const addToCart = async (listing) => {
    if (!user) return onNeedLogin();
    try {
      await api("/cart", { method: "POST", body: { listing_id: listing.id } });
      setMsg({ type: "success", text: `Added "${listing.title}" to your cart.` });
    } catch (err) {
      setMsg({ type: "danger", text: err.message });
    }
  };

  const messageSeller = (listing) => {
    if (!user) return onNeedLogin();
    onOpenChat(listing.id, listing.seller_id);
  };

  if (selected) {
    const l = selected;
    const own = user && user.id === l.seller_id;
    return (
      <div className="card mk-stack">
        <button className="btn btn-secondary" style={{ alignSelf: "flex-start" }} onClick={() => setSelected(null)}>
          ← Back to results
        </button>
        {msg && <div className={`alert alert-${msg.type}`}>{msg.text}</div>}
        <div className="mk-two">
          <div className="mk-stack">
            {l.images.length ? (
              l.images.map((img) => <img key={img.id} className="mk-thumb" style={{ height: 260 }} src={imageUrl(img.url)} alt={img.view_type} />)
            ) : (
              <div className="mk-thumb" style={{ height: 260 }}>No photos yet</div>
            )}
          </div>
          <div className="mk-stack">
            <h2 className="page-title">{l.title}</h2>
            <div className="mk-price">{rupees(l.price)}</div>
            <div className="mk-row">
              <span className="mk-badge">{l.category}</span>
              {l.grade ? <span className={`cert-grade-badge-sm grade-${l.grade}`}>Grade {l.grade}{l.grade_score != null && ` · ${l.grade_score}/100`}</span>
                       : <span className="mk-muted">Not graded yet</span>}
            </div>
            {l.location && <div className="mk-muted">📍 {l.location}</div>}
            <p>{l.description || <span className="mk-muted">No description.</span>}</p>
            {own ? (
              <div className="alert alert-info">This is your listing.</div>
            ) : (
              <div className="mk-row">
                <button className="btn btn-primary" onClick={() => addToCart(l)}>Add to cart</button>
                <button className="btn btn-secondary" onClick={() => messageSeller(l)}>Message seller</button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mk-stack">
      <div className="page-header">
        <h1 className="page-title">Browse items</h1>
        <p className="page-subtitle">Every grade comes from the AI condition interview.</p>
      </div>

      <form className="card mk-filters" onSubmit={(e) => { e.preventDefault(); search(); }}>
        <div className="form-group"><label className="form-label">Search</label>
          <input className="form-input" placeholder="e.g. iPhone" value={filters.q} onChange={set("q")} /></div>
        <div className="form-group"><label className="form-label">Category</label>
          <input className="form-input" placeholder="phones" value={filters.category} onChange={set("category")} /></div>
        <div className="form-group"><label className="form-label">Min ₹</label>
          <input className="form-input" type="number" min="0" value={filters.min_price} onChange={set("min_price")} /></div>
        <div className="form-group"><label className="form-label">Max ₹</label>
          <input className="form-input" type="number" min="0" value={filters.max_price} onChange={set("max_price")} /></div>
        <div className="form-group"><label className="form-label">Grade</label>
          <select className="form-select" value={filters.grade} onChange={set("grade")}>
            <option value="">Any</option>{["A", "B", "C", "D"].map((g) => <option key={g}>{g}</option>)}
          </select></div>
        <div className="form-group"><label className="form-label">Location</label>
          <input className="form-input" value={filters.location} onChange={set("location")} /></div>
        <div className="mk-row">
          <button className="btn btn-primary">Search</button>
          <button type="button" className="btn btn-secondary" onClick={() => { setFilters(EMPTY); search(EMPTY); }}>Clear</button>
        </div>
      </form>

      {msg && <div className={`alert alert-${msg.type}`}>{msg.text}</div>}
      {loading ? <p className="mk-muted">Loading...</p> : items.length === 0 ? (
        <div className="card mk-muted">No items found. Try clearing the filters, or log in as a seller and list something.</div>
      ) : (
        <div className="mk-grid">
          {items.map((l) => (
            <div key={l.id} className="card mk-item" onClick={() => { setSelected(l); setMsg(null); }}>
              {l.images[0] ? <img className="mk-thumb" src={imageUrl(l.images[0].url)} alt={l.title} />
                           : <div className="mk-thumb">No photo</div>}
              <div className="mk-between">
                <strong>{l.title}</strong>
                {l.grade && <span className={`cert-grade-badge-sm grade-${l.grade}`}>{l.grade}</span>}
              </div>
              <div className="mk-price">{rupees(l.price)}</div>
              <div className="mk-muted">{l.category}{l.location && ` · ${l.location}`}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
