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

export async function sendChatMessage(messages, context) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages,
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
      detail = JSON.parse(detail).detail ?? detail
    } catch {
      // keep raw text
    }
    throw new Error(detail)
  }

  return res.json()
}
