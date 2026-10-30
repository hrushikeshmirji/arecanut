import { FormEvent, useEffect, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import type { CSSProperties } from "react"
import { ArrowLeft, ArrowRight, Eye, EyeOff, Leaf, LoaderCircle, LockKeyhole, Mail } from "lucide-react"
import { useAuth } from "../contexts/AuthContext"
import { useLanguage } from "../contexts/LanguageContext"
import { ThemeToggle } from "../components/ThemeToggle"
import { useTheme } from "../contexts/ThemeProvider"
import loginImage from "../images/image.png"
import BrandMark from "../components/BrandMark"

export default function Login() {
  const { login, isAuthenticated, isLoading } = useAuth()
  const { t } = useLanguage()
  const { theme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")
  const isDemoAuthEnabled = import.meta.env.VITE_DEMO_AUTH === "true"
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const isDark = theme === "dark" || (theme === "system" && systemDark)
  const loginPalette = {
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
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme])

  useEffect(() => {
    if (isAuthenticated) navigate(returnTo, { replace: true })
  }, [isAuthenticated, navigate, returnTo])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")
    setIsSubmitting(true)
    try {
      await login({ email: email.trim(), password })
      navigate(returnTo, { replace: true })
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : t("login.failed_fallback"))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-background text-foreground" style={loginPalette}>
      <header className="relative z-10 flex h-[76px] items-center justify-between border-b border-white/10 bg-[#0A1104] px-5 text-white sm:px-8">
        <Link to="/" className="flex items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">
          <BrandMark size={40} />
          <span>
            <span className="block text-sm font-bold leading-tight text-white">ArecaVision <span className="text-[#A9CF4C]">AI</span></span>
            <span className="block text-[11px] text-white/65">Arecanut crop health</span>
          </span>
        </Link>
        <div className="flex items-center gap-2">
          <Link to="/" className="hidden items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-white/75 transition hover:bg-white/10 hover:text-white sm:inline-flex"><ArrowLeft size={15} /> Home</Link>
          <ThemeToggle />
        </div>
      </header>

      <div className="mx-auto grid min-h-[calc(100vh-76px)] w-full max-w-[1440px] grid-cols-1 lg:grid-cols-2 lg:gap-6 lg:px-6 lg:py-6">
        <section
          aria-label="Arecanut plantation"
          className="relative hidden min-h-[560px] overflow-hidden rounded-[28px] bg-[#10200d] bg-cover bg-[center_44%] lg:flex lg:flex-col lg:justify-end"
          style={{
            backgroundImage: `url('${loginImage}')`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-[#071207]/90 via-[#071207]/25 to-[#071207]/10" />
          <div className="relative z-[1] max-w-2xl p-8 pb-10 sm:p-10 xl:p-14" style={{ padding: "clamp(2rem, 4vw, 3.5rem)" }}>
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-[#0A1104]/40 px-3.5 py-2 text-xs font-medium text-white/90 backdrop-blur-sm"><span className="h-2 w-2 rounded-full bg-[#A9CF4C]" /> Made for arecanut growers</div>
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-[#c0dd65]">A clearer view of your farm</p>
            <h1 className="max-w-xl text-4xl font-semibold leading-[1.12] tracking-tight text-white xl:text-5xl">Good decisions begin with healthy palms.</h1>
            <p className="mt-5 max-w-lg text-base leading-7 text-white/75">Keep crop checks, plantation records, and practical care guidance together in one place.</p>
            <div className="mt-7 flex items-center gap-3 text-sm font-medium text-white/80">
              <span className="flex h-9 w-9 items-center justify-center rounded-full border border-white/25 bg-white/10"><Leaf size={16} /></span>
              Field-ready crop health tools for every growing season
            </div>
          </div>
        </section>

        <section className="flex min-h-[calc(100vh-76px)] items-center justify-center px-5 py-10 sm:px-10 lg:min-h-[560px] lg:px-8 xl:px-14">
          <div className="w-full max-w-[440px] rounded-[24px] border border-border bg-card p-6 shadow-sm sm:p-9">
            <div className="mb-8 lg:mb-10">
              <p className="text-sm font-semibold text-primary">Your plantation workspace</p>
              <h2 className="mt-2 text-3xl font-semibold tracking-tight sm:text-[34px]">Welcome back</h2>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">Sign in to continue to ArecaVision and your farm updates.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="login-email" className="mb-2 block text-sm font-medium">{t("login.email_label", "Email address")}</label>
                <div className="relative">
                  <Mail size={17} aria-hidden="true" className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input id="login-email" name="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder={t("login.email_placeholder", "you@example.com")} className="h-12 w-full rounded-xl border border-input bg-card pl-11 pr-4 text-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10" />
                </div>
              </div>

              <div>
                <label htmlFor="login-password" className="mb-2 block text-sm font-medium">{t("login.password_label", "Password")}</label>
                <div className="relative">
                  <LockKeyhole size={17} aria-hidden="true" className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <input id="login-password" name="password" type={showPassword ? "text" : "password"} autoComplete="current-password" required minLength={6} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="••••••••" className="h-12 w-full rounded-xl border border-input bg-card pl-11 pr-12 text-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10" />
                  <button type="button" onClick={() => setShowPassword((visible) => !visible)} className="absolute right-2 top-1/2 flex h-9 w-9 -translate-y-1/2 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary" aria-label={showPassword ? "Hide password" : "Show password"} aria-pressed={showPassword}>
                    {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                  </button>
                </div>
              </div>

              {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 dark:border-red-900/60 dark:bg-red-950/30 dark:text-red-200">{error}</div>}

              <button type="submit" disabled={isSubmitting || isLoading} className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-sm transition hover:bg-primaryHover focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20 disabled:cursor-not-allowed disabled:opacity-60">
                {isSubmitting || isLoading ? <><LoaderCircle size={17} className="animate-spin" /> {t("login.authenticating", "Signing in…")}</> : <>{t("login.submit_btn", "Sign in")} <ArrowRight size={16} /></>}
              </button>
            </form>

            <div className="mt-5 rounded-xl border border-primary/20 bg-primary/5 p-3.5">
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-semibold">Demo farmer account</p>
                  <p className="mt-1 truncate text-[11px] text-muted-foreground">farmer@arecavision.ai · farmer123</p>
                </div>
                <button type="button" onClick={() => { setEmail("farmer@arecavision.ai"); setPassword("farmer123"); setError("") }} className="shrink-0 rounded-lg border border-primary/25 px-3 py-2 text-[11px] font-semibold text-primary transition hover:bg-primary/10">Use demo</button>
              </div>
            </div>

            {isDemoAuthEnabled && <p className="mt-3 text-center text-[11px] leading-5 text-muted-foreground">Frontend demo access only. This session is stored in this browser and does not authenticate with a server.</p>}

            <div className="mt-7 border-t border-border pt-5 text-center">
              {!isDemoAuthEnabled && <p className="text-xs leading-5 text-muted-foreground">New to ArecaVision? <Link to="/register" className="font-semibold text-primary hover:underline">Create an account</Link></p>}
              <Link to="/" className="mt-4 inline-block text-xs font-semibold text-primary hover:underline">Back to ArecaVision home</Link>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
