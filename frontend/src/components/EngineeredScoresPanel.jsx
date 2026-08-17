import { motion } from 'framer-motion'
import { LABELS } from '../data/topFeatures'

export default function EngineeredScoresPanel({ scores }) {
  if (!scores) return null
  const entries = Object.entries(scores)

  return (
    <div className="bg-carbon/40 border border-sandlewood/15 rounded-2xl p-4">
      <p className="text-sm text-sandlewood mb-1">Computed metrics</p>
      <p className="text-[11px] text-sandlewood/60 mb-2.5">
        Derived internally from your raw inputs — shown for transparency, not directly editable.
      </p>
      <ul className="flex flex-col gap-1.5">
        {entries.map(([key, value], i) => (
          <motion.li
            key={key}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.03 * i }}
            className="flex justify-between text-xs gap-3"
          >
            <span className="text-sandlewood">{LABELS[key] ?? key}</span>
            <span className="text-almond tabular-nums shrink-0">{value}</span>
          </motion.li>
        ))}
      </ul>
    </div>
  )
}
