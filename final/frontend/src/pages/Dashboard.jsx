import { useEffect, useMemo, useState } from 'react'
import Layout from '../components/Layout'
import StatCard from '../components/StatCard'
import api from '../api/client'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WS_BASE = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://')

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get('/dashboard/summary')
      setSummary(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/api/v1/ws/dashboard`)
    ws.onopen = () => ws.send('ping')
    ws.onmessage = (msg) => {
      const ev = JSON.parse(msg.data)
      setEvents((prev) => [ev, ...prev].slice(0, 20))
      load()
    }
    const i = setInterval(() => ws.readyState === 1 && ws.send('ping'), 20000)
    return () => { clearInterval(i); ws.close() }
  }, [])

  const gaps = useMemo(() => summary?.top_gaps || [], [summary])

  const downloadExcel = async () => {
    try {
      const res = await api.get('/exports/assessments.xlsx', {
        responseType: 'blob',
      })

      const blob = new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'skills_policy_report.xlsx'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error(err)
      alert('Export failed. Make sure you are logged in as admin.')
    }
  }

  if (!summary && loading)
    return <Layout><div>Loading dashboard…</div></Layout>

  return (
    <Layout>

      {/* KPI SECTION */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Assessments" value={summary?.total_assessments ?? 0} />
        <StatCard title="Avg Overall" value={Number(summary?.avg_overall ?? 0).toFixed(2)} hint="Out of 5" />
        <StatCard title="Avg Soft Skills" value={Number(summary?.avg_soft ?? 0).toFixed(2)} hint="Out of 5" />
        <StatCard title="Avg Digital Skills" value={Number(summary?.avg_digital ?? 0).toFixed(2)} hint="Out of 5" />
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* CHART CARD */}
        <div className="card p-6 lg:col-span-2">

          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-[#101828]">
              Lowest Scoring Skill Areas
            </h3>
            <span className="text-xs text-[#98A2B3]">
              {gaps.length ? `Showing ${gaps.length}` : 'No data'}
            </span>
          </div>

          <div style={{ width: '100%', height: 340 }}>
            {gaps.length === 0 ? (
              <div className="h-full flex items-center justify-center text-sm text-[#667085]">
                No results yet — complete at least 1 assessment.
              </div>
            ) : (
              <ResponsiveContainer>
                <BarChart
                  data={gaps}
                  layout="vertical"
                  margin={{ top: 8, right: 24, left: 8, bottom: 8 }}
                  barCategoryGap={12}
                >

                  {/* Minimal Grid */}
                  <CartesianGrid
                    stroke="#E7EAEE"
                    horizontal={false}
                    vertical={true}
                  />

                  <XAxis
                    type="number"
                    domain={[0, 5]}
                    tick={{ fill: '#667085', fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <YAxis
                    type="category"
                    dataKey="skill_area"
                    width={200}
                    tick={{ fill: '#101828', fontSize: 13 }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <Tooltip
                    cursor={{ fill: 'rgba(14,107,70,0.06)' }}
                    contentStyle={{
                      background: '#FFFFFF',
                      border: '1px solid #E7EAEE',
                      borderRadius: 12,
                      boxShadow: '0 10px 30px rgba(16,24,40,0.08)',
                      fontSize: 13,
                    }}
                    formatter={(value) => [
                      `${Number(value).toFixed(2)} / 5`,
                      'Average Score'
                    ]}
                  />

                  <Bar
                    dataKey="avg_score"
                    fill="#0E6B46"
                    radius={[8, 8, 8, 8]}
                    animationDuration={600}
                  />

                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="text-xs text-[#98A2B3] mt-3">
            Lower average score indicates a larger skill gap.
          </div>
        </div>

        {/* LIVE ACTIVITY */}
        <div className="card p-6">
          <h3 className="text-base font-semibold text-[#101828] mb-4">
            Live Activity
          </h3>

          <div className="space-y-3 max-h-80 overflow-auto">
            {events.length === 0 && (
              <div className="text-sm text-[#667085]">
                No recent events.
              </div>
            )}

            {events.map((e, idx) => (
              <div
                key={idx}
                className="p-4 rounded-[16px] border border-[#E7EAEE] bg-white text-sm transition-all duration-200"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="font-medium text-[#101828]">{e.type}</div>
                  <div className="text-xs text-[#98A2B3]">
                    {e.created_at
                      ? new Date(e.created_at).toLocaleString()
                      : ''}
                  </div>
                </div>

                <div className="text-[#667085]">
                  Assessment #{e.payload?.assessment_id ?? '—'}
                  {typeof e.payload?.overall_score !== 'undefined'
                    ? ` · Score ${Number(e.payload.overall_score).toFixed(2)}`
                    : ''}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* EXPORT */}
      <div className="mt-8">
        <button
          onClick={downloadExcel}
          className="btn-primary"
        >
          Export Report
        </button>
      </div>

    </Layout>
  )
}