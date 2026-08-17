import { useState } from 'react'
import { motion } from 'framer-motion'

const SIZE = 280
const CENTER = SIZE / 2
const RADIUS = SIZE / 2 - 40
const MAX_VALUE = 100

const AXES = [
  { key: 'DSA_Score', label: 'DSA' },
  { key: 'Programming_Score', label: 'Programming' },
  { key: 'WebDev_Score', label: 'Web Dev' },
  { key: 'ML_Score', label: 'ML' },
  { key: 'Communication_Score', label: 'Communication' },
  { key: 'Leadership_Score', label: 'Leadership' },
]

function pointFor(index, total, value) {
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2
  const r = (value / MAX_VALUE) * RADIUS
  return [CENTER + r * Math.cos(angle), CENTER + r * Math.sin(angle)]
}

export default function SkillRadarChart({ profile }) {
  const [hovered, setHovered] = useState(null)
  const values = AXES.map((a) => Number(profile[a.key]) || 0)
  const dataPoints = AXES.map((a, i) => pointFor(i, AXES.length, values[i]))
  const dataPath = dataPoints.map((p) => p.join(',')).join(' ')

  const rings = [0.25, 0.5, 0.75, 1]

  return (
    <div className="bg-carbon/40 border border-sandlewood/15 rounded-2xl p-5">
      <p className="text-sm text-sandlewood mb-4">Skill profile</p>
      <svg width="100%" viewBox={`0 0 ${SIZE} ${SIZE}`} className="overflow-visible">
        {rings.map((frac) => {
          const ringPoints = AXES.map((_, i) => pointFor(i, AXES.length, MAX_VALUE * frac))
          return (
            <polygon
              key={frac}
              points={ringPoints.map((p) => p.join(',')).join(' ')}
              fill="none"
              stroke="var(--color-sandlewood)"
              strokeOpacity={0.2}
              strokeWidth="1"
            />
          )
        })}

        {AXES.map((axis, i) => {
          const [x, y] = pointFor(i, AXES.length, MAX_VALUE)
          return (
            <line
              key={axis.key}
              x1={CENTER}
              y1={CENTER}
              x2={x}
              y2={y}
              stroke="var(--color-sandlewood)"
              strokeOpacity={0.2}
              strokeWidth="1"
            />
          )
        })}

        <motion.polygon
          points={dataPath}
          fill="var(--color-plum-light)"
          fillOpacity={0.35}
          stroke="var(--color-plum-light)"
          strokeWidth="2"
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{ transformOrigin: `${CENTER}px ${CENTER}px` }}
        />

        {dataPoints.map(([x, y], i) => (
          <circle
            key={AXES[i].key}
            cx={x}
            cy={y}
            r={hovered === AXES[i].key ? 6 : 4}
            fill="var(--color-almond)"
            stroke="var(--color-plum-light)"
            strokeWidth="2"
            onMouseEnter={() => setHovered(AXES[i].key)}
            onMouseLeave={() => setHovered(null)}
            style={{ cursor: 'default' }}
          />
        ))}

        {AXES.map((axis, i) => {
          const [x, y] = pointFor(i, AXES.length, MAX_VALUE * 1.18)
          return (
            <text
              key={axis.key}
              x={x}
              y={y}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="10"
              fill={hovered === axis.key ? 'var(--color-almond)' : 'var(--color-sandlewood)'}
            >
              {axis.label}
              {hovered === axis.key ? ` (${values[i]})` : ''}
            </text>
          )
        })}
      </svg>
    </div>
  )
}
