import { useState } from 'react'
import ContextMenu from './ContextMenu'

function HistoryPanel({ isOpen, onClose, entries, onSelect, onDelete, onDeleteSingle, coachLabel }) {
  const [contextMenu, setContextMenu] = useState(null)

  if (!isOpen) return null

  const handleRightClick = (e, entryId) => {
    e.preventDefault()
    setContextMenu({ x: e.clientX, y: e.clientY, entryId })
  }

  const handleDeleteSingle = () => {
    if (contextMenu) {
      onDeleteSingle(contextMenu.entryId)
      setContextMenu(null)
    }
  }

  return (
    <div className="absolute inset-0 z-10 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      <div className="relative w-72 h-full bg-(--color-bg-elevated) border-l border-white/10 flex flex-col">
        <div className="flex items-center justify-between px-4 py-4 border-b border-white/10">
          <h3 className="text-xs uppercase tracking-widest text-(--color-chalk-dim)">
            {coachLabel} History
          </h3>
          <button
            onClick={onClose}
            className="text-(--color-chalk-dim) hover:text-(--color-chalk) text-lg leading-none"
          >
            ×
          </button>
        </div>

        {entries.length > 0 && (
          <div className="px-4 py-3 border-b border-white/10">
            <button
              onClick={onDelete}
              className="text-xs uppercase tracking-wide text-red-400 hover:text-red-300 transition-all"
            >
              Delete All History
            </button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-2">
          {entries.length === 0 && (
            <p className="text-xs text-(--color-chalk-dim) px-2 py-4 text-center">
              No conversations yet.
            </p>
          )}

          {entries.map((entry) => (
            <button
              key={entry.id}
              onClick={() => onSelect(entry.id)}
              onContextMenu={(e) => handleRightClick(e, entry.id)}
              className="text-left px-3 py-2 rounded-md hover:bg-white/5 transition-all border border-transparent hover:border-white/10"
            >
              <p className="text-xs text-(--color-chalk) line-clamp-2">
                {entry.question}
              </p>
              <p className="text-[10px] text-(--color-chalk-dim) mt-1">
                {new Date(entry.created_at).toLocaleString()}
              </p>
            </button>
          ))}
        </div>
      </div>

      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          onDelete={handleDeleteSingle}
          onClose={() => setContextMenu(null)}
        />
      )}
    </div>
  )
}

export default HistoryPanel