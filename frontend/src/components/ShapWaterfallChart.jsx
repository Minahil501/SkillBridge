import { motion } from 'framer-motion'
import { LABELS } from '../data/topFeatures'

const WIDTH = 600
const HEIGHT = 240
const MARGIN = { top: 24, right: 16, bottom: 64, left: 16 }

export default function ShapWaterfallChart({ waterfall, title, note }) {
  if (!waterfall?.points?.length) return null
  const { points } = waterfall

  const values = points.map((p) => p.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const pad = (max - min) * 0.2 || 1
  const yMin = min - pad
  const yMax = max + pad

  const plotW = WIDTH - MARGIN.left - MARGIN.right
  const plotH = HEIGHT - MARGIN.top - MARGIN.bottom
  const xStep = points.length > 1 ? plotW / (points.length - 1) : 0
  const yScale = (v) => MARGIN.top + plotH - ((v - yMin) / (yMax - yMin || 1)) * plotH

  const coords = points.map((p, i) => [MARGIN.left + i * xStep, yScale(p.value)])
  const linePath = coords.map(([x, y], i) => `${i === 0 ? 'M' : 'L'} ${x} ${y}`).join(' ')

  return (
    <div className="bg-carbon/40 border border-sandlewood/15 rounded-2xl p-5">
      <p className="text-sm text-sandlewood mb-1">{title}</p>
      {note && <p className="text-[11px] text-sandlewood/60 mb-3">{note}</p>}
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full overflow-visible">
        <motion.path
          d={linePath}
          fill="none"
          stroke="var(--color-plum-light)"
          strokeWidth="2"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
        {coords.map(([x, y], i) => {
          const isEndpoint = i === 0 || i === coords.length - 1
          return (
            <motion.circle
              key={i}
              cx={x}
              cy={y}
              r={isEndpoint ? 5 : 3.5}
              fill={isEndpoint ? 'var(--color-almond)' : 'var(--color-plum-light)'}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.05 * i + 0.3 }}
            />
          )
        })}
        {coords.map(([x, y], i) => (
          <text
            key={`v${i}`}
            x={x}
            y={y - 10}
            textAnchor="middle"
            fontSize="9"
            fill="var(--color-almond)"
          >
            {points[i].value}
          </text>
        ))}
        {points.map((p, i) => (
          <text
            key={p.label}
            x={coords[i][0]}
            y={HEIGHT - MARGIN.bottom + 18}
            textAnchor="end"
            fontSize="9"
            fill="var(--color-sandlewood)"
            transform={`rotate(-35 ${coords[i][0]} ${HEIGHT - MARGIN.bottom + 18})`}
          >
            {LABELS[p.label] ?? p.label}
          </text>
        ))}
      </svg>
    </div>
  )
}
