import { useState } from 'react'
import ContextMenu from './ContextMenu'

function HistoryPanel({ isOpen, onClose, conversations, onSelect, onDelete, coachLabel }) {
  const [contextMenu, setContextMenu] = useState(null)

  if (!isOpen) return null

  const handleRightClick = (e, convId) => {
    e.preventDefault()
    setContextMenu({ x: e.clientX, y: e.clientY, convId })
  }

  const handleDotsClick = (e, convId) => {
    e.stopPropagation()
    const rect = e.currentTarget.getBoundingClientRect()
    setContextMenu({ x: rect.right - 140, y: rect.bottom + 4, convId })
  }

  const handleDeleteFromMenu = () => {
    if (contextMenu) {
      onDelete(contextMenu.convId)
      setContextMenu(null)
    }
  }

  return (
    <div className="absolute inset-0 z-10 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      <div className="relative w-72 h-full bg-(--color-bg-elevated) border-l border-white/10 flex flex-col">
        <div className="flex items-center justify-between px-4 py-4 border-b border-white/10">
          <h3 className="text-xs uppercase tracking-widest text-(--color-chalk-dim)">
            {coachLabel} Conversations
          </h3>
          <button
            onClick={onClose}
            className="text-(--color-chalk-dim) hover:text-(--color-chalk) text-lg leading-none"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-2">
          {conversations.length === 0 && (
            <p className="text-xs text-(--color-chalk-dim) px-2 py-4 text-center">
              No conversations yet.
            </p>
          )}

          {conversations.map((conv) => (
            <div
              key={conv.conversation_id}
              onContextMenu={(e) => handleRightClick(e, conv.conversation_id)}
              className="relative flex items-start gap-1 rounded-md hover:bg-white/5 transition-all border border-transparent hover:border-white/10"
            >
              <button
                onClick={() => onSelect(conv.conversation_id)}
                className="flex-1 text-left px-3 py-2 min-w-0"
              >
                <p className="text-xs text-(--color-chalk) line-clamp-2">
                  {conv.title}
                </p>
                <p className="text-[10px] text-(--color-chalk-dim) mt-1">
                  {new Date(conv.created_at).toLocaleDateString()} · {conv.message_count} message{conv.message_count !== 1 ? 's' : ''}
                </p>
              </button>

              <button
                onClick={(e) => handleDotsClick(e, conv.conversation_id)}
                className="shrink-0 px-2 py-2 text-(--color-chalk-dim) hover:text-(--color-chalk) text-sm"
                aria-label="More options"
              >
                ⋮
              </button>
            </div>
          ))}
        </div>
      </div>

      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          onDelete={handleDeleteFromMenu}
          onClose={() => setContextMenu(null)}
        />
      )}
    </div>
  )
}

export default HistoryPanel