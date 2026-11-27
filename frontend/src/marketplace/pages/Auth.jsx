import React, { useState } from "react";
import { api, login } from "../api";

export default function Auth({ onLoggedIn }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "buyer" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "register") {
        await api("/auth/register", { method: "POST", body: form });
      }
      onLoggedIn(await login(form.email, form.password));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card mk-auth">
      <h2 className="card-title">{mode === "login" ? "Log in" : "Create an account"}</h2>
      <form className="mk-stack" onSubmit={submit}>
        {mode === "register" && (
          <div className="form-group">
            <label className="form-label">Name</label>
            <input className="form-input" value={form.name} onChange={set("name")} required />
          </div>
        )}
        <div className="form-group">
          <label className="form-label">Email</label>
          <input className="form-input" type="email" value={form.email} onChange={set("email")} required />
        </div>
        <div className="form-group">
          <label className="form-label">Password</label>
          <input className="form-input" type="password" minLength={6} value={form.password}
                 onChange={set("password")} required />
        </div>
        {mode === "register" && (
          <div className="form-group">
            <label className="form-label">I want to</label>
            <select className="form-select" value={form.role} onChange={set("role")}>
              <option value="buyer">Buy items</option>
              <option value="seller">Sell items</option>
            </select>
          </div>
        )}
        {error && <div className="alert alert-danger">{error}</div>}
        <button className="btn btn-primary" disabled={busy}>
          {busy ? "Please wait..." : mode === "login" ? "Log in" : "Register"}
        </button>
      </form>
      <p className="mk-muted" style={{ marginTop: 12 }}>
        {mode === "login" ? "New here? " : "Already have an account? "}
        <a href="#" onClick={(e) => { e.preventDefault(); setMode(mode === "login" ? "register" : "login"); setError(""); }}>
          {mode === "login" ? "Create an account" : "Log in"}
        </a>
      </p>
    </div>
  );
}
