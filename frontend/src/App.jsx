import { useState } from "react";
import ChatWindow from "./ChatWindow";
import ProfileForm from "./ProfileForm";
import AuthForm from "./AuthForm";
import ProgressTracker from "./ProgressTracker";
import PlanViewer from "./PlanViewer";

const COACHES = [
  {
    id: "bodybuilding",
    label: "Bodybuilding",
    accent: "var(--accent-bodybuilding)",
    tagline: "Muscle & mass",
    starterQuestions: [
      "What rep range is best for building muscle?",
      "Design a 4-day workout split for a beginner",
      "How much training volume do I need per week?",
    ],
  },
  {
    id: "powerlifting",
    label: "Powerlifting",
    accent: "var(--accent-powerlifting)",
    tagline: "Strength & power",
    starterQuestions: [
      "How do I increase my squat strength?",
      "What percentage of my 1RM should I train at?",
      "How long should I rest between heavy sets?",
    ],
  },
  {
    id: "nutrition",
    label: "Nutrition",
    accent: "var(--accent-nutrition)",
    tagline: "Diet & macros",
    starterQuestions: [
      "How much protein do I need per day?",
      "Give me a full daily diet plan for building muscle",
      "What should I eat before and after a workout?",
    ],
  },
  {
    id: "fatloss",
    label: "Fat Loss",
    accent: "var(--accent-fatloss)",
    tagline: "Cutting & cardio",
    starterQuestions: [
      "How do I lose fat without losing muscle?",
      "What's a safe rate of weight loss per week?",
      "Should I do cardio or just diet to lose fat?",
    ],
  },
];

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [selectedCoach, setSelectedCoach] = useState("bodybuilding");
  const [view, setView] = useState("coaches");
  const [profile, setProfile] = useState({
    age: "",
    weight_kg: "",
    experience_level: "",
    goal: "",
    gender: "",
  });

  const activeCoach = COACHES.find((c) => c.id === selectedCoach);

  const handleAuthSuccess = (newToken) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  if (!token) {
    return <AuthForm onAuthSuccess={handleAuthSuccess} />;
  }
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <header className="border-b border-white/10 px-4 md:px-8 py-4 md:py-6 flex items-center justify-between gap-3">
        <div>
          <h1 className="font-[Oswald] uppercase tracking-wide text-xl md:text-3xl font-semibold">
            AI Personal Trainer{" "}
            <span style={{ color: activeCoach.accent }}>Simulator</span>
          </h1>
          <p className="text-(--color-chalk-dim) text-sm mt-1">
            Pick your coach, ask your question.
          </p>
          <p className="text-(--color-chalk-dim) text-xs mt-1 opacity-70">
            AI-generated fitness guidance — not a substitute for professional
            medical advice.
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="text-xs uppercase tracking-wide px-4 py-2 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all shrink-0"
        >
          Log out
        </button>
      </header>

      <div className="flex gap-2 max-w-5xl mx-auto w-full px-4 md:px-8 pt-4 md:pt-8">
        <button
          onClick={() => setView("coaches")}
          className={`text-xs uppercase tracking-wide px-4 py-2 rounded-md border transition-all ${
            view === "coaches"
              ? "border-white/30 bg-white/5"
              : "border-white/10 text-(--color-chalk-dim) hover:border-white/20"
          }`}
        >
          Coaches
        </button>
        <button
          onClick={() => setView("progress")}
          className={`text-xs uppercase tracking-wide px-4 py-2 rounded-md border transition-all ${
            view === "progress"
              ? "border-white/30 bg-white/5"
              : "border-white/10 text-(--color-chalk-dim) hover:border-white/20"
          }`}
        >
          Progress
        </button>
        <button
          onClick={() => setView("plans")}
          className={`text-xs uppercase tracking-wide px-4 py-2 rounded-md border transition-all ${
            view === "plans"
              ? "border-white/30 bg-white/5"
              : "border-white/10 text-(--color-chalk-dim) hover:border-white/20"
          }`}
        >
          Plans
        </button>
      </div>

      {view === "coaches" && (
        <div className="flex flex-col md:flex-row flex-1 max-w-5xl mx-auto w-full px-4 md:px-8 py-4 md:py-8 gap-4 md:gap-8 min-h-0">
          <aside className="w-full md:w-64 shrink-0 overflow-y-auto" style={{ maxHeight: '75vh' }}>
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
                      ? "border-white/30 bg-white/5"
                      : "border-white/10 hover:border-white/20"
                  }`}
                  style={{
                    borderLeftWidth: "4px",
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

            <ProfileForm
              profile={profile}
              setProfile={setProfile}
              token={token}
            />
          </aside>

          <main className="flex-1 border border-white/10 rounded-md overflow-hidden">
            <ChatWindow coach={activeCoach} profile={profile} token={token} />
          </main>
        </div>
      )}

      {view === "progress" && (
        <div className="flex-1 max-w-5xl mx-auto w-full px-4 md:px-8 py-4 md:py-8 min-h-0">
          <div className="h-full border border-white/10 rounded-md overflow-hidden">
            <ProgressTracker token={token} />
          </div>
        </div>
      )}

      {view === "plans" && (
        <div className="flex-1 max-w-5xl mx-auto w-full px-4 md:px-8 py-4 md:py-8 min-h-0">
          <div className="h-full border border-white/10 rounded-md overflow-hidden">
            <PlanViewer token={token} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;