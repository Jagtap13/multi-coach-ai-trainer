import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:8000'
const ACCENT = '#3D6B8C'

function KnowledgeBaseAdmin({ token }) {
  const [files, setFiles] = useState({})
  const [activeFile, setActiveFile] = useState(null)
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(true)
  const [forbidden, setForbidden] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState(null)

  const loadFiles = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/admin/knowledge-base`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.status === 403) {
        setForbidden(true)
        return
      }
      if (response.ok) {
        const data = await response.json()
        setFiles(data)
        const firstFile = Object.keys(data)[0]
        setActiveFile(firstFile)
        setDraft(data[firstFile] || '')
      }
    } catch (err) {
      console.error('Failed to load knowledge base:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFiles()
  }, [])

  const selectFile = (filename) => {
    setActiveFile(filename)
    setDraft(files[filename] || '')
    setSaveStatus(null)
  }

  const handleSave = async () => {
    setSaving(true)
    setSaveStatus(null)
    try {
      const response = await fetch(`${API_URL}/admin/knowledge-base/${activeFile}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content: draft }),
      })
      if (response.ok) {
        setFiles((prev) => ({ ...prev, [activeFile]: draft }))
        setSaveStatus('success')
      } else {
        setSaveStatus('error')
      }
    } catch (err) {
      console.error('Failed to save knowledge base:', err)
      setSaveStatus('error')
    } finally {
      setSaving(false)
      setTimeout(() => setSaveStatus(null), 3000)
    }
  }

  const hasChanges = activeFile && draft !== (files[activeFile] || '')

  if (loading) {
    return <div className="h-full p-6"><p className="text-(--color-chalk-dim) text-sm">Loading knowledge base...</p></div>
  }

  if (forbidden) {
    return <div className="h-full p-6"><p className="text-(--color-chalk-dim) text-sm">This section is restricted to admin accounts.</p></div>
  }

  return (
    <div className="h-full flex flex-col p-6">
      <h2 className="font-[Oswald] uppercase tracking-wide text-lg mb-1" style={{ color: ACCENT }}>
        Knowledge Base
      </h2>
      <p className="text-(--color-chalk-dim) text-sm mb-4">
        Edit each coach's source content. Saving automatically rebuilds the retrieval index.
      </p>

      <div className="flex gap-2 mb-4">
        {Object.keys(files).map((filename) => (
          <button
            key={filename}
            onClick={() => selectFile(filename)}
            className={`text-xs uppercase tracking-wide px-3 py-1.5 rounded-md border transition-all ${
              activeFile === filename
                ? 'border-white/30 bg-white/5'
                : 'border-white/10 text-(--color-chalk-dim) hover:border-white/20'
            }`}
          >
            {filename.replace('.txt', '')}
          </button>
        ))}
      </div>

      <textarea
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        className="flex-1 bg-(--color-bg-elevated) rounded-md border border-white/10 p-4 text-sm font-mono resize-none outline-none"
        spellCheck={false}
      />

      <div className="flex items-center gap-3 mt-4">
        <button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className="px-5 py-2 rounded-md text-sm font-medium uppercase tracking-wide disabled:opacity-40 transition-opacity"
          style={{ backgroundColor: ACCENT, color: '#1C1D1F' }}
        >
          {saving ? 'Saving & Re-ingesting...' : 'Save & Re-ingest'}
        </button>
        {saveStatus === 'success' && (
          <span className="text-xs text-green-400">Saved and re-indexed successfully.</span>
        )}
        {saveStatus === 'error' && (
          <span className="text-xs text-red-400">Save failed — check the backend logs.</span>
        )}
        {hasChanges && !saving && !saveStatus && (
          <span className="text-xs text-(--color-chalk-dim)">Unsaved changes</span>
        )}
      </div>
    </div>
  )
}

export default KnowledgeBaseAdmin