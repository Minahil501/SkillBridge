import { useEffect, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'

const SIZE = 220
const STROKE = 14
const RADIUS = (SIZE - STROKE) / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export default function ScoreGauge({ score }) {
  const clamped = Math.max(0, Math.min(100, score))
  const progress = useMotionValue(0)
  const spring = useSpring(progress, { stiffness: 60, damping: 18 })
  const dashOffset = useTransform(spring, (v) => CIRCUMFERENCE - (v / 100) * CIRCUMFERENCE)
  const [displayed, setDisplayed] = useState(0)

  useEffect(() => {
    progress.set(clamped)
    const unsub = spring.on('change', (v) => setDisplayed(Math.round(v)))
    return unsub
  }, [clamped, progress, spring])

  return (
    <div className="relative" style={{ width: SIZE, height: SIZE }}>
      <svg width={SIZE} height={SIZE} className="-rotate-90">
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--color-velvet)"
          strokeWidth={STROKE}
        />
        <motion.circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--color-plum-light)"
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          style={{ strokeDashoffset: dashOffset }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-5xl font-semibold text-almond tabular-nums">{displayed}</span>
        <span className="text-sandlewood text-sm tracking-wide uppercase mt-1">Employability</span>
      </div>
    </div>
  )
}
