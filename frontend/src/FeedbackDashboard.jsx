import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'
const ACCENT = '#D9A441'

const REASON_LABELS = {
  inaccurate: 'Inaccurate',
  unsafe: 'Unsafe advice',
  off_topic: 'Off-topic',
  too_generic: 'Too generic',
}

function FeedbackDashboard({ token }) {
  const [summary, setSummary] = useState({})
  const [downvoted, setDownvoted] = useState([])
  const [loading, setLoading] = useState(true)
  const [forbidden, setForbidden] = useState(false)
  const [expandedId, setExpandedId] = useState(null)

  const loadData = async () => {
    setLoading(true)
    try {
      const [summaryRes, downvotedRes] = await Promise.all([
        fetch(`${API_URL}/feedback/summary`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_URL}/feedback/downvoted`, { headers: { Authorization: `Bearer ${token}` } }),
      ])
      if (summaryRes.status === 403 || downvotedRes.status === 403) {
        setForbidden(true)
        return
      }
      if (summaryRes.ok) setSummary(await summaryRes.json())
      if (downvotedRes.ok) setDownvoted(await downvotedRes.json())
    } catch (err) {
      console.error('Failed to load feedback data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const coachTypes = Object.keys(summary)

  return (
    <div className="h-full overflow-y-auto p-6">
      <h2 className="font-[Oswald] uppercase tracking-wide text-lg mb-1" style={{ color: ACCENT }}>
        Feedback
      </h2>
      <p className="text-(--color-chalk-dim) text-sm mb-5">
        How your coaches are performing, based on your ratings.
      </p>

      {loading && (
        <p className="text-(--color-chalk-dim) text-sm">Loading feedback...</p>
      )}

      {!loading && forbidden && (
        <p className="text-(--color-chalk-dim) text-sm">
          This section is restricted to admin accounts.
        </p>
      )}

      {!loading && !forbidden && coachTypes.length === 0 && (
        <p className="text-(--color-chalk-dim) text-sm">
          No feedback yet — rate a coach's response with 👍 or 👎 to see it here.
        </p>
      )}

      {!loading && !forbidden && coachTypes.length > 0 && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            {coachTypes.map((coach) => (
              <div
                key={coach}
                className="bg-(--color-bg-elevated) rounded-md border border-white/10 p-4"
              >
                <div className="text-sm font-medium capitalize mb-2">{coach}</div>
                <div className="flex gap-3 text-sm">
                  <span className="text-green-400">👍 {summary[coach].up}</span>
                  <span className="text-red-400">👎 {summary[coach].down}</span>
                </div>
              </div>
            ))}
          </div>

          <h3 className="text-xs uppercase tracking-widest text-(--color-chalk-dim) mb-3">
            Downvoted Responses
          </h3>

          {downvoted.length === 0 && (
            <p className="text-(--color-chalk-dim) text-sm">No downvoted responses yet.</p>
          )}

          <div className="flex flex-col gap-2">
            {downvoted.map((item) => (
              <div
                key={item.id}
                className="bg-(--color-bg-elevated) rounded-md border border-white/10 overflow-hidden"
              >
                <button
                  onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
                  className="w-full flex items-center justify-between px-4 py-3 text-left"
                >
                  <div>
                    <div className="text-sm">{item.question}</div>
                    <div className="text-xs text-(--color-chalk-dim) mt-0.5 capitalize">
                      {item.coach_type} · {new Date(item.created_at).toLocaleDateString()}
                      {item.reason && ` · ${REASON_LABELS[item.reason] || item.reason}`}
                    </div>
                  </div>
                  <span className="text-(--color-chalk-dim) text-xs">
                    {expandedId === item.id ? '▲' : '▼'}
                  </span>
                </button>
                {expandedId === item.id && (
                  <div className="px-4 pb-4 border-t border-white/10 pt-3">
                    <p className="text-sm text-(--color-chalk-dim) whitespace-pre-wrap">
                      {item.answer}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default FeedbackDashboard