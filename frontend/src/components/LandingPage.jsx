import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Logo from './Logo'

const CAREERS = [
  'Machine Learning Engineer',
  'Web Developer',
  'Data Analyst',
  'Software Engineer',
  'UI/UX Designer',
  'Cybersecurity Analyst',
]

function useCycling(items, intervalMs) {
  const [index, setIndex] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setIndex((i) => (i + 1) % items.length), intervalMs)
    return () => clearInterval(id)
  }, [items.length, intervalMs])
  return items[index]
}

function OrbitMotif() {
  const rings = [50, 85, 120]
  const nodes = [
    [0, -120], [104, -60], [104, 60], [0, 120], [-104, 60], [-104, -60],
  ]
  return (
    <div className="relative w-64 h-64 sm:w-80 sm:h-80">
      <svg viewBox="-140 -140 280 280" className="w-full h-full overflow-visible">
        {rings.map((r) => (
          <circle key={r} cx="0" cy="0" r={r} fill="none" stroke="var(--color-sandlewood)" strokeOpacity="0.18" strokeWidth="1" />
        ))}
        {nodes.map(([x, y], i) => (
          <line key={i} x1="0" y1="0" x2={x} y2={y} stroke="var(--color-sandlewood)" strokeOpacity="0.18" strokeWidth="1" />
        ))}
        <motion.polygon
          points={nodes.map((p) => p.join(',')).join(' ')}
          fill="var(--color-plum-light)"
          fillOpacity="0.25"
          stroke="var(--color-plum-light)"
          strokeWidth="1.5"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 40, ease: 'linear' }}
          style={{ transformOrigin: '0px 0px' }}
        />
        {nodes.map(([x, y], i) => (
          <motion.circle
            key={i}
            cx={x}
            cy={y}
            r="4"
            fill="var(--color-almond)"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ repeat: Infinity, duration: 3, delay: i * 0.4, ease: 'easeInOut' }}
          />
        ))}
      </svg>
    </div>
  )
}

export default function LandingPage({ onStart }) {
  const career = useCycling(CAREERS, 2200)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col lg:flex-row items-center gap-4 lg:gap-16 max-w-5xl w-full py-16"
    >
      <div className="flex-1 text-center lg:text-left">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center justify-center lg:justify-start gap-3 mb-6"
        >
          <Logo size={44} />
          <span className="text-3xl sm:text-4xl font-semibold text-almond tracking-tight">
            SkillBridge
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          className="text-4xl sm:text-5xl font-semibold text-almond tracking-tight leading-[1.1]"
        >
          Are you headed towards
        </motion.h1>

        <div className="min-h-14 sm:min-h-18 flex items-center justify-center lg:justify-start py-1">
          <AnimatePresence mode="wait">
            <motion.h1
              key={career}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.35 }}
              className="text-2xl sm:text-3xl font-semibold text-plum-light tracking-tight leading-tight"
            >
              {career}?
            </motion.h1>
          </AnimatePresence>
        </div>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-sandlewood mt-5 max-w-md mx-auto lg:mx-0 text-lg"
        >
          Feed in your academic and technical profile — get an employability score,
          a career match, and a plan to close the gap between them.
        </motion.p>

        <motion.button
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45, duration: 0.5 }}
          onClick={onStart}
          className="mt-8 px-8 py-3.5 rounded-full bg-plum hover:bg-plum-light text-almond font-medium text-lg
                     shadow-lg shadow-plum/30 transition-colors cursor-pointer"
        >
          Get Started
        </motion.button>
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.85 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="hidden sm:flex flex-1 justify-center"
      >
        <OrbitMotif />
      </motion.div>
    </motion.div>
  )
}
