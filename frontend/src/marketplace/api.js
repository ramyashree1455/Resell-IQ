// Talks to the FastAPI backend. The login token is kept in localStorage.
export const BACKEND_URL = "http://127.0.0.1:8000";

export const getToken = () => localStorage.getItem("reselliq_token");
export const setToken = (t) =>
  t ? localStorage.setItem("reselliq_token", t) : localStorage.removeItem("reselliq_token");

export const imageUrl = (path) => (path?.startsWith("http") ? path : `${BACKEND_URL}${path}`);

// api("/cart")                         -> GET
// api("/cart", { method: "POST", body: { listing_id: 1 } })
export async function api(path, { method = "GET", body, form } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let payload;
  if (form) {
    payload = form;                                   // FormData (file upload)
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${BACKEND_URL}${path}`, { method, headers, body: payload });
  } catch {
    throw new Error("Cannot reach the backend. Is uvicorn running on port 8000?");
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const d = data?.detail;
    const msg = Array.isArray(d) ? d.map((e) => e.msg).join(", ") : d || `Error ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export async function login(email, password) {
  // FastAPI's OAuth2 login expects a form with "username" and "password"
  const res = await fetch(`${BACKEND_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username: email, password }),
  }).catch(() => {
    throw new Error("Cannot reach the backend. Is uvicorn running on port 8000?");
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.detail || "Login failed");
  setToken(data.access_token);
  return api("/auth/me");
}

export const rupees = (n) => `₹${Number(n || 0).toLocaleString("en-IN")}`;
