import { motion } from 'framer-motion'
import { LABELS } from '../data/topFeatures'

const SUGGESTIONS = {
  Python_Skill: 'Strengthen Python fundamentals — build a couple of small projects that use it end to end.',
  DSA_Score: 'Practice data structures & algorithms problems regularly; this is a heavily-weighted signal.',
  Technical_Skill_Index: 'Round out your technical breadth — pick up a skill outside your current comfort zone.',
  JavaScript_Skill: 'Build something with JavaScript — even a small interactive page moves this number.',
  ML_Score: 'Work through an applied ML project (not just theory) to lift this score.',
  Web_JS_Synergy: 'Pair a web project with heavier JavaScript use to build this synergy.',
  DS_Python_Synergy: 'Combine a data/ML task with Python scripting to build this synergy.',
  SE_Core_Strength: 'Focus on core software engineering fundamentals — DSA plus solid programming practice.',
  DA_Core_Strength: 'Practice database work — schema design, queries — alongside Python.',
  Comm_Tech_Ratio: 'Balance your technical work with communication practice — presentations, writing, teamwork.',
  Project_Complexity_Enc: 'Take on a more complex project — more moving parts, more depth.',
  Tech_Soft_Product: 'Grow both technical and soft skills together — this reflects their combined strength.',
  Programming_Score: 'Keep coding regularly — consistent practice moves this the most.',
}

function collectWeakSpots(reasoning) {
  const all = [...reasoning.employability, ...reasoning.career]
  const seen = new Map()
  for (const item of all) {
    if (item.assessment.includes('below average') && !seen.has(item.feature)) {
      seen.set(item.feature, item)
    }
  }
  return [...seen.values()].sort((a, b) => a.z_score - b.z_score).slice(0, 3)
}

export default function RecommendationsSection({ reasoning, probabilities, topCareer }) {
  const weakSpots = collectWeakSpots(reasoning)
  const ranked = Object.entries(probabilities ?? {}).sort((a, b) => b[1] - a[1])
  const runnerUp = ranked.find(([name]) => name !== topCareer)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="w-full bg-carbon/40 border border-sandlewood/15 rounded-2xl p-5"
    >
      <p className="text-sm text-sandlewood mb-3">Recommendations</p>
      {weakSpots.length > 0 ? (
        <ul className="flex flex-col gap-2 mb-3">
          {weakSpots.map((item) => (
            <li key={item.feature} className="text-sm text-almond flex gap-2">
              <span className="text-plum-light shrink-0">→</span>
              {SUGGESTIONS[item.feature] ?? `Improve ${LABELS[item.feature] ?? item.feature}.`}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-almond mb-3">
          Your top-weighted signals are all at or above average — a strong, well-rounded profile.
        </p>
      )}
      {runnerUp && (
        <p className="text-sm text-sandlewood">
          Also worth exploring: <span className="text-almond">{runnerUp[0]}</span>{' '}
          ({Math.round(runnerUp[1] * 100)}% match) is your next-closest fit.
        </p>
      )}
    </motion.div>
  )
}
