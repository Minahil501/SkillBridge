// Field definitions grouped to match backend/main.py::InputData exactly (key names + order matter).

export const FORM_SECTIONS = [
  {
    key: 'academic',
    title: 'Academic',
    fields: [
      { name: 'Age', label: 'Age', type: 'number', min: 17, max: 35, step: 1 },
      { name: 'Semester', label: 'Semester', type: 'number', min: 1, max: 8, step: 1 },
      { name: 'CGPA', label: 'CGPA', type: 'number', min: 0, max: 4, step: 0.01 },
      { name: 'Attendance_Percentage', label: 'Attendance %', type: 'number', min: 0, max: 100, step: 0.1 },
    ],
  },
  {
    key: 'technical',
    title: 'Technical Skills',
    fields: [
      { name: 'DSA_Score', label: 'DSA Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Programming_Score', label: 'Programming Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Database_Score', label: 'Database Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'WebDev_Score', label: 'Web Dev Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'ML_Score', label: 'ML Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Python_Skill', label: 'Python Skill', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'JavaScript_Skill', label: 'JavaScript Skill', type: 'number', min: 0, max: 100, step: 0.1 },
      {
        name: 'Project_Complexity',
        label: 'Project Complexity',
        type: 'select',
        options: ['Low', 'Medium', 'High'],
      },
      { name: 'Technical_Skill_Index', label: 'Technical Skill Index', type: 'number', min: 0, max: 10, step: 0.1 },
    ],
  },
  {
    key: 'soft',
    title: 'Soft Skills',
    fields: [
      { name: 'Communication_Score', label: 'Communication Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Presentation_Score', label: 'Presentation Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Problem_Solving_Score', label: 'Problem Solving Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Leadership_Score', label: 'Leadership Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Teamwork_Score', label: 'Teamwork Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Aptitude_Test_Score', label: 'Aptitude Test Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'English_Proficiency_Score', label: 'English Proficiency', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Soft_Skill_Index', label: 'Soft Skill Index', type: 'number', min: 0, max: 10, step: 0.1 },
    ],
  },
  {
    key: 'activity',
    title: 'Activity & Experience',
    fields: [
      { name: 'Projects_Count', label: 'Projects Completed', type: 'number', min: 0, max: 20, step: 1 },
      { name: 'Certifications_Count', label: 'Certifications', type: 'number', min: 0, max: 15, step: 1 },
      { name: 'Hackathons_Participated', label: 'Hackathons Participated', type: 'number', min: 0, max: 15, step: 1 },
      { name: 'Internship_Experience', label: 'Internship Experience (yrs)', type: 'number', min: 0, max: 5, step: 0.1 },
      {
        name: 'GitHub_Repo_Count',
        label: 'GitHub Repos',
        type: 'number',
        min: 0,
        max: 100,
        step: 1,
        helpUrl: 'https://github.com/settings/repositories',
        helpLabel: "Don't know your count? Check it on GitHub →",
      },
      {
        name: 'LinkedIn_Profile_Strength',
        label: 'LinkedIn Profile Strength',
        type: 'number',
        min: 0,
        max: 100,
        step: 0.1,
        helpUrl: 'https://revscale.com/free-tools/linkedin-profile-score',
        helpLabel: "Don't know your score? Check it here →",
      },
      { name: 'Volunteer_Activities', label: 'Volunteer Activities', type: 'number', min: 0, max: 10, step: 1 },
      { name: 'Research_Papers', label: 'Research Papers', type: 'number', min: 0, max: 10, step: 1 },
      { name: 'Workshops_Attended', label: 'Workshops Attended', type: 'number', min: 0, max: 15, step: 1 },
      { name: 'Coding_Contest_Rating', label: 'Coding Contest Rating', type: 'number', min: 0, max: 3000, step: 1 },
      { name: 'Mock_Interview_Score', label: 'Mock Interview Score', type: 'number', min: 0, max: 100, step: 0.1 },
      { name: 'Experience_Index', label: 'Experience Index', type: 'number', min: 0, max: 3, step: 0.01 },
    ],
  },
]

export const ALL_FIELDS = FORM_SECTIONS.flatMap((s) => s.fields)

export const EMPTY_PROFILE = Object.fromEntries(
  ALL_FIELDS.map((f) => [f.name, f.type === 'select' ? f.options[0] : ''])
)
