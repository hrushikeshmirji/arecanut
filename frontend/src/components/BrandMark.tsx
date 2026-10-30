interface BrandMarkProps {
  size?: number
  className?: string
}

export default function BrandMark({ size = 40, className = "" }: BrandMarkProps) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      className={`shrink-0 ${className}`}
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="48" height="48" rx="14" fill="#88A928" />
      <path d="M24 37V20" stroke="#0A1104" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M24 21C18.8 14.9 12.7 12.3 7 13.4C10.1 19.5 15.6 22.2 24 23" fill="#0A1104" />
      <path d="M24 21C29.2 14.9 35.3 12.3 41 13.4C37.9 19.5 32.4 22.2 24 23" fill="#0A1104" />
      <path d="M23.5 20.5C21.9 13.8 18.7 9.5 14 7.5C13.6 13.7 16.6 18.2 23.5 22.3" fill="#0A1104" />
      <path d="M24.5 20.5C26.1 13.8 29.3 9.5 34 7.5C34.4 13.7 31.4 18.2 24.5 22.3" fill="#0A1104" />
      <circle cx="20" cy="28" r="2.4" fill="#F4F3EE" />
      <circle cx="24" cy="30.5" r="2.6" fill="#F4F3EE" />
      <circle cx="28" cy="28" r="2.4" fill="#F4F3EE" />
    </svg>
  )
}
