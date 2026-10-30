import { FormEvent, useEffect, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import type { CSSProperties } from "react"
import { ArrowLeft, ArrowRight, Eye, EyeOff, Leaf, LoaderCircle, LockKeyhole, Mail, UserRound } from "lucide-react"
import { useAuth } from "../contexts/AuthContext"
import { ThemeToggle } from "../components/ThemeToggle"
import { useTheme } from "../contexts/ThemeProvider"
import registerImage from "../images/image.png"
import BrandMark from "../components/BrandMark"

export default function Register() {
  const { register, isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [name, setName] = useState("")
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")
  const { theme } = useTheme()
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const isDark = theme === "dark" || (theme === "system" && systemDark)
  const palette = {
    "--color-background": isDark ? "#0A1104" : "#F4F3EE",
    "--color-foreground": isDark ? "#DCDCE1" : "#0A1104",
    "--color-surface": isDark ? "#141B11" : "#FCFCF9",
    "--color-card": isDark ? "#141B11" : "#FCFCF9",
    "--color-muted": isDark ? "#1B2318" : "#E8E9E1",
    "--color-muted-foreground": isDark ? "#A0A2A9" : "#525046",
    "--color-border": isDark ? "#303A2B" : "#D2D3CB",
    "--color-input": isDark ? "#303A2B" : "#D2D3CB",
    "--color-primary": isDark ? "#88A928" : "#2D4C0D",
    "--color-primary-foreground": isDark ? "#0A1104" : "#FFFFFF",
    "--color-accent": "#88A928",
    "--color-ring": "#88A928",
  } as CSSProperties
  const returnTo = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || "/dashboard"

  useEffect(() => {
    if (theme !== "system") return
    const media = window.matchMedia("(prefers-color-scheme: dark)")
    const onChange = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    media.addEventListener("change", onChange)
    return () => media.removeEventListener("change", onChange)
  }, [theme])

  useEffect(() => {
    if (isAuthenticated) navigate(returnTo, { replace: true })
  }, [isAuthenticated, navigate, returnTo])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")
    if (password !== confirmPassword) return setError("Passwords do not match.")
    setSubmitting(true)
    try {
      await register({ name: name.trim(), username: username.trim(), email: email.trim(), password })
      navigate(returnTo, { replace: true })
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to create your account.")
    } finally {
      setSubmitting(false)
    }
  }

  const inputClass = "h-11 w-full rounded-xl border border-input bg-card px-3.5 text-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"

  return (
    <main className="min-h-screen bg-background text-foreground" style={palette}>
      <header className="relative z-10 flex h-[76px] items-center justify-between border-b border-white/10 bg-[#0A1104] px-5 text-white sm:px-8">
        <Link to="/" className="flex items-center gap-3"><BrandMark size={40} /><span><span className="block text-sm font-bold text-white">ArecaVision <span className="text-[#A9CF4C]">AI</span></span><span className="block text-[11px] text-white/65">Arecanut crop health</span></span></Link>
        <div className="flex items-center gap-2"><Link to="/" className="hidden items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-white/75 hover:bg-white/10 sm:inline-flex"><ArrowLeft size={15} /> Home</Link><ThemeToggle /></div>
      </header>
      <div className="mx-auto grid min-h-[calc(100vh-76px)] w-full max-w-[1440px] grid-cols-1 lg:grid-cols-2 lg:gap-6 lg:px-6 lg:py-6">
        <section aria-label="Arecanut plantation" className="relative hidden min-h-[560px] overflow-hidden rounded-[28px] bg-[#10200d] bg-cover bg-center lg:flex lg:flex-col lg:justify-end" style={{ backgroundImage: `url('${registerImage}')`, backgroundSize: "cover", backgroundRepeat: "no-repeat" }}>
          <div className="absolute inset-0 bg-gradient-to-t from-[#071207]/90 via-[#071207]/25 to-[#071207]/10" />
          <div className="relative z-[1] p-10 xl:p-14"><div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-[#0A1104]/40 px-3.5 py-2 text-xs text-white/90 backdrop-blur-sm"><span className="h-2 w-2 rounded-full bg-[#A9CF4C]" /> Made for arecanut growers</div><p className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-[#c0dd65]">A clearer view of your farm</p><h1 className="max-w-xl text-4xl font-semibold leading-tight tracking-tight text-white xl:text-5xl">A healthier season starts with a closer look.</h1><p className="mt-5 max-w-lg text-base leading-7 text-white/75">Keep crop checks, plantation records, and practical care guidance together in one place.</p><div className="mt-7 flex items-center gap-3 text-sm font-medium text-white/80"><span className="flex h-9 w-9 items-center justify-center rounded-full border border-white/25 bg-white/10"><Leaf size={16} /></span> Field-ready crop health tools for every growing season</div></div>
        </section>
        <section className="flex items-center justify-center px-5 py-8 sm:px-10 lg:px-8 xl:px-14">
          <div className="w-full max-w-[460px] rounded-[24px] border border-border bg-card p-6 shadow-sm sm:p-9">
            <div className="mb-6"><p className="text-sm font-semibold text-primary">Your plantation workspace</p><h2 className="mt-2 text-3xl font-semibold tracking-tight">Create your account</h2><p className="mt-2 text-sm leading-6 text-muted-foreground">Join ArecaVision to keep your crop health information in one place.</p></div>
            <form onSubmit={handleSubmit} className="space-y-3.5">
              <label className="block text-sm font-medium">Full name<input autoComplete="name" required maxLength={80} value={name} onChange={e => setName(e.target.value)} placeholder="Your name" className={`${inputClass} mt-1.5`} /></label>
              <label className="block text-sm font-medium">Username<div className="relative mt-1.5"><UserRound size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" /><input autoComplete="username" required minLength={3} maxLength={32} pattern="[A-Za-z0-9._-]+" title="Use letters, numbers, dots, underscores, or hyphens" value={username} onChange={e => setUsername(e.target.value)} placeholder="Choose a username" className={`${inputClass} pl-10`} /></div></label>
              <label className="block text-sm font-medium">Email address<div className="relative mt-1.5"><Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" /><input type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" className={`${inputClass} pl-10`} /></div></label>
              <label className="block text-sm font-medium">Password<div className="relative mt-1.5"><LockKeyhole size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" /><input type={showPassword ? "text" : "password"} autoComplete="new-password" required minLength={6} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 6 characters" className={`${inputClass} pl-10 pr-11`} /><button type="button" onClick={() => setShowPassword(v => !v)} aria-label={showPassword ? "Hide password" : "Show password"} className="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted">{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}</button></div></label>
              <label className="block text-sm font-medium">Confirm password<input type={showPassword ? "text" : "password"} autoComplete="new-password" required minLength={6} value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} placeholder="Re-enter your password" className={`${inputClass} mt-1.5`} /></label>
              {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-200">{error}</div>}
              <button type="submit" disabled={submitting || isLoading} className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-sm transition hover:bg-primaryHover disabled:opacity-60">{submitting || isLoading ? <><LoaderCircle size={17} className="animate-spin" /> Creating account…</> : <>Create account <ArrowRight size={16} /></>}</button>
            </form>
            <div className="mt-6 border-t border-border pt-5 text-center text-sm text-muted-foreground">Already have an account? <Link to="/login" className="font-semibold text-primary hover:underline">Sign in</Link></div>
          </div>
        </section>
      </div>
    </main>
  )
}
