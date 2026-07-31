import { useState } from 'react'
import ChatWindow from './ChatWindow'
import ProfileForm from './ProfileForm'
import AuthForm from './AuthForm'

const COACHES = [
  { id: 'bodybuilding', label: 'Bodybuilding', accent: 'var(--accent-bodybuilding)', tagline: 'Muscle & mass' },
  { id: 'powerlifting', label: 'Powerlifting', accent: 'var(--accent-powerlifting)', tagline: 'Strength & power' },
  { id: 'nutrition', label: 'Nutrition', accent: 'var(--accent-nutrition)', tagline: 'Diet & macros' },
  { id: 'fatloss', label: 'Fat Loss', accent: 'var(--accent-fatloss)', tagline: 'Cutting & cardio' },
]

function App() {
  const [token , setToken] = useState(() => localStorage.getItem('token')) 
  const [selectedCoach, setSelectedCoach] = useState('bodybuilding')
  const [profile, setProfile] = useState({
    age: '',
    weight_kg: '',
    experience_level: '',
    goal: '',
  })

  const activeCoach = COACHES.find((c) => c.id === selectedCoach)

  const handleAuthSuccess = (newToken) => {
    localStorage.setItem('token',newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  if(!token){
    return <AuthForm onAuthSuccess={handleAuthSuccess} />
  }  
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-white/10 px-8 py-6 flex items-center justify-between">
        <div>
          <h1 className="font-[Oswald] uppercase tracking-wide text-3xl font-semibold">
            AI Personal Trainer <span style={{ color: activeCoach.accent }}>Simulator</span>
          </h1>
          <p className="text-(--color-chalk-dim) text-sm mt-1">
            Pick your coach, ask your question.
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="text-xs uppercase tracking-wide px-4 py-2 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all shrink-0"
        >
          Log out
        </button>
      </header>

      <div className="flex flex-1 max-w-5xl mx-auto w-full px-8 py-8 gap-8">
        <aside className="w-64 shrink-0">
          <h2 className="text-xs uppercase tracking-widest text-(--color-chalk-dim) mb-3">
            Select Coach
          </h2>
          <div className="flex flex-col gap-2">
            {COACHES.map((coach) => (
              <button
                key={coach.id}
                onClick={() => setSelectedCoach(coach.id)}
                className={`text-left px-4 py-3 rounded-md border transition-all ${
                  selectedCoach === coach.id
                    ? 'border-white/30 bg-white/5'
                    : 'border-white/10 hover:border-white/20'
                }`}
                style={{
                  borderLeftWidth: '4px',
                  borderLeftColor: coach.accent,
                }}
              >
                <div className="font-[Oswald] uppercase text-sm tracking-wide">
                  {coach.label}
                </div>
                <div className="text-xs text-(--color-chalk-dim) mt-0.5">
                  {coach.tagline}
                </div>
              </button>
            ))}
          </div>

          <ProfileForm profile={profile} setProfile={setProfile} />
        </aside>

        <main className="flex-1 border border-white/10 rounded-md overflow-hidden">
          <ChatWindow coach={activeCoach} profile={profile} token={token} />
        </main>
      </div>
    </div>
  )
}

export default App