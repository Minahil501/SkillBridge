import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import LandingPage from './components/LandingPage'
import InputForm from './components/InputForm'
import ResultView from './components/ResultView'
import InsightsView from './components/InsightsView'
import ChatWidget from './components/ChatWidget'
import Logo from './components/Logo'
import { predictCareer } from './lib/api'

const STATUS = {
  LANDING: 'landing',
  FORM: 'form',
  LOADING: 'loading',
  RESULT: 'result',
  INSIGHTS: 'insights',
  ERROR: 'error',
}

const HEADER_LABEL = {
  [STATUS.RESULT]: 'Your Results',
  [STATUS.INSIGHTS]: 'Insights',
}

export default function App() {
  const [status, setStatus] = useState(STATUS.LANDING)
  const [profile, setProfile] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (submittedProfile) => {
    setProfile(submittedProfile)
    setStatus(STATUS.LOADING)
    try {
      const data = await predictCareer(submittedProfile)
      setResult(data)
      setStatus(STATUS.RESULT)
    } catch (err) {
      setError(err.message)
      setStatus(STATUS.ERROR)
    }
  }

  const reset = () => {
    setResult(null)
    setError(null)
    setStatus(STATUS.FORM)
  }

  return (
    <div className="min-h-screen bg-carbon text-almond flex flex-col items-center px-4 py-12">
      {status !== STATUS.LANDING && (
        <header className="w-full max-w-6xl flex items-center justify-between mb-8">
          <button
            onClick={() => setStatus(STATUS.LANDING)}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <span className="group-hover:scale-110 transition-transform">
              <Logo size={28} />
            </span>
            <span className="text-2xl font-semibold text-almond tracking-tight">SkillBridge</span>
          </button>
          {HEADER_LABEL[status] && (
            <span className="text-sm text-sandlewood uppercase tracking-wide">{HEADER_LABEL[status]}</span>
          )}
        </header>
      )}

      {status === STATUS.FORM && (
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-semibold text-almond">
            Where do your skills point?
          </h1>
          <p className="text-sandlewood mt-3 max-w-md mx-auto">
            Fill in a student profile to get an employability score and recommended career path.
          </p>
        </div>
      )}

      <main className="w-full flex flex-col items-center flex-1">
        <AnimatePresence mode="wait">
          {status === STATUS.LANDING && (
            <motion.div key="landing" exit={{ opacity: 0 }} className="w-full flex justify-center">
              <LandingPage onStart={() => setStatus(STATUS.FORM)} />
            </motion.div>
          )}

          {status === STATUS.FORM && (
            <motion.div key="form" exit={{ opacity: 0 }} className="w-full flex justify-center">
              <InputForm onSubmit={handleSubmit} />
            </motion.div>
          )}

          {status === STATUS.LOADING && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4 py-24"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                className="w-10 h-10 rounded-full border-2 border-sandlewood/30 border-t-plum-light"
              />
              <p className="text-sandlewood">Running the model…</p>
            </motion.div>
          )}

          {status === STATUS.RESULT && result && (
            <motion.div key="result" exit={{ opacity: 0 }} className="w-full flex justify-center">
              <ResultView
                result={result}
                profile={profile}
                onReset={reset}
                onViewInsights={() => setStatus(STATUS.INSIGHTS)}
              />
            </motion.div>
          )}

          {status === STATUS.INSIGHTS && result && (
            <motion.div key="insights" exit={{ opacity: 0 }} className="w-full flex justify-center">
              <InsightsView result={result} onBack={() => setStatus(STATUS.RESULT)} />
            </motion.div>
          )}

          {status === STATUS.ERROR && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-4 py-16 max-w-md text-center"
            >
              <div className="w-12 h-12 rounded-full bg-plum/30 flex items-center justify-center text-plum-light text-xl">
                !
              </div>
              <p className="text-almond font-medium">Couldn't reach the prediction API</p>
              <p className="text-sandlewood text-sm">{error}</p>
              <button
                onClick={reset}
                className="mt-2 px-5 py-2 rounded-lg bg-plum hover:bg-plum-light text-almond transition-colors cursor-pointer"
              >
                Try again
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {(status === STATUS.RESULT || status === STATUS.INSIGHTS) && result && (
        <ChatWidget result={result} />
      )}

      <footer className="mt-16 text-sandlewood/60 text-xs">
        © {new Date().getFullYear()} Minahil Kamran. All rights reserved.
      </footer>
    </div>
  )
}
