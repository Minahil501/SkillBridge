import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { FORM_SECTIONS, EMPTY_PROFILE } from '../data/formSections'
import { SAMPLE_PROFILES } from '../data/samples'

function Field({ field, value, onChange }) {
  if (field.type === 'select') {
    return (
      <label className="flex flex-col gap-1.5">
        <span className="text-sm text-sandlewood">{field.label}</span>
        <select
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          className="bg-velvet border border-sandlewood/30 rounded-lg px-3 py-2.5 text-almond
                     focus:outline-none focus:border-plum-light focus:ring-1 focus:ring-plum-light
                     transition-colors"
        >
          {field.options.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </label>
    )
  }

  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm text-sandlewood">{field.label}</span>
      <input
        type="number"
        min={field.min}
        max={field.max}
        step={field.step}
        value={value}
        onChange={(e) => onChange(field.name, e.target.value)}
        required
        placeholder={`${field.min}–${field.max}`}
        className="bg-velvet border border-sandlewood/30 rounded-lg px-3 py-2.5 text-almond
                   placeholder:text-sandlewood/50
                   focus:outline-none focus:border-plum-light focus:ring-1 focus:ring-plum-light
                   transition-colors"
      />
      {field.helpUrl && (
        <a
          href={field.helpUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-plum-light hover:text-almond transition-colors w-fit"
        >
          {field.helpLabel ?? 'Look it up →'}
        </a>
      )}
    </label>
  )
}

export default function InputForm({ onSubmit }) {
  const [profile, setProfile] = useState(EMPTY_PROFILE)
  const [step, setStep] = useState(0)
  const section = FORM_SECTIONS[step]
  const isLast = step === FORM_SECTIONS.length - 1

  const handleChange = (name, value) => setProfile((p) => ({ ...p, [name]: value }))

  const loadSample = (sample) => {
    setProfile(sample.data)
    setStep(0)
  }

  const handleNext = (e) => {
    e.preventDefault()
    if (isLast) {
      onSubmit(profile)
    } else {
      setStep((s) => s + 1)
    }
  }

  return (
    <div className="w-full max-w-2xl">
      <div className="mb-6">
        <p className="text-sm text-sandlewood mb-2">Try a sample profile</p>
        <div className="flex flex-wrap gap-2">
          {SAMPLE_PROFILES.map((s) => (
            <button
              key={s.key}
              type="button"
              onClick={() => loadSample(s)}
              className="text-sm px-3 py-1.5 rounded-full border border-sandlewood/40 text-almond
                         hover:border-plum-light hover:bg-plum/30 transition-colors cursor-pointer"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 mb-6">
        {FORM_SECTIONS.map((s, i) => (
          <div key={s.key} className="flex-1">
            <div
              className={`h-1.5 rounded-full transition-colors duration-300 ${
                i <= step ? 'bg-plum-light' : 'bg-velvet'
              }`}
            />
            <p className={`mt-2 text-xs ${i === step ? 'text-almond' : 'text-sandlewood/60'}`}>
              {s.title}
            </p>
          </div>
        ))}
      </div>

      <form onSubmit={handleNext}>
        <AnimatePresence mode="wait">
          <motion.div
            key={section.key}
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-carbon/40 border border-sandlewood/15 rounded-2xl p-6"
          >
            {section.fields.map((field) => (
              <Field
                key={field.name}
                field={field}
                value={profile[field.name]}
                onChange={handleChange}
              />
            ))}
          </motion.div>
        </AnimatePresence>

        <div className="flex items-center justify-between mt-6">
          <button
            type="button"
            disabled={step === 0}
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            className="px-4 py-2 rounded-lg text-sandlewood disabled:opacity-30 disabled:cursor-not-allowed
                       hover:text-almond transition-colors cursor-pointer"
          >
            Back
          </button>
          <button
            type="submit"
            className="px-6 py-2.5 rounded-lg bg-plum hover:bg-plum-light text-almond font-medium
                       transition-colors cursor-pointer shadow-lg shadow-plum/20"
          >
            {isLast ? 'Predict my career' : 'Next'}
          </button>
        </div>
      </form>
    </div>
  )
}
