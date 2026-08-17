import { useState } from 'react'
import { motion } from 'framer-motion'
import { LABELS } from '../data/topFeatures'

const ASSESSMENT_STYLES = {
  'significantly above average': 'text-plum-light font-medium',
  'above average': 'text-almond',
  typical: 'text-sandlewood',
  'below average': 'text-sandlewood',
  'significantly below average': 'text-sandlewood/70',
}

function PopulationList({ items, maxItems }) {
  const shown = [...items]
    .sort((a, b) => Math.abs(b.z_score) - Math.abs(a.z_score))
    .slice(0, maxItems)
  return (
    <ul className="flex flex-col gap-1.5">
      {shown.map((item, i) => (
        <motion.li
          key={item.feature}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.05 * i }}
          className="text-xs leading-snug"
        >
          <span className="text-almond">{LABELS[item.feature] ?? item.feature}</span>{' '}
          <span className={ASSESSMENT_STYLES[item.assessment] ?? 'text-sandlewood'}>
            is {item.assessment}
          </span>
          <span className="text-sandlewood/60"> ({item.value} vs. avg {item.population_mean})</span>
        </motion.li>
      ))}
    </ul>
  )
}

function ShapList({ items, maxItems }) {
  const shown = [...items]
    .filter((item) => Math.abs(item.impact) > 0.01)
    .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
    .slice(0, maxItems)
  if (!shown.length) {
    return <p className="text-xs text-sandlewood/60">No single feature dominates this prediction.</p>
  }
  return (
    <ul className="flex flex-col gap-1.5">
      {shown.map((item, i) => (
        <motion.li
          key={item.feature}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.05 * i }}
          className="text-xs leading-snug"
        >
          <span className="text-almond">{LABELS[item.feature] ?? item.feature}</span>{' '}
          <span className={item.direction === 'increases' ? 'text-plum-light font-medium' : 'text-sandlewood'}>
            {item.direction} it
          </span>
          <span className="text-sandlewood/60"> (impact {item.impact > 0 ? '+' : ''}{item.impact})</span>
        </motion.li>
      ))}
    </ul>
  )
}

export default function ReasoningPanel({ title, items, shapItems, maxItems = 4 }) {
  const [mode, setMode] = useState('population')
  if (!items?.length && !shapItems?.length) return null

  return (
    <div className="bg-carbon/40 border border-sandlewood/15 rounded-2xl p-4">
      <div className="flex items-center justify-between mb-2.5">
        <p className="text-sm text-sandlewood">{title}</p>
        {shapItems?.length > 0 && (
          <div className="flex gap-1 text-[11px]">
            <button
              onClick={() => setMode('population')}
              className={`px-2 py-0.5 rounded-full cursor-pointer transition-colors ${
                mode === 'population' ? 'bg-plum text-almond' : 'text-sandlewood hover:text-almond'
              }`}
            >
              vs. average
            </button>
            <button
              onClick={() => setMode('shap')}
              className={`px-2 py-0.5 rounded-full cursor-pointer transition-colors ${
                mode === 'shap' ? 'bg-plum text-almond' : 'text-sandlewood hover:text-almond'
              }`}
            >
              model (SHAP)
            </button>
          </div>
        )}
      </div>
      {mode === 'population' ? (
        <PopulationList items={items ?? []} maxItems={maxItems} />
      ) : (
        <ShapList items={shapItems ?? []} maxItems={maxItems} />
      )}
    </div>
  )
}
