import { motion } from 'framer-motion'
import ScoreGauge from './ScoreGauge'
import CareerBarChart from './CareerBarChart'
import SkillRadarChart from './SkillRadarChart'
import CategoryStrengthChart from './CategoryStrengthChart'
import EngineeredScoresPanel from './EngineeredScoresPanel'

export default function ResultView({ result, profile, onReset, onViewInsights }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="w-full max-w-6xl flex flex-col items-center gap-5"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 w-full items-start">
        {/* Row 1 — headline visuals, roughly equal height */}
        <div className="lg:col-span-4 bg-carbon/40 border border-sandlewood/15 rounded-2xl p-5 flex flex-col items-center gap-3">
          <ScoreGauge score={result.employability_score} />
          {result.employability_range && (
            <p className="text-sandlewood text-xs -mt-3">
              Likely range: {result.employability_range[0]} – {result.employability_range[1]}
            </p>
          )}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.3 }}
            className="flex flex-col items-center gap-1.5"
          >
            <span className="text-xs text-sandlewood uppercase tracking-wide">Recommended career</span>
            <span className="px-4 py-1.5 rounded-full bg-plum text-almond text-base font-medium text-center">
              {result.recommended_career_path}
            </span>
            {typeof result.confidence === 'number' && (
              <span className="text-sandlewood text-xs">
                {Math.round(result.confidence * 100)}% model confidence
              </span>
            )}
          </motion.div>
        </div>

        {result.career_probabilities && (
          <div className="lg:col-span-4">
            <CareerBarChart
              probabilities={result.career_probabilities}
              topCareer={result.recommended_career_path}
            />
          </div>
        )}

        {profile && (
          <div className="lg:col-span-4">
            <SkillRadarChart profile={profile} />
          </div>
        )}

        {/* Row 2 — supporting detail */}
        {profile && (
          <div className="lg:col-span-6">
            <CategoryStrengthChart profile={profile} />
          </div>
        )}

        {result.engineered_features && (
          <div className="lg:col-span-6">
            <EngineeredScoresPanel scores={result.engineered_features} />
          </div>
        )}
      </div>

      <motion.button
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        onClick={onViewInsights}
        className="w-full max-w-2xl flex items-center justify-between px-6 py-4 rounded-2xl
                   bg-plum/20 border border-plum-light/40 hover:border-plum-light hover:bg-plum/30
                   transition-colors cursor-pointer text-left"
      >
        <span>
          <span className="block text-almond font-medium">Why this result, and what to do next</span>
          <span className="block text-sandlewood text-sm mt-0.5">
            Reasoning, model attribution, and personalized recommendations
          </span>
        </span>
        <span className="text-plum-light text-xl">→</span>
      </motion.button>

      <button
        onClick={onReset}
        className="px-5 py-2 rounded-lg border border-sandlewood/40 text-sandlewood
                   hover:text-almond hover:border-plum-light transition-colors cursor-pointer"
      >
        Try another profile
      </button>
    </motion.div>
  )
}
