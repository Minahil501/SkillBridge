import { motion } from 'framer-motion'

const CATEGORIES = [
  { label: 'Academic', fields: ['CGPA_normalized', 'Attendance_Percentage'] },
  { label: 'Technical', fields: ['DSA_Score', 'Programming_Score', 'Database_Score', 'WebDev_Score', 'ML_Score', 'Python_Skill', 'JavaScript_Skill'] },
  { label: 'Soft Skills', fields: ['Communication_Score', 'Presentation_Score', 'Problem_Solving_Score', 'Leadership_Score', 'Teamwork_Score', 'Aptitude_Test_Score', 'English_Proficiency_Score'] },
  { label: 'Activity', fields: ['LinkedIn_Profile_Strength', 'Mock_Interview_Score'] },
]

function fieldValue(profile, key) {
  if (key === 'CGPA_normalized') return (Number(profile.CGPA) || 0) * 25
  return Number(profile[key]) || 0
}

export default function CategoryStrengthChart({ profile }) {
  const rows = CATEGORIES.map((cat) => {
    const values = cat.fields.map((f) => fieldValue(profile, f))
    const avg = values.reduce((a, b) => a + b, 0) / values.length
    return { label: cat.label, avg }
  })

  return (
    <div className="bg-carbon/40 border border-sandlewood/15 rounded-2xl p-5">
      <p className="text-sm text-sandlewood mb-4">Category strength</p>
      <div className="flex flex-col gap-3">
        {rows.map((row, i) => (
          <div key={row.label}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-almond">{row.label}</span>
              <span className="text-sandlewood">{Math.round(row.avg)}</span>
            </div>
            <div className="h-2 rounded-full bg-velvet overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-plum-light"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(row.avg, 100)}%` }}
                transition={{ duration: 0.6, delay: i * 0.08, ease: 'easeOut' }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
