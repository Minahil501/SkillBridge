export default function Logo({ size = 40 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none" aria-hidden="true">
      <path
        d="M6 30 Q24 8 42 30"
        stroke="var(--color-plum-light)"
        strokeWidth="3"
        strokeLinecap="round"
      />
      <path d="M6 30 L6 38" stroke="var(--color-sandlewood)" strokeWidth="3" strokeLinecap="round" />
      <path d="M42 30 L42 38" stroke="var(--color-sandlewood)" strokeWidth="3" strokeLinecap="round" />
      <circle cx="6" cy="30" r="4.5" fill="var(--color-almond)" />
      <circle cx="42" cy="30" r="4.5" fill="var(--color-plum-light)" />
      <circle cx="24" cy="13" r="3" fill="var(--color-almond)" />
    </svg>
  )
}
