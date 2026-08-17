import { motion } from 'framer-motion'
import ReasoningPanel from './ReasoningPanel'
import RecommendationsSection from './RecommendationsSection'
import ShapWaterfallChart from './ShapWaterfallChart'

export default function InsightsView({ result, onBack }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="w-full max-w-6xl flex flex-col items-center gap-5"
    >
      <button
        onClick={onBack}
        className="self-start text-sm text-sandlewood hover:text-almond transition-colors cursor-pointer"
      >
        ← Back to results
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 w-full items-start">
        {result.reasoning && (
          <div className="lg:col-span-12">
            <RecommendationsSection
              reasoning={result.reasoning}
              probabilities={result.career_probabilities}
              topCareer={result.recommended_career_path}
            />
          </div>
        )}

        {result.reasoning && (
          <div className="lg:col-span-6">
            <ReasoningPanel
              title="Why this employability score"
              items={result.reasoning.employability}
              shapItems={result.shap_reasoning?.employability}
            />
          </div>
        )}
        {result.reasoning && (
          <div className="lg:col-span-6">
            <ReasoningPanel
              title="Why this career match"
              items={result.reasoning.career}
              shapItems={result.shap_reasoning?.career}
            />
          </div>
        )}

        {result.shap_waterfall?.employability && (
          <div className="lg:col-span-6">
            <ShapWaterfallChart
              title="Employability score — model attribution"
              note="How each signal moves the XGBoost model's raw estimate from its baseline. (One of three ensemble members — an indicative view, not the exact final blended score.)"
              waterfall={result.shap_waterfall.employability}
            />
          </div>
        )}
        {result.shap_waterfall?.career && (
          <div className="lg:col-span-6">
            <ShapWaterfallChart
              title="Career match — model attribution"
              note="Same idea, for the recommended career's raw model score (not a probability)."
              waterfall={result.shap_waterfall.career}
            />
          </div>
        )}
      </div>
    </motion.div>
  )
}
