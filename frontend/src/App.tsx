import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

type Daily = { day: string; endpoint: string; failures: number }
type Anomaly = {
  endpoint: string
  recent: number
  baseline: number
  common: [string, string, number, number][]
}
type Failure = { user_id: string; step_id: string; payload: Record<string, unknown>; occurred_at: string }

const COLORS = ['#2563eb', '#16a34a', '#dc2626', '#9333ea']
const short = (e: string) => e.replace(/^https?:\/\/[^/]+/, '')

async function getJSON<T>(url: string): Promise<T> {
  const r = await fetch(url)
  if (!r.ok) throw new Error(`${url} returned ${r.status}`)
  return r.json()
}

export default function App() {
  const [daily, setDaily] = useState<Daily[]>([])
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [failures, setFailures] = useState<Failure[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      getJSON<Daily[]>('/api/stats/daily?days=7'),
      getJSON<Anomaly[]>('/api/anomalies'),
    ])
      .then(([d, a]) => {
        setDaily(d)
        setAnomalies(a)
      })
      .catch((e) => setError(String(e)))
  }, [])

  useEffect(() => {
    if (!selected) return
    getJSON<Failure[]>(`/api/failures?endpoint=${encodeURIComponent(selected)}&hours=24`)
      .then(setFailures)
      .catch((e) => setError(String(e)))
  }, [selected])

  const endpoints = [...new Set(daily.map((d) => d.endpoint))]
  const chartData = Object.values(
    daily.reduce<Record<string, Record<string, string | number>>>((acc, d) => {
      acc[d.day] ??= { day: d.day }
      acc[d.day][d.endpoint] = d.failures
      return acc
    }, {}),
  )

  return (
    <main>
      <h1>Connected Content failures</h1>
      {error && <p className="banner">Error: {error}</p>}

      {anomalies.map((a) => (
        <div className="banner" key={a.endpoint}>
          <strong>Spike on {short(a.endpoint)}</strong>: {a.recent} failures in the last hour
          (normal {a.baseline.toFixed(1)}/hour)
          <ul>
            {a.common.map(([k, v, share, base]) => (
              <li key={k + v}>
                {Math.round(share * 100)}% have {k} = {v} (normally {Math.round(base * 100)}%)
              </li>
            ))}
          </ul>
          <button onClick={() => setSelected(a.endpoint)}>View failures</button>
        </div>
      ))}

      <div className="card">
        <h2>Failures per day</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            {endpoints.map((e, i) => (
              <Bar key={e} dataKey={e} name={short(e)} stackId="a" fill={COLORS[i % COLORS.length]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2>Affected users</h2>
        {endpoints.map((e) => (
          <button key={e} onClick={() => setSelected(e)}>{short(e)}</button>
        ))}
        {selected && (
          <>
            <h3>{short(selected)}: last 24 hours</h3>
            <table>
              <thead>
                <tr><th>Time</th><th>User</th><th>Step</th><th>Data</th></tr>
              </thead>
              <tbody>
                {failures.map((f, i) => (
                  <tr key={i}>
                    <td>{new Date(f.occurred_at).toLocaleString()}</td>
                    <td>{f.user_id}</td>
                    <td>{f.step_id}</td>
                    <td>{JSON.stringify(f.payload)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </div>
    </main>
  )
}