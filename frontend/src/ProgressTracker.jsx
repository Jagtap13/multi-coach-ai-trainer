import { useState, useEffect, useRef } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts'

const API_URL = 'http://127.0.0.1:8000'
const ACCENT = '#4A7A9D'

function ProgressTracker({ token }) {
  const chartContainerRef = useRef(null)
  const [chartWidth, setChartWidth] = useState(0)
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [weight, setWeight] = useState('')
  const [entryDate, setEntryDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [notes, setNotes] = useState('')
  const [waist, setWaist] = useState('')
  const [chest, setChest] = useState('')
  const [arms, setArms] = useState('')
  const [showMeasurements, setShowMeasurements] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [goalWeight, setGoalWeight] = useState('')
  const [goalInput, setGoalInput] = useState('')
  const [savingGoal, setSavingGoal] = useState(false)


    const loadEntries = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/progress`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setEntries(data)
      }
    } catch (err) {
      console.error('Failed to load progress entries:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadGoal = async () => {
    try {
      const response = await fetch(`${API_URL}/progress/goal`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setGoalWeight(data.goal_weight_kg)
        setGoalInput(data.goal_weight_kg || '')
      }
    } catch (err) {
      console.error('Failed to load goal weight:', err)
    }
  }
  
    useEffect(() => {
    loadEntries()
    loadGoal()
  }, [])

  const handleSaveGoal = async () => {
    setSavingGoal(true)
    try {
      const response = await fetch(`${API_URL}/progress/goal`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ goal_weight_kg: goalInput ? parseFloat(goalInput) : null }),
      })
      if (response.ok) {
        const data = await response.json()
        setGoalWeight(data.goal_weight_kg)
      }
    } catch (err) {
      console.error('Failed to save goal weight:', err)
    } finally {
      setSavingGoal(false)
    }
  }

  useEffect(() => {
    const updateWidth = () => {
      if (chartContainerRef.current) {
        setChartWidth(chartContainerRef.current.clientWidth)
      }
    }
    updateWidth()
    window.addEventListener('resize', updateWidth)
    return () => window.removeEventListener('resize', updateWidth)
  }, [entries])

    const handleAddEntry = async () => {
    if (!weight || !entryDate) return
    setSubmitting(true)
    try {
      const response = await fetch(`${API_URL}/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          weight_kg: parseFloat(weight),
          entry_date: entryDate,
          notes: notes || null,
          waist_cm: waist ? parseFloat(waist) : null,
          chest_cm: chest ? parseFloat(chest) : null,
          arms_cm: arms ? parseFloat(arms) : null,
        }),
      })
      if (response.ok) {
        setWeight('')
        setNotes('')
        setWaist('')
        setChest('')
        setArms('')
        await loadEntries()
      }
    } catch (err) {
      console.error('Failed to add progress entry:', err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      const response = await fetch(`${API_URL}/progress/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        setEntries((prev) => prev.filter((e) => e.id !== id))
      }
    } catch (err) {
      console.error('Failed to delete progress entry:', err)
    }
  }

  const chartData = entries.map((e) => ({
    date: e.entry_date,
    weight: e.weight_kg,
  }))

  return (
    <div className="flex flex-col h-full overflow-y-auto p-6 gap-6">
      <div>
        <h2 className="font-[Oswald] uppercase tracking-wide text-lg mb-1" style={{ color: ACCENT }}>
          Progress Tracker
        </h2>
        <p className="text-(--color-chalk-dim) text-sm">
          Log your weight over time and watch your trend.
        </p>
      </div>

            <div className="flex flex-wrap gap-3 items-end bg-(--color-bg-elevated) p-4 rounded-md border border-white/10 mb-1">
        <div>
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Goal Weight (kg)</label>
          <input
            type="number"
            step="0.1"
            value={goalInput}
            onChange={(e) => setGoalInput(e.target.value)}
            placeholder="optional"
            className="bg-black/20 rounded-md px-3 py-2 text-sm outline-none w-32"
          />
        </div>
        <button
          onClick={handleSaveGoal}
          disabled={savingGoal}
          className="px-4 py-2 rounded-md text-xs uppercase tracking-wide border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all disabled:opacity-40"
        >
          {savingGoal ? 'Saving...' : 'Set Goal'}
        </button>
      </div>

      <div className="flex flex-wrap gap-3 items-end bg-(--color-bg-elevated) p-4 rounded-md border border-white/10">
        <div>
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Weight (kg)</label>
          <input
            type="number"
            step="0.1"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            className="bg-black/20 rounded-md px-3 py-2 text-sm outline-none w-28"
          />
        </div>
        <div>
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Date</label>
          <input
            type="date"
            value={entryDate}
            onChange={(e) => setEntryDate(e.target.value)}
            className="bg-black/20 rounded-md px-3 py-2 text-sm outline-none"
          />
        </div>
        <div className="flex-1 min-w-[150px]">
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Notes (optional)</label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="e.g. after a cut"
            className="bg-black/20 rounded-md px-3 py-2 text-sm outline-none w-full"
          />
        </div>
                <button
          onClick={() => setShowMeasurements(!showMeasurements)}
          className="text-xs uppercase tracking-wide text-(--color-chalk-dim) hover:text-(--color-chalk) transition-colors px-2 py-2"
        >
          {showMeasurements ? '− Measurements' : '+ Measurements'}
        </button>
        <button
          onClick={handleAddEntry}
          disabled={submitting || !weight || !entryDate}
          className="px-5 py-2 rounded-md text-sm font-medium uppercase tracking-wide disabled:opacity-40 transition-opacity"
          style={{ backgroundColor: ACCENT, color: '#1C1D1F' }}
        >
          Add
        </button>
      </div>

      {showMeasurements && (
        <div className="flex flex-wrap gap-3 items-end bg-(--color-bg-elevated) p-4 rounded-md border border-white/10 -mt-3">
          <div>
            <label className="text-xs text-(--color-chalk-dim) block mb-1">Waist (cm)</label>
            <input
              type="number"
              step="0.1"
              value={waist}
              onChange={(e) => setWaist(e.target.value)}
              className="bg-black/20 rounded-md px-3 py-2 text-sm outline-none w-24"
            />
          </div>
          <div>
            <label className="text-xs text-(--color-chalk-dim) block mb-1">Chest (cm)</label>
            <input
              type="number"
              step="0.1"
              value={chest}
              onChange={(e) => setChest(e.target.value)}
              className="bg-black/20 rounded-md px-3 py-2 text-sm outline-none w-24"
            />
          </div>
          <div>
            <label className="text-xs text-(--color-chalk-dim) block mb-1">Arms (cm)</label>
            <input
              type="number"
              step="0.1"
              value={arms}
              onChange={(e) => setArms(e.target.value)}
              className="bg-black/20 rounded-md px-3 py-2 text-sm outline-none w-24"
            />
          </div>
        </div>
      )}

      {loading && (
        <p className="text-(--color-chalk-dim) text-sm">Loading progress...</p>
      )}

      {!loading && entries.length === 0 && (
        <p className="text-(--color-chalk-dim) text-sm">
          No entries yet — log your first weigh-in above to start tracking your trend.
        </p>
      )}

      {!loading && entries.length > 0 && (
        <>
          <div ref={chartContainerRef} className="bg-(--color-bg-elevated) rounded-md border border-white/10 p-4 h-64">
            {chartWidth > 0 && (
                <LineChart width={chartWidth - 32} height={224} data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="date" tick={{ fill: '#8A8781', fontSize: 11 }} />
                <YAxis tick={{ fill: '#8A8781', fontSize: 11 }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1C1D1F', border: '1px solid rgba(255,255,255,0.1)' }}
                  labelStyle={{ color: '#EDEAE3' }}
                />
                {goalWeight && (
                  <ReferenceLine y={goalWeight} stroke="#D9A441" strokeDasharray="4 4" label={{ value: 'Goal', fill: '#D9A441', fontSize: 11, position: 'right' }} />
                )}
                <Line type="monotone" dataKey="weight" stroke={ACCENT} strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            )}
          </div>

          <div className="flex flex-col gap-2">
            {entries.slice().reverse().map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between bg-(--color-bg-elevated) px-4 py-2.5 rounded-md border border-white/10 text-sm"
              >
                                <div>
                  <span className="font-medium">{entry.weight_kg} kg</span>
                  <span className="text-(--color-chalk-dim) ml-3">{entry.entry_date}</span>
                  {(entry.waist_cm || entry.chest_cm || entry.arms_cm) && (
                    <span className="text-(--color-chalk-dim) ml-3">
                      {[
                        entry.waist_cm && `Waist ${entry.waist_cm}cm`,
                        entry.chest_cm && `Chest ${entry.chest_cm}cm`,
                        entry.arms_cm && `Arms ${entry.arms_cm}cm`,
                      ].filter(Boolean).join(' · ')}
                    </span>
                  )}
                  {entry.notes && (
                    <span className="text-(--color-chalk-dim) ml-3 italic">{entry.notes}</span>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(entry.id)}
                  className="text-(--color-chalk-dim) hover:text-red-400 transition-colors text-xs uppercase tracking-wide"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default ProgressTracker