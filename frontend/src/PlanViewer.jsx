import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'
const ACCENT = '#7C8B4A'

function PlanViewer({ token }) {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPlan, setSelectedPlan] = useState(null)

  const loadPlans = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/plans`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setPlans(data)
      }
    } catch (err) {
      console.error('Failed to load plans:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPlans()
  }, [])

  const handleDelete = async (id) => {
    const confirmed = window.confirm('Delete this plan? This cannot be undone.')
    if (!confirmed) return
    try {
      const response = await fetch(`${API_URL}/plans/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        setPlans((prev) => prev.filter((p) => p.id !== id))
        setSelectedPlan(null)
      }
    } catch (err) {
      console.error('Failed to delete plan:', err)
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <h2 className="font-[Oswald] uppercase tracking-wide text-lg mb-1" style={{ color: ACCENT }}>
        Saved Plans
      </h2>
      <p className="text-(--color-chalk-dim) text-sm mb-5">
        Workout and meal plans you've saved from your coaches.
      </p>

      {loading && (
        <p className="text-(--color-chalk-dim) text-sm">Loading plans...</p>
      )}

      {!loading && plans.length === 0 && (
        <p className="text-(--color-chalk-dim) text-sm">
          No saved plans yet — ask a coach for a plan and save it from the chat.
        </p>
      )}

      {!loading && plans.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {plans.map((plan) => (
            <button
              key={plan.id}
              onClick={() => setSelectedPlan(plan)}
              className="text-left bg-(--color-bg-elevated) rounded-md border border-white/10 hover:border-white/30 transition-all p-4"
            >
              <div className="text-sm font-medium">{plan.title}</div>
              <div className="text-xs text-(--color-chalk-dim) mt-1 capitalize">
                {plan.coach_type}
              </div>
              <div className="text-xs text-(--color-chalk-dim) mt-0.5">
                {new Date(plan.created_at).toLocaleDateString()}
              </div>
            </button>
          ))}
        </div>
      )}

      {selectedPlan && (
        <div
          className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedPlan(null)}
        >
          <div
            className="bg-(--color-bg) rounded-md border border-white/10 w-full max-w-lg max-h-[80vh] overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-1">
              <div>
                <div className="text-base font-medium">{selectedPlan.title}</div>
                <div className="text-xs text-(--color-chalk-dim) mt-0.5 capitalize">
                  {selectedPlan.coach_type} · {new Date(selectedPlan.created_at).toLocaleDateString()}
                </div>
              </div>
              <button
                onClick={() => setSelectedPlan(null)}
                className="text-(--color-chalk-dim) hover:text-(--color-chalk) text-lg leading-none"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="mt-4">
              {selectedPlan.plan_data && selectedPlan.plan_data.days ? (
                <div className="flex flex-col gap-3">
                  {selectedPlan.plan_data.days.map((day, i) => (
                    <div key={i}>
                      <div className="text-xs uppercase tracking-wide mb-1.5" style={{ color: ACCENT }}>
                        {day.label}
                      </div>
                      <ul className="flex flex-col gap-1">
                        {day.items.map((item, j) => (
                          <li key={j} className="text-sm text-(--color-chalk-dim) pl-3 border-l border-white/10">
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-(--color-chalk-dim) whitespace-pre-wrap">
                  {selectedPlan.raw_text}
                </p>
              )}
            </div>

            <button
              onClick={() => handleDelete(selectedPlan.id)}
              className="mt-5 text-xs uppercase tracking-wide text-(--color-chalk-dim) hover:text-red-400 transition-colors"
            >
              Delete Plan
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default PlanViewer