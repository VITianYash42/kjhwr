import { useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, BarChart, Bar
} from "recharts";

const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default function App() {
  const [start, setStart] = useState("2026-01-01");
  const [end, setEnd] = useState("2026-01-07");
  const [horizon, setHorizon] = useState(24);
  const [rows, setRows] = useState([]);
  const [stats, setStats] = useState(null);
  const [hor, setHor] = useState([]);
  const [loading, setLoading] = useState(false);

  function load() {
    setLoading(true);
    const s = start + "T00:00:00Z";
    const e = end + "T23:59:59Z";
    fetch(`${API}/api/data?start=${s}&end=${e}&horizon=${horizon}`)
      .then((r) => r.json())
      .then((d) => {
        setRows(d.rows.map((r) => ({ ...r, label: r.time.slice(5, 16).replace("T", " ") })));
        setStats(d.stats);
        setLoading(false);
      });
    fetch(`${API}/api/horizons?start=${s}&end=${e}`)
      .then((r) => r.json())
      .then(setHor);
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h2>UK Wind Generation: Actual vs Forecast</h2>

      <div style={{ marginBottom: 15 }}>
        Start <input type="date" value={start} min="2026-01-01" max="2026-01-31" onChange={(e) => setStart(e.target.value)} />
        {" "}End <input type="date" value={end} min="2026-01-01" max="2026-01-31" onChange={(e) => setEnd(e.target.value)} />
        {" "}Horizon: {horizon}h{" "}
        <input type="range" min="0" max="48" value={horizon} onChange={(e) => setHorizon(e.target.value)} />
        {" "}<button onClick={load}>Apply</button>
      </div>

      {loading && <p>Loading...</p>}

      {stats && (
        <p>
          MAE: {stats.mae.toFixed(0)} MW | RMSE: {stats.rmse.toFixed(0)} MW | Bias: {stats.bias.toFixed(0)} MW | Points: {stats.count}
        </p>
      )}

      <LineChart width={1000} height={350} data={rows}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" minTickGap={40} />
        <YAxis unit=" MW" />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="actual" stroke="#1f77b4" dot={false} />
        <Line type="monotone" dataKey="forecast" stroke="#ff7f0e" dot={false} connectNulls />
      </LineChart>

      <h3>Error by forecast horizon</h3>
      <BarChart width={1000} height={250} data={hor}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="horizon" unit="h" />
        <YAxis unit=" MW" />
        <Tooltip />
        <Legend />
        <Bar dataKey="mae" fill="#8884d8" />
        <Bar dataKey="rmse" fill="#82ca9d" />
      </BarChart>
    </div>
  );
}
