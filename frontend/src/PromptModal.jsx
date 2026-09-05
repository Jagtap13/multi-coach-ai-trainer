import { useState, useEffect } from 'react'

function PromptModal({ isOpen, mode = 'confirm', title, message, defaultValue = '', confirmLabel = 'Confirm', accentColor = '#C0503D', onConfirm, onCancel }) {
  const [value, setValue] = useState(defaultValue)

  useEffect(() => {
    if (isOpen) setValue(defaultValue)
  }, [isOpen, defaultValue])

  if (!isOpen) return null

  const handleConfirm = () => {
    if (mode === 'prompt') {
      if (!value.trim()) return
      onConfirm(value.trim())
    } else {
      onConfirm()
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50"
      onClick={onCancel}
    >
      <div
        className="bg-(--color-bg) rounded-md border border-white/10 w-full max-w-sm p-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="text-sm font-medium mb-2">{title}</div>
        {message && (
          <p className="text-sm text-(--color-chalk-dim) mb-4">{message}</p>
        )}
        {mode === 'prompt' && (
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleConfirm() }}
            autoFocus
            className="w-full bg-black/20 rounded-md px-3 py-2 text-sm outline-none mb-4"
          />
        )}
        <div className="flex justify-end gap-2">
          <button
            onClick={onCancel}
            className="text-xs uppercase tracking-wide px-4 py-2 rounded-md border border-white/10 text-(--color-chalk-dim) hover:text-(--color-chalk) hover:border-white/30 transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="text-xs uppercase tracking-wide px-4 py-2 rounded-md font-medium transition-opacity"
            style={{ backgroundColor: accentColor, color: '#1C1D1F' }}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PromptModal