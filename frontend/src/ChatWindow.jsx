import { useState, useEffect, useRef } from 'react'
import HistoryPanel from './HistoryPanel'

const API_URL = 'http://127.0.0.1:8000'

function ChatWindow({ coach, profile, token }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [panelOpen, setPanelOpen] = useState(false)
  const [copiedId, setCopiedId] = useState(null)
  const [conversationId, setConversationId] = useState(null)
  const [conversations, setConversations] = useState([])
  const [isListening, setIsListening] = useState(false)

  const recognitionRef = useRef(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    const loadConversations = async () => {
      setLoadingHistory(true)
      try {
        const response = await fetch(`${API_URL}/chat/conversations?coach_type=${coach.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (response.ok) {
          const data = await response.json()
          setConversations(data)
        }
      } catch (err) {
        console.error('Failed to load conversations:', err)
      } finally {
        setLoadingHistory(false)
      }
    }

    setMessages([])
    setConversationId(null)
    if (token) loadConversations()
  }, [coach.id, token])

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }, [messages, loading])

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
          conversation_id: conversationId,
          profile: {
            age: profile.age ? parseInt(profile.age) : null,
            weight_kg: profile.weight_kg ? parseFloat(profile.weight_kg) : null,
            experience_level: profile.experience_level || null,
            goal: profile.goal || null,
            gender: profile.gender || null,
          },
        }),
      })

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`)
      }

      const data = await response.json()
      setConversationId(data.conversation_id)
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

  const handleCopy = async (content, messageIndex) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedId(messageIndex)
      setTimeout(() => setCopiedId(null), 1500)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }
  const handleExport = () => {
    if (messages.length === 0) return

    const lines = [`${coach.label} Coach — Conversation Export`, `Exported: ${new Date().toLocaleString()}`, '']

    messages.forEach((msg) => {
      if (msg.role === 'user') {
        lines.push(`You: ${msg.content}`)
      } else if (msg.role === 'assistant') {
        lines.push(`${coach.label} Coach: ${msg.content}`)
        if (msg.sources && msg.sources.length > 0) {
          lines.push(`(Sources: ${msg.sources.join(', ')})`)
        }
      }
      lines.push('')
    })

    const text = lines.join('\n')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = `${coach.id}-conversation-${new Date().toISOString().slice(0, 10)}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
  const handleNewChat = () => {
    setMessages([])
    setConversationId(null)
  }

  const loadConversation = async (convId) => {
    setLoadingHistory(true)
    try {
      const response = await fetch(`${API_URL}/chat/conversations/${convId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        const loadedMessages = data.flatMap((entry) => [
          { role: 'user', content: entry.question },
          { role: 'assistant', content: entry.answer, sources: entry.sources },
        ])
        setMessages(loadedMessages)
        setConversationId(convId)
      }
    } catch (err) {
      console.error('Failed to load conversation:', err)
    } finally {
      setLoadingHistory(false)
      setPanelOpen(false)
    }
  }

  const handleDeleteConversation = async (convId) => {
    const confirmed = window.confirm('Delete this conversation? This cannot be undone.')
    if (!confirmed) return

    try {
      const response = await fetch(`${API_URL}/chat/history?conversation_id=${convId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        setConversations((prev) => prev.filter((c) => c.conversation_id !== convId))
        if (conversationId === convId) {
          setMessages([])
          setConversationId(null)
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err)
    }
  }
  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      alert('Voice input is not supported in this browser. Try Chrome or Edge.')
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
    }
    recognition.onresult = (event) => {
      console.log('Speech recognition result event:', event)
      const transcript = event.results[0][0].transcript
      console.log('Transcript:', transcript)
      setInput((prev) => (prev ? `${prev} ${transcript}` : transcript))
    }
    recognitionRef.current = recognition
    recognition.start()
  }

  return (
    <div className="relative flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4">
        <div className="flex justify-end gap-2">
          <button
            onClick={handleNewChat}
            className="text-xs uppercase tracking-wide px-3 py-1.5 rounded-md font-medium transition-opacity"
            style={{ backgroundColor: coach.accent, color: '#1C1D1F' }}
          >
            + New Chat
          </button>
          {messages.length > 0 && !loadingHistory && (
            <button
              onClick={handleExport}
              className="text-xs uppercase tracking-wide px-3 py-1.5 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all"
            >
              Export
            </button>
          )}
          {conversations.length > 0 && (
            <button
              onClick={() => setPanelOpen(true)}
              className="text-xs uppercase tracking-wide px-3 py-1.5 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all"
            >
              History
            </button>
          )}
        </div>

        {loadingHistory && (
          <p className="text-(--color-chalk-dim) text-sm m-auto">Loading conversation...</p>
        )}

        {!loadingHistory && messages.length === 0 && (
          <div className="m-auto flex flex-col items-center gap-4 max-w-md">
            <p className="text-(--color-chalk-dim) text-sm text-center">
              Ask your {coach.label} Coach a question to get started.
            </p>
            {coach.starterQuestions && (
              <div className="flex flex-col gap-2 w-full">
                {coach.starterQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(q)}
                    className="text-left text-xs px-3 py-2 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`group relative max-w-[80%] px-4 py-3 rounded-md text-sm transition-all ${
              msg.role === 'user'
                ? 'self-end bg-white/10'
                : msg.role === 'error'
                ? 'self-start bg-red-900/30 text-red-300'
                : 'self-start bg-(--color-bg-elevated)'
            }`}
          >
            <p className="whitespace-pre-wrap pr-6">{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <p className="text-xs text-(--color-chalk-dim) mt-2 pt-2 border-t border-white/10">
                Sources: {msg.sources.join(', ')}
              </p>
            )}

            {msg.role !== 'error' && (
              <button
                onClick={() => handleCopy(msg.content, i)}
                className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-(--color-chalk-dim) hover:text-(--color-chalk)"
                aria-label="Copy message"
                title={copiedId === i ? 'Copied!' : 'Copy'}
              >
                {copiedId === i ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                )}
              </button>
            )}
          </div>
        ))}

        {loading && (
          <div className="self-start bg-(--color-bg-elevated) px-4 py-3 rounded-md flex items-center gap-3">
            <span className="text-sm text-(--color-chalk-dim)">{coach.label} Coach is typing</span>
            <span className="flex gap-1">
              <span
                className="typing-dot w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: coach.accent }}
              />
              <span
                className="typing-dot w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: coach.accent }}
              />
              <span
                className="typing-dot w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: coach.accent }}
              />
            </span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-white/10 p-4 flex gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isListening ? 'Listening...' : `Ask the ${coach.label} Coach...`}
          rows={1}
          className="flex-1 bg-(--color-bg-elevated) rounded-md px-4 py-3 text-sm resize-none outline-none placeholder:text-(--color-chalk-dim)"
        />
                <div className="relative">
          <button
            onClick={handleVoiceInput}
            className={`px-4 py-2 rounded-md transition-all ${
              isListening
                ? 'bg-red-500/20 text-red-400 animate-pulse'
                : 'border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30'
            }`}
            aria-label={isListening ? 'Stop listening' : 'Voice input'}
            title={isListening ? 'Stop listening (Beta — reliability varies by browser)' : 'Voice input (Beta — reliability varies by browser)'}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </svg>
          </button>
          <span className="absolute -top-1.5 -right-1.5 text-[8px] uppercase tracking-wide bg-white/10 text-(--color-chalk-dim) px-1 py-0.5 rounded">
            Beta
          </span>
        </div>
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
        conversations={conversations}
        onSelect={loadConversation}
        onDelete={handleDeleteConversation}
        coachLabel={coach.label}
      />
    </div>
  )
}

export default ChatWindow