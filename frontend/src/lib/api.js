const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export async function predictCareer(profile) {
  const payload = Object.fromEntries(
    Object.entries(profile).map(([key, value]) => [
      key,
      typeof value === 'string' && value.trim() !== '' && !Number.isNaN(Number(value))
        ? Number(value)
        : value,
    ])
  )

  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`Prediction failed (${res.status}): ${detail}`)
  }

  return res.json()
}

// Only the most recent turns are sent, keeping each request small. Must stay <= the
// backend's ChatRequest.messages max_length (backend/main.py).
const CHAT_HISTORY_LIMIT = 10

export async function sendChatMessage(messages, context) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: messages.slice(-CHAT_HISTORY_LIMIT),
      context: {
        employability_score: context.employability_score,
        recommended_career_path: context.recommended_career_path,
        confidence: context.confidence,
        career_probabilities: context.career_probabilities,
      },
    }),
  })

  if (!res.ok) {
    let detail = await res.text()
    try {
      const parsed = JSON.parse(detail).detail
      if (typeof parsed === 'string') detail = parsed
      // Validation errors (422) come back as a list of objects, not a readable string
      else if (Array.isArray(parsed)) detail = 'Your message could not be sent. It may be too long.'
    } catch {
      // keep raw text
    }
    throw new Error(detail)
  }

  return res.json()
}
