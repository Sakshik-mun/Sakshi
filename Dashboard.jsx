import { useCallback, useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import api, { errMsg } from "./api";
import ProfileForm from "./ProfileForm.jsx";

export default function Dashboard({ onLogout }) {
  const [p, setP] = useState(null);
  const [hist, setHist] = useState([]);
  const [delta, setDelta] = useState(null);
  const [advice, setAdvice] = useState(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const load = useCallback(async () => {
    try {
      const [a, h] = await Promise.all([api.get("/profile"), api.get("/history")]);
      setP(a.data); setHist(h.data);
    } catch (e) {
      if (e.response?.status === 401) onLogout();
      else if (e.response?.status !== 404) setErr(errMsg(e));
    } finally { setLoading(false); }
  }, [onLogout]);

  useEffect(() => { load(); }, [load]);

  const saved = async (data) => {
    setDelta(data.delta ?? null); setAdvice(null); setEditing(false);
    await load();
  };

  const getAdvice = async () => {
    setBusy(true); setErr("");
    try { setAdvice((await api.post("/advice")).data); }
    catch (e) { setErr(errMsg(e)); }
    finally { setBusy(false); }
  };

  if (loading) return <div className="wrap">Loading...</div>;
  if (!p) return <div className="wrap"><ProfileForm onSaved={saved} /></div>;

  const pie = [
    { name: "Used", value: p.credit_used, color: p.utilization > 30 ? "#b3372b" : "#1f7a4d" },
    { name: "Available", value: p.available_credit, color: "#d9e2dd" },
  ];

  return (
    <div className="wrap">
      <header>
        <h2>Hello, {p.name}</h2>
        <div>
          <button className="ghost" onClick={() => setEditing(true)}>Update data</button>{" "}
          <button className="ghost" onClick={onLogout}>Log out</button>
        </div>
      </header>

      {editing && <div style={{ marginBottom: 16 }}><ProfileForm existing={p} onSaved={saved} onCancel={() => setEditing(false)} /></div>}
      {err && <p className="err">{err}</p>}

      <div className="grid">
        <div className="card">
          <div className="score">{p.credit_score}<span className={`badge ${p.band}`}>{p.band}</span></div>
          {delta !== null && delta !== 0 && (
            <p className={delta > 0 ? "up" : "down"}>
              {delta > 0 ? "+" : ""}{delta} points since last update
            </p>
          )}
          <p className="note">Debt-to-income: {p.dti}% | Utilization: {p.utilization}%</p>
          <div>
            {p.bottlenecks.length
              ? p.bottlenecks.map((b) => <span className="chip" key={b}>{b}</span>)
              : <span className="up">No bottlenecks found.</span>}
          </div>
        </div>

        <div className="card">
          <h3>Credit utilization</h3>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={pie} dataKey="value" innerRadius={45} outerRadius={75}>
                {pie.map((s) => <Cell key={s.name} fill={s.color} />)}
              </Pie>
              <Tooltip formatter={(v) => `₹${Number(v).toLocaleString("en-IN")}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card full">
          <h3>Score history</h3>
          {hist.length < 2 && <p className="note">Update your data over time to see your trend.</p>}
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={hist}>
              <CartesianGrid stroke="#d9e2dd" strokeDasharray="3 3" />
              <XAxis dataKey="date" /><YAxis domain={[300, 900]} /><Tooltip />
              <Line type="monotone" dataKey="score" stroke="#1f7a4d" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card full">
          <h3>AI credit advisor</h3>
          <button onClick={getAdvice} disabled={busy}>{busy ? "Analysing..." : "Get AI advice"}</button>
          {advice && (
            <div>
              <p>{advice.analysis}</p>
              <ol>{advice.steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
            </div>
          )}
          <p className="note">AI-generated guidance, not financial advice.</p>
        </div>
      </div>
    </div>
  );
}
