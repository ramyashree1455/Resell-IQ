import React, { useEffect, useRef, useState } from "react";
import { api } from "../api";

export default function Messages({ user, target }) {
  const [convos, setConvos] = useState([]);
  const [active, setActive] = useState(target);       // {listingId, otherUserId}
  const [thread, setThread] = useState([]);
  const [titles, setTitles] = useState({});
  const [text, setText] = useState("");
  const [err, setErr] = useState("");
  const bottom = useRef(null);

  const loadConvos = async () => {
    const list = await api("/chats");
    setConvos(list);
    const ids = [...new Set(list.map((c) => c.listing_id).concat(target ? [target.listingId] : []))];
    const found = await Promise.all(ids.map((id) => api(`/listings/${id}`).catch(() => null)));
    setTitles(Object.fromEntries(found.filter(Boolean).map((l) => [l.id, l.title])));
  };

  const loadThread = async (c = active) => {
    if (!c) return;
    const q = c.otherUserId ? `?other_user_id=${c.otherUserId}` : "";
    setThread(await api(`/chats/${c.listingId}/messages${q}`));
  };

  useEffect(() => { loadConvos().catch((e) => setErr(e.message)); }, []);

  // refresh the open chat every 5 seconds (simple polling)
  useEffect(() => {
    loadThread().catch((e) => setErr(e.message));
    const t = setInterval(() => { loadThread().catch(() => {}); loadConvos().catch(() => {}); }, 5000);
    return () => clearInterval(t);
  }, [active]);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: "smooth" }); }, [thread.length]);

  const send = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setErr("");
    try {
      await api(`/chats/${active.listingId}/messages`, {
        method: "POST",
        body: { body: text, receiver_id: active.otherUserId },
      });
      setText("");
      loadThread();
      loadConvos();
    } catch (x) { setErr(x.message); }
  };

  const isActive = (c) => active && c.listing_id === active.listingId && c.other_user_id === active.otherUserId;

  return (
    <div className="mk-stack">
      <div className="page-header"><h1 className="page-title">Messages</h1></div>
      <div className="card mk-chat">
        <div className="mk-stack" style={{ gap: 8 }}>
          {convos.length === 0 && !active && <p className="mk-muted">No conversations yet. Open an item and click "Message seller".</p>}
          {convos.map((c) => (
            <div key={`${c.listing_id}-${c.other_user_id}`} className={`mk-convo ${isActive(c) ? "active" : ""}`}
                 onClick={() => setActive({ listingId: c.listing_id, otherUserId: c.other_user_id })}>
              <div className="mk-between">
                <strong>{titles[c.listing_id] || `Listing #${c.listing_id}`}</strong>
                {c.unread > 0 && <span className="mk-badge">{c.unread}</span>}
              </div>
              <div className="mk-muted">User #{c.other_user_id}: {c.last_message.slice(0, 40)}</div>
            </div>
          ))}
        </div>

        <div className="mk-stack">
          {!active ? <p className="mk-muted">Pick a conversation.</p> : (
            <>
              <strong>{titles[active.listingId] || `Listing #${active.listingId}`} · User #{active.otherUserId}</strong>
              <div className="mk-thread">
                {thread.length === 0 && <p className="mk-muted">Say hello 👋</p>}
                {thread.map((m) => (
                  <div key={m.id} className={`mk-msg ${m.sender_id === user.id ? "mine" : ""}`}>{m.body}</div>
                ))}
                <div ref={bottom} />
              </div>
              {err && <div className="alert alert-danger">{err}</div>}
              <form className="mk-row" onSubmit={send}>
                <input className="form-input" style={{ flex: 1 }} placeholder="Type a message"
                       value={text} onChange={(e) => setText(e.target.value)} />
                <button className="btn btn-primary">Send</button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
