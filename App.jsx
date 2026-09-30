import { useEffect, useState } from "react";
import api, { errMsg } from "./api";
import Dashboard from "./Dashboard.jsx";

function Auth({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [err, setErr] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async () => {
    setErr("");
    try {
      const r = mode === "register"
        ? await api.post("/auth/register", f)
        : await api.post("/auth/login", new URLSearchParams({ username: f.email, password: f.password }));
      localStorage.setItem("token", r.data.access_token);
      onAuth();
    } catch (e) { setErr(errMsg(e)); }
  };

  return (
    <div className="wrap" style={{ maxWidth: 420 }}>
      <div className="card">
        <h2>Credit Assistant</h2>
        <p className="note">Track your CIBIL score and get a plan to improve it.</p>
        {mode === "register" && (<><label>Name</label><input value={f.name} onChange={set("name")} /></>)}
        <label>Email</label><input type="email" value={f.email} onChange={set("email")} />
        <label>Password</label><input type="password" value={f.password} onChange={set("password")} />
        {err && <p className="err">{err}</p>}
        <button onClick={submit}>{mode === "login" ? "Log in" : "Create account"}</button>{" "}
        <button className="ghost" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "New here? Register" : "Have an account? Log in"}
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("token"));
  return authed
    ? <Dashboard onLogout={() => { localStorage.removeItem("token"); setAuthed(false); }} />
    : <Auth onAuth={() => setAuthed(true)} />;
}
