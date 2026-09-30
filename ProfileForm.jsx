import { useState } from "react";
import api, { errMsg } from "./api";

const FIELDS = [
  ["credit_score", "Credit score (300-900)"], ["monthly_income", "Monthly income (₹)"],
  ["monthly_expenses", "Monthly expenses (₹)"], ["total_emi", "Total monthly EMIs (₹)"],
  ["credit_limit", "Total credit limit (₹)"], ["credit_used", "Credit used (₹)"],
];

export default function ProfileForm({ existing, onSaved, onCancel }) {
  const [v, setV] = useState(Object.fromEntries(FIELDS.map(([k]) => [k, existing?.[k] ?? ""])));
  const [err, setErr] = useState("");

  const save = async () => {
    setErr("");
    const body = Object.fromEntries(Object.entries(v).map(([k, x]) => [k, Number(x)]));
    try {
      const r = existing ? await api.put("/profile", body) : await api.post("/profile", body);
      onSaved(r.data);
    } catch (e) { setErr(errMsg(e)); }
  };

  return (
    <div className="card">
      <h3>{existing ? "Update your finances" : "Set up your profile"}</h3>
      {FIELDS.map(([k, l]) => (
        <div key={k}><label>{l}</label>
          <input type="number" value={v[k]} onChange={(e) => setV({ ...v, [k]: e.target.value })} /></div>
      ))}
      {err && <p className="err">{err}</p>}
      <button onClick={save}>Save</button>{" "}
      {onCancel && <button className="ghost" onClick={onCancel}>Cancel</button>}
    </div>
  );
}
