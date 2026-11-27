import React, { useEffect, useState } from "react";
import { api, imageUrl, rupees } from "../api";

const EMPTY = { title: "", category: "phones", price: "", location: "", description: "" };
const VIEWS = ["front", "back", "side", "screen", "closeup"];

export default function Sell() {
  const [form, setForm] = useState(EMPTY);
  const [created, setCreated] = useState(null);         // listing we are adding photos to
  const [file, setFile] = useState(null);
  const [view, setView] = useState("front");
  const [mine, setMine] = useState([]);
  const [msg, setMsg] = useState(null);
  const [me, setMe] = useState(null);

  const loadMine = async (meId = me?.id) => {
    if (!meId) return;
    const all = await api("/listings?limit=100");
    setMine(all.filter((l) => l.seller_id === meId));
  };

  useEffect(() => {
    api("/auth/me").then((u) => { setMe(u); loadMine(u.id); }).catch(() => {});
  }, []);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const create = async (e) => {
    e.preventDefault();
    setMsg(null);
    try {
      const l = await api("/listings", { method: "POST", body: { ...form, price: Number(form.price) } });
      setCreated(l);
      setForm(EMPTY);
      setMsg({ type: "success", text: `Listed "${l.title}". Now add photos.` });
      loadMine();
    } catch (err) {
      setMsg({ type: "danger", text: err.message });
    }
  };

  const upload = async (e) => {
    e.preventDefault();
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    try {
      await api(`/listings/${created.id}/images?view_type=${view}`, { method: "POST", form: fd });
      setCreated(await api(`/listings/${created.id}`));
      setFile(null);
      e.target.reset();
      loadMine();
    } catch (err) {
      setMsg({ type: "danger", text: err.message });
    }
  };

  const remove = async (l) => {
    if (!window.confirm(`Remove "${l.title}" from the marketplace?`)) return;
    await api(`/listings/${l.id}`, { method: "PUT", body: { status: "removed" } });
    if (created?.id === l.id) setCreated(null);
    loadMine();
  };

  return (
    <div className="mk-stack">
      <div className="page-header">
        <h1 className="page-title">Sell an item</h1>
        <p className="page-subtitle">
          Create the listing, add photos, then run the <a href="/">AI condition inspection</a> to get it graded.
        </p>
      </div>
      {msg && <div className={`alert alert-${msg.type}`}>{msg.text}</div>}

      <div className="mk-two">
        <form className="card mk-stack" onSubmit={create}>
          <h3 className="card-title">1. Listing details</h3>
          <div className="form-group"><label className="form-label">Title</label>
            <input className="form-input" value={form.title} onChange={set("title")} placeholder="iPhone 12, 128 GB" required /></div>
          <div className="form-group"><label className="form-label">Category</label>
            <select className="form-select" value={form.category} onChange={set("category")}>
              {["phones", "laptops", "tablets", "cameras", "electronics", "furniture", "other"].map((c) => <option key={c}>{c}</option>)}
            </select></div>
          <div className="form-group"><label className="form-label">Price (₹)</label>
            <input className="form-input" type="number" min="1" value={form.price} onChange={set("price")} required /></div>
          <div className="form-group"><label className="form-label">Location</label>
            <input className="form-input" value={form.location} onChange={set("location")} placeholder="Udupi" /></div>
          <div className="form-group"><label className="form-label">Description</label>
            <textarea className="form-textarea" rows={3} value={form.description} onChange={set("description")} /></div>
          <button className="btn btn-primary">Create listing</button>
        </form>

        <div className="card mk-stack">
          <h3 className="card-title">2. Photos</h3>
          {!created ? (
            <p className="mk-muted">Create a listing first, or pick one of yours below.</p>
          ) : (
            <>
              <div className="mk-muted">Adding photos to <strong>{created.title}</strong></div>
              <div className="mk-row">
                {created.images.map((img) => (
                  <img key={img.id} src={imageUrl(img.url)} alt={img.view_type} title={img.view_type}
                       style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 8 }} />
                ))}
              </div>
              <form className="mk-stack" onSubmit={upload}>
                <select className="form-select" value={view} onChange={(e) => setView(e.target.value)}>
                  {VIEWS.map((v) => <option key={v}>{v}</option>)}
                </select>
                <input className="form-input" type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
                <button className="btn btn-primary" disabled={!file}>Upload photo</button>
              </form>
            </>
          )}
        </div>
      </div>

      <div className="card mk-stack">
        <h3 className="card-title">Your live listings</h3>
        {mine.length === 0 ? <p className="mk-muted">Nothing listed yet.</p> : (
          <table className="data-table">
            <thead><tr><th>Item</th><th>Price</th><th>Grade</th><th>Photos</th><th></th></tr></thead>
            <tbody>
              {mine.map((l) => (
                <tr key={l.id}>
                  <td>{l.title}</td>
                  <td>{rupees(l.price)}</td>
                  <td>{l.grade || "—"}</td>
                  <td>{l.images.length}</td>
                  <td className="mk-row">
                    <button className="btn btn-secondary" onClick={() => setCreated(l)}>Add photos</button>
                    <button className="btn btn-danger" onClick={() => remove(l)}>Remove</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
