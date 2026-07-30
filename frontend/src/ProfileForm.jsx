function ProfileForm({ profile, setProfile }) {
  const handleChange = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }))
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
      </div>
    </div>
  )
}

export default ProfileForm