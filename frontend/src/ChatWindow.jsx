import { useState } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function ChatWindow({ coach }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          coach_type: coach.id,
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

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4">
        {messages.length === 0 && (
          <p className="text-[var(--color-chalk-dim)] text-sm m-auto">
            Ask your {coach.label} Coach a question to get started.
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-[80%] px-4 py-3 rounded-md text-sm ${
              msg.role === 'user'
                ? 'self-end bg-white/10'
                : msg.role === 'error'
                ? 'self-start bg-red-900/30 text-red-300'
                : 'self-start bg-[var(--color-bg-elevated)]'
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <p className="text-xs text-[var(--color-chalk-dim)] mt-2 pt-2 border-t border-white/10">
                Sources: {msg.sources.join(', ')}
              </p>
            )}
          </div>
        ))}

        {loading && (
          <div className="self-start bg-[var(--color-bg-elevated)] px-4 py-3 rounded-md text-sm text-[var(--color-chalk-dim)]">
            {coach.label} Coach is thinking...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-white/10 p-4 flex gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Ask the ${coach.label} Coach...`}
          rows={1}
          className="flex-1 bg-[var(--color-bg-elevated)] rounded-md px-4 py-3 text-sm resize-none outline-none placeholder:text-[var(--color-chalk-dim)]"
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
    </div>
  )
}

export default ChatWindow