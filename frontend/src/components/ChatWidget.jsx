import { useState, useRef, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { sendChatMessage } from '../lib/api'

export default function ChatWidget({ result }) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, loading])

  const send = async (e) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || loading) return
    const next = [...messages, { role: 'user', content: text }]
    setMessages(next)
    setInput('')
    setLoading(true)
    setError(null)
    try {
      const { reply } = await sendChatMessage(next, result)
      setMessages((m) => [...m, { role: 'assistant', content: reply }])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="w-[min(92vw,380px)] bg-carbon border border-sandlewood/25 rounded-2xl overflow-hidden shadow-2xl shadow-black/50"
          >
            <div className="flex items-center justify-between px-5 py-3 border-b border-sandlewood/15 bg-velvet/60">
              <p className="text-sm text-almond font-medium">Career chat</p>
              <button
                onClick={() => setOpen(false)}
                className="text-sandlewood hover:text-almond text-sm cursor-pointer"
              >
                Close
              </button>
            </div>

            <div ref={scrollRef} className="max-h-80 overflow-y-auto px-5 py-4 flex flex-col gap-3">
              {messages.length === 0 && (
                <p className="text-sm text-sandlewood/70">
                  Ask about your score, how to prepare for {result.recommended_career_path}, or why
                  another career might also fit.
                </p>
              )}
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`text-sm max-w-[85%] px-3 py-2 rounded-xl ${
                    m.role === 'user'
                      ? 'self-end bg-plum text-almond'
                      : 'self-start bg-velvet text-almond'
                  }`}
                >
                  {m.content}
                </div>
              ))}
              {loading && (
                <div className="self-start flex gap-1 px-3 py-2">
                  {[0, 1, 2].map((i) => (
                    <motion.span
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-sandlewood"
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ repeat: Infinity, duration: 1, delay: i * 0.15 }}
                    />
                  ))}
                </div>
              )}
              {error && <p className="text-sm text-plum-light">{error}</p>}
            </div>

            <form onSubmit={send} className="flex gap-2 px-4 py-3 border-t border-sandlewood/15">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question..."
                className="flex-1 bg-velvet border border-sandlewood/30 rounded-lg px-3 py-2 text-sm text-almond
                           placeholder:text-sandlewood/50 focus:outline-none focus:border-plum-light"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 rounded-lg bg-plum hover:bg-plum-light text-almond text-sm
                           transition-colors cursor-pointer disabled:opacity-50"
              >
                Send
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onClick={() => setOpen((o) => !o)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="flex items-center gap-2 px-5 py-3.5 rounded-full bg-plum hover:bg-plum-light text-almond
                   font-medium shadow-xl shadow-plum/40 cursor-pointer transition-colors"
      >
        <span className="text-lg leading-none">{open ? '×' : '💬'}</span>
        {!open && 'Ask about your result'}
      </motion.button>
    </div>
  )
}
