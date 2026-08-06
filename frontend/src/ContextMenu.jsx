import { useEffect, useRef } from 'react'

function ContextMenu({ x, y, onDelete, onClose }) {
  const menuRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onClose])

  return (
    <div
      ref={menuRef}
      style={{ top: y, left: x }}
      className="fixed z-50 bg-(--color-bg-elevated) border border-white/10 rounded-md shadow-lg py-1 min-w-[140px]"
    >
      <button
        onClick={onDelete}
        className="w-full text-left px-3 py-2 text-xs text-red-400 hover:bg-red-900/20 transition-all"
      >
        Delete conversation
      </button>
    </div>
  )
}

export default ContextMenu