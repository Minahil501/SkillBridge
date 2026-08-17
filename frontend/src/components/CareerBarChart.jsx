import { useState } from 'react'
import { motion } from 'framer-motion'

const WIDTH = 480
const ROW_H = 34
const GAP = 10
const LABEL_W = 150
const BAR_MAX_W = WIDTH - LABEL_W - 50

export default function CareerBarChart({ probabilities, topCareer }) {
  const [hovered, setHovered] = useState(null)
  if (!probabilities) return null
  const entries = Object.entries(probabilities).sort((a, b) => b[1] - a[1])
  const height = entries.length * (ROW_H + GAP)

  return (
    <div className="bg-carbon/40 border border-sandlewood/15 rounded-2xl p-5">
      <p className="text-sm text-sandlewood mb-4">Confidence across all careers</p>
      <svg width="100%" viewBox={`0 0 ${WIDTH} ${height}`} className="overflow-visible">
        {entries.map(([name, prob], i) => {
          const y = i * (ROW_H + GAP)
          const barW = Math.max(prob * BAR_MAX_W, 2)
          const isTop = name === topCareer
          const isHovered = hovered === name
          return (
            <g
              key={name}
              onMouseEnter={() => setHovered(name)}
              onMouseLeave={() => setHovered(null)}
              style={{ cursor: 'default' }}
            >
              <text
                x={LABEL_W - 10}
                y={y + ROW_H / 2}
                textAnchor="end"
                dominantBaseline="middle"
                fontSize="12"
                fill="var(--color-almond)"
                opacity={isTop || isHovered ? 1 : 0.75}
              >
                {name}
              </text>
              <rect
                x={LABEL_W}
                y={y + 4}
                width={BAR_MAX_W}
                height={ROW_H - 8}
                rx="4"
                fill="var(--color-velvet)"
              />
              <motion.rect
                x={LABEL_W}
                y={y + 4}
                height={ROW_H - 8}
                rx="4"
                fill={isTop ? 'var(--color-plum-light)' : 'var(--color-sandlewood)'}
                opacity={isTop ? 1 : isHovered ? 0.85 : 0.55}
                initial={{ width: 0 }}
                animate={{ width: barW }}
                transition={{ duration: 0.6, delay: i * 0.06, ease: 'easeOut' }}
              />
              <text
                x={LABEL_W + BAR_MAX_W + 8}
                y={y + ROW_H / 2}
                dominantBaseline="middle"
                fontSize="12"
                fontWeight={isTop ? 600 : 400}
                fill={isTop ? 'var(--color-almond)' : 'var(--color-sandlewood)'}
              >
                {Math.round(prob * 100)}%
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
