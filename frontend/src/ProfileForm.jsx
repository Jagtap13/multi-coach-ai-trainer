import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function ProfileForm({ profile, setProfile, token }) {
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState('')

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await fetch(`${API_URL}/profile`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (response.ok) {
          const data = await response.json()
          setProfile({
            age: data.age ?? '',
            weight_kg: data.weight_kg ?? '',
            experience_level: data.experience_level ?? '',
            goal: data.goal ?? '',
          })
        }
      } catch (err) {
        console.error('Failed to load profile:', err)
      }
    }

    if (token) loadProfile()
  }, [token])

  const handleChange = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    setSaving(true)
    setSaveStatus('')
    try {
      const response = await fetch(`${API_URL}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          age: profile.age ? parseInt(profile.age) : null,
          weight_kg: profile.weight_kg ? parseFloat(profile.weight_kg) : null,
          experience_level: profile.experience_level || null,
          goal: profile.goal || null,
        }),
      })

      if (response.ok) {
        setSaveStatus('Saved!')
        setTimeout(() => setSaveStatus(''), 2000)
      } else {
        setSaveStatus('Failed to save')
      }
    } catch (err) {
      setSaveStatus('Failed to save')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mt-6 pt-6 border-t border-white/10">
      <h2 className="text-xs uppercase tracking-widest text-(--color-chalk-dim) mb-3">
        Your Profile
      </h2>

      <div className="flex flex-col gap-3">
        <div>
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Age</label>
          <input
            type="number"
            value={profile.age}
            onChange={(e) => handleChange('age', e.target.value)}
            placeholder="e.g. 22"
            className="w-full bg-(--color-bg-elevated) rounded-md px-3 py-2 text-sm outline-none placeholder:text-(--color-chalk-dim)"
          />
        </div>

        <div>
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Weight (kg)</label>
          <input
            type="number"
            value={profile.weight_kg}
            onChange={(e) => handleChange('weight_kg', e.target.value)}
            placeholder="e.g. 65"
            className="w-full bg-(--color-bg-elevated) rounded-md px-3 py-2 text-sm outline-none placeholder:text-(--color-chalk-dim)"
          />
        </div>

        <div>
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Experience Level</label>
          <select
            value={profile.experience_level}
            onChange={(e) => handleChange('experience_level', e.target.value)}
            className="w-full bg-(--color-bg-elevated) rounded-md px-3 py-2 text-sm outline-none"
          >
            <option value="">Select...</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div>
          <label className="text-xs text-(--color-chalk-dim) block mb-1">Goal</label>
          <input
            type="text"
            value={profile.goal}
            onChange={(e) => handleChange('goal', e.target.value)}
            placeholder="e.g. build muscle"
            className="w-full bg-(--color-bg-elevated) rounded-md px-3 py-2 text-sm outline-none placeholder:text-(--color-chalk-dim)"
          />
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="mt-1 text-xs uppercase tracking-wide px-3 py-2 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all disabled:opacity-50"
        >
          {saving ? 'Saving...' : saveStatus || 'Save Profile'}
        </button>
      </div>
    </div>
  )
}

export default ProfileForm