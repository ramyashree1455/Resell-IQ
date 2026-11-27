import React, { useEffect, useState } from "react";
import { api, rupees } from "../api";

export default function Admin({ user }) {
  const [stats, setStats] = useState(null);
  const [queue, setQueue] = useState([]);
  const [listings, setListings] = useState([]);
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [view, setView] = useState("queue");
  const [msg, setMsg] = useState(null);

  const load = async () => {
    try {
      const [s, q, l, u, o] = await Promise.all([
        api("/admin/stats"), api("/admin/review-queue"), api("/admin/listings"),
        api("/admin/users"), api("/admin/orders"),
      ]);
      setStats(s); setQueue(q); setListings(l); setUsers(u); setOrders(o);
    } catch (e) { setMsg({ type: "danger", text: e.message }); }
  };
  useEffect(() => { load(); }, []);

  const act = async (path, body, done) => {
    try {
      await api(path, { method: "PATCH", body });
      setMsg({ type: "success", text: done });
      load();
    } catch (e) { setMsg({ type: "danger", text: e.message }); }
  };

  const setListing = (l, status) => act(`/admin/listings/${l.id}`, { status }, `"${l.title}" is now ${status}.`);
  const setRole = (u, role) => act(`/admin/users/${u.id}`, { role }, `${u.name} is now ${role}.`);

  return (
    <div className="mk-stack">
      <div className="page-header"><h1 className="page-title">Admin</h1></div>
      {msg && <div className={`alert alert-${msg.type}`}>{msg.text}</div>}

      {stats && (
        <div className="stat-cards-grid">
          {[["Users", stats.users], ["Active listings", stats.listings_active],
            ["Waiting for review", stats.listings_in_review], ["Paid orders", stats.orders_paid],
            ["Revenue", rupees(stats.revenue)]].map(([label, value]) => (
            <div key={label} className="card stat-card">
              <div className="stat-card-label">{label}</div>
              <div className="stat-card-number">{value}</div>
            </div>
          ))}
        </div>
      )}

      <div className="filter-pills">
        {[["queue", `Review queue (${queue.length})`], ["listings", "Listings"], ["users", "Users"], ["orders", "Orders"]].map(([id, label]) => (
          <button key={id} className={`filter-pill ${view === id ? "active" : ""}`} onClick={() => setView(id)}>{label}</button>
        ))}
      </div>

      <div className="card">
        {view === "queue" && (queue.length === 0 ? <p className="mk-muted">Nothing waiting. Low-confidence AI grades land here.</p> : (
          <table className="data-table">
            <thead><tr><th>Item</th><th>Price</th><th>AI grade</th><th>Seller</th><th>Decision</th></tr></thead>
            <tbody>{queue.map((l) => (
              <tr key={l.id}>
                <td>{l.title}</td><td>{rupees(l.price)}</td><td>{l.grade || "—"}</td><td>#{l.seller_id}</td>
                <td className="mk-row">
                  <button className="btn btn-primary" onClick={() => setListing(l, "active")}>Approve</button>
                  <button className="btn btn-danger" onClick={() => setListing(l, "removed")}>Reject</button>
                </td>
              </tr>))}
            </tbody>
          </table>
        ))}

        {view === "listings" && (
          <table className="data-table">
            <thead><tr><th>Item</th><th>Price</th><th>Status</th><th>Seller</th><th>Action</th></tr></thead>
            <tbody>{listings.map((l) => (
              <tr key={l.id}>
                <td>{l.title}</td><td>{rupees(l.price)}</td><td>{l.status}</td><td>#{l.seller_id}</td>
                <td>
                  {l.status === "active" && <button className="btn btn-danger" onClick={() => setListing(l, "removed")}>Remove</button>}
                  {l.status === "removed" && <button className="btn btn-secondary" onClick={() => setListing(l, "active")}>Restore</button>}
                  {l.status === "review" && <button className="btn btn-primary" onClick={() => setListing(l, "active")}>Approve</button>}
                </td>
              </tr>))}
            </tbody>
          </table>
        )}

        {view === "users" && (
          <table className="data-table">
            <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Rating</th><th>Action</th></tr></thead>
            <tbody>{users.map((u) => (
              <tr key={u.id}>
                <td>{u.name}</td><td>{u.email}</td><td>{u.role}</td><td>{u.rating ?? "—"}</td>
                <td>
                  {u.id === user.id ? <span className="mk-muted">You</span> : u.role === "banned" ? (
                    <button className="btn btn-secondary" onClick={() => setRole(u, "buyer")}>Unban</button>
                  ) : (
                    <button className="btn btn-danger" onClick={() => setRole(u, "banned")}>Ban</button>
                  )}
                </td>
              </tr>))}
            </tbody>
          </table>
        )}

        {view === "orders" && (orders.length === 0 ? <p className="mk-muted">No orders yet.</p> : (
          <table className="data-table">
            <thead><tr><th>#</th><th>Listing</th><th>Buyer</th><th>Seller</th><th>Amount</th><th>Status</th></tr></thead>
            <tbody>{orders.map((o) => (
              <tr key={o.id}>
                <td>{o.id}</td><td>#{o.listing_id}</td><td>#{o.buyer_id}</td><td>#{o.seller_id}</td>
                <td>{rupees(o.amount)}</td><td>{o.status}</td>
              </tr>))}
            </tbody>
          </table>
        ))}
      </div>
    </div>
  );
}
