import React, { useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";
import Auth from "./pages/Auth";
import Browse from "./pages/Browse";
import Sell from "./pages/Sell";
import Cart from "./pages/Cart";
import Orders from "./pages/Orders";
import Messages from "./pages/Messages";
import Admin from "./pages/Admin";

// which tabs each role sees
const TABS = [
  { id: "browse", label: "Browse", roles: ["guest", "buyer", "seller", "admin"] },
  { id: "sell", label: "Sell", roles: ["seller", "admin"] },
  { id: "cart", label: "Cart", roles: ["buyer", "seller", "admin"] },
  { id: "orders", label: "Orders", roles: ["buyer", "seller", "admin"] },
  { id: "messages", label: "Messages", roles: ["buyer", "seller", "admin"] },
  { id: "admin", label: "Admin", roles: ["admin"] },
];

export default function MarketApp() {
  const [user, setUser] = useState(null);
  const [tab, setTab] = useState("browse");
  const [chatTarget, setChatTarget] = useState(null);   // {listingId, otherUserId} from Browse
  const [theme, setTheme] = useState(() => localStorage.getItem("reselliq_theme") || "light");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("reselliq_theme", theme);
  }, [theme]);

  // stay logged in after a page refresh
  useEffect(() => {
    if (getToken()) api("/auth/me").then(setUser).catch(() => setToken(null));
  }, []);

  const role = user?.role || "guest";
  const visible = TABS.filter((t) => t.roles.includes(role));

  const logout = () => {
    setToken(null);
    setUser(null);
    setTab("browse");
  };

  const openChat = (listingId, otherUserId) => {
    setChatTarget({ listingId, otherUserId });
    setTab("messages");
  };

  const needsLogin = !user && tab !== "browse";

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-brand">
          <span className="brand-title">ReSellIQ</span>
          <span className="brand-badge">Marketplace</span>
        </div>
        <div className="nav-tabs">
          {visible.map((t) => (
            <button key={t.id} className={`nav-tab ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)}>
              {t.label}
            </button>
          ))}
          <a className="nav-tab" href="/">AI Inspection</a>
        </div>
        <div className="mk-row">
          {user ? (
            <>
              <span className="mk-muted">{user.name} · {user.role}</span>
              <button className="btn btn-secondary" onClick={logout}>Log out</button>
            </>
          ) : (
            <button className="btn btn-primary" onClick={() => setTab("login")}>Log in</button>
          )}
          <button className="theme-toggle-btn" onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
            {theme === "light" ? "Dark Mode" : "Light Mode"}
          </button>
        </div>
      </nav>

      <main className="main-content">
        {(tab === "login" || needsLogin) && !user && (
          <Auth onLoggedIn={(u) => { setUser(u); setTab(u.role === "seller" ? "sell" : "browse"); }} />
        )}
        {tab === "browse" && (
          <Browse user={user} onNeedLogin={() => setTab("login")} onOpenChat={openChat} />
        )}
        {user && tab === "sell" && <Sell />}
        {user && tab === "cart" && <Cart user={user} onPaid={() => setTab("orders")} />}
        {user && tab === "orders" && <Orders user={user} />}
        {user && tab === "messages" && <Messages user={user} target={chatTarget} />}
        {user && tab === "admin" && <Admin user={user} />}
      </main>
    </div>
  );
}
