import { useState, useEffect, useRef } from 'react'
import HistoryPanel from './HistoryPanel'

const API_URL = 'http://127.0.0.1:8000'

function ChatWindow({ coach, profile, token }) {
  const [messages, setMessages] = useState([])
  const [historyEntries, setHistoryEntries] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [panelOpen, setPanelOpen] = useState(false)
  const [highlightedId, setHighlightedId] = useState(null)

  const messageRefs = useRef({})

  useEffect(() => {
    const loadHistory = async () => {
      setLoadingHistory(true)
      try {
        const response = await fetch(`${API_URL}/chat/history`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (response.ok) {
          const data = await response.json()
          const coachHistory = data
            .filter((entry) => entry.coach_type === coach.id)
            .reverse()

          setHistoryEntries(coachHistory)

          const historyMessages = coachHistory.flatMap((entry) => [
            { role: 'user', content: entry.question, historyId: entry.id },
            { role: 'assistant', content: entry.answer, sources: entry.sources, historyId: entry.id },
          ])

          setMessages(historyMessages)
        }
      } catch (err) {
        console.error('Failed to load chat history:', err)
      } finally {
        setLoadingHistory(false)
      }
    }

    if (token) loadHistory()
  }, [coach.id, token])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          question: userMessage.content,
          coach_type: coach.id,
          profile: {
            age: profile.age ? parseInt(profile.age) : null,
            weight_kg: profile.weight_kg ? parseFloat(profile.weight_kg) : null,
            experience_level: profile.experience_level || null,
            goal: profile.goal || null,
          },
        }),
      })

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }

      const data = await response.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'error', content: `Something went wrong: ${err.message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleSelectHistory = (historyId) => {
    setPanelOpen(false)
    const node = messageRefs.current[historyId]
    if (node) {
      node.scrollIntoView({ behavior: 'smooth', block: 'center' })
      setHighlightedId(historyId)
      setTimeout(() => setHighlightedId(null), 1500)
    }
  }

  const handleDeleteHistory = async () => {
    const confirmed = window.confirm(`Delete all ${coach.label} conversation history? This cannot be undone.`)
    if (!confirmed) return

    try {
      const response = await fetch(`${API_URL}/chat/history?coach_type=${coach.id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        setHistoryEntries([])
        setMessages([])
        setPanelOpen(false)
      }
    } catch (err) {
      console.error('Failed to delete history:', err)
    }
  }

  return (
    <div className="relative flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4">
        <div className="flex justify-end gap-2">
          {historyEntries.length > 0 && (
            <button
              onClick={() => setPanelOpen(true)}
              className="text-xs uppercase tracking-wide px-3 py-1.5 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all"
            >
              History
            </button>
          )}
          {messages.length > 0 && !loadingHistory && (
            <button
              onClick={() => setMessages([])}
              className="text-xs uppercase tracking-wide px-3 py-1.5 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all"
            >
              Clear View
            </button>
          )}
        </div>

        {loadingHistory && (
          <p className="text-(--color-chalk-dim) text-sm m-auto">Loading conversation...</p>
        )}

        {!loadingHistory && messages.length === 0 && (
          <p className="text-(--color-chalk-dim) text-sm m-auto">
            Ask your {coach.label} Coach a question to get started.
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            ref={(el) => {
              if (msg.historyId && msg.role === 'user') messageRefs.current[msg.historyId] = el
            }}
            className={`max-w-[80%] px-4 py-3 rounded-md text-sm transition-all ${
              msg.role === 'user'
                ? 'self-end bg-white/10'
                : msg.role === 'error'
                ? 'self-start bg-red-900/30 text-red-300'
                : 'self-start bg-(--color-bg-elevated)'
            } ${highlightedId === msg.historyId ? 'ring-2' : ''}`}
            style={highlightedId === msg.historyId ? { ringColor: coach.accent } : {}}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <p className="text-xs text-(--color-chalk-dim) mt-2 pt-2 border-t border-white/10">
                Sources: {msg.sources.join(', ')}
              </p>
            )}
          </div>
        ))}

        {loading && (
          <div className="self-start bg-(--color-bg-elevated) px-4 py-3 rounded-md text-sm text-(--color-chalk-dim)">
            {coach.label} Coach is thinking...
          </div>
        )}
      </div>

      <div className="border-t border-white/10 p-4 flex gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask the ${coach.label} Coach...`}
          rows={1}
          className="flex-1 bg-(--color-bg-elevated) rounded-md px-4 py-3 text-sm resize-none outline-none placeholder:text-(--color-chalk-dim)"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="px-5 py-2 rounded-md text-sm font-medium uppercase tracking-wide disabled:opacity-40 transition-opacity"
          style={{ backgroundColor: coach.accent, color: '#1C1D1F' }}
        >
          Send
        </button>
      </div>

      <HistoryPanel
        isOpen={panelOpen}
        onClose={() => setPanelOpen(false)}
        entries={historyEntries}
        onSelect={handleSelectHistory}
        onDelete={handleDeleteHistory}
        coachLabel={coach.label}
      />
    </div>
  )
}

export default ChatWindow