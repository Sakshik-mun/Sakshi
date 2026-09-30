import axios from "axios";
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000" });
api.interceptors.request.use((c) => {
  const t = localStorage.getItem("token");
  if (t) c.headers.Authorization = `Bearer ${t}`;
  return c;
});
export const errMsg = (e) => {
  const d = e.response?.data?.detail;
  return Array.isArray(d) ? d.map((x) => x.msg).join(", ") : d || "Something went wrong";
};
export default api;
