import { useEffect, useRef, useState } from "react"
import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Camera,
  Check,
  ChevronDown,
  CloudRain,
  Globe,
  Leaf,
  LogIn,
  Menu,
  ScanLine,
  ShieldCheck,
  Sprout,
  Trees,
  Upload,
  X,
} from "lucide-react"
import { useLanguage } from "../contexts/LanguageContext"
import type { Language } from "../contexts/LanguageContext"
import { ThemeToggle } from "../components/ThemeToggle"
import { useTheme } from "../contexts/ThemeProvider"
import { useClickOutside } from "../hooks/useClickOutside"
import BrandMark from "../components/BrandMark"

const LANGUAGES: { code: Language; label: string }[] = [
  { code: "en", label: "English" },
  { code: "kn", label: "Kannada" },
  { code: "hi", label: "Hindi" },
]

const NAV_ITEMS = [
  { label: "How it works", href: "#how-it-works" },
  { label: "Field tools", href: "#field-tools" },
  { label: "Disease guide", href: "/diseases" },
]

const CONDITIONS = ["Fruit rot / Koleroga", "Yellow leaf", "Anthracnose", "Bud borer"]

const FAQS = [
  {
    question: "What should I photograph?",
    answer: "Take a clear, close photo of the affected leaf, nut bunch, or trunk. Good light and a steady image help the system assess visible symptoms.",
  },
  {
    question: "What happens after I upload a photo?",
    answer: "ArecaVision checks the image and shows a likely condition with supporting details and practical care guidance. Treat it as an early screening aid, and consult a local agronomist when symptoms are severe or unclear.",
  },
  {
    question: "Can I use the site on my phone?",
    answer: "Yes. The scan flow works with a photo from your phone camera or gallery, and the site adapts to smaller screens.",
  },
  {
    question: "Where can I learn about a disease?",
    answer: "Open the disease guide to browse common arecanut conditions, symptoms, and available management advice.",
  },
]

export default function Landing() {
  const { language, setLanguage } = useLanguage()
  const { theme } = useTheme()
  const [languageMenuOpen, setLanguageMenuOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const languageMenuRef = useRef<HTMLDivElement>(null)
  const isDark = theme === "dark" || (theme === "system" && systemDark)
  const landingPalette = {
    "--color-background": isDark ? "#0A1104" : "#F4F3EE",
    "--color-foreground": isDark ? "#DCDCE1" : "#0A1104",
    "--color-surface": isDark ? "#141B11" : "#FCFCF9",
    "--color-card": isDark ? "#141B11" : "#FCFCF9",
    "--color-card-hover": isDark ? "#20291B" : "#E8E9E1",
    "--color-primary": isDark ? "#88A928" : "#2D4C0D",
    "--color-primary-foreground": isDark ? "#0A1104" : "#FFFFFF",
    "--color-secondary": isDark ? "#252920" : "#D3C2B9",
    "--color-accent": "#88A928",
    "--color-muted": isDark ? "#1B2318" : "#E8E9E1",
    "--color-muted-foreground": isDark ? "#A0A2A9" : "#525046",
    "--color-border": isDark ? "#303A2B" : "#D2D3CB",
    "--color-input": isDark ? "#303A2B" : "#D2D3CB",
    "--color-ring": "#88A928",
    "--color-navbar": isDark ? "#0A1104" : "#FCFCF9",
    "--color-footer": isDark ? "#0A1104" : "#FCFCF9",
  } as CSSProperties

  useClickOutside(languageMenuRef, () => setLanguageMenuOpen(false))

  useEffect(() => {
    if (theme !== "system") return
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme])

  function closeMobileMenu() {
    setMobileMenuOpen(false)
  }

  return (
    <div className="min-h-screen bg-background text-foreground" style={landingPalette}>
      <section id="top" className="relative isolate flex min-h-[680px] flex-col overflow-hidden bg-[#0A1104] text-[#DCDCE1] lg:min-h-[760px]">
        <img
          src="/landing/arecavision_hero_v2.png"
          alt="Arecanut grower checking a palm in a plantation"
          className="absolute inset-0 z-0 h-full w-full object-cover object-center"
          fetchPriority="high"
        />
        <div className="absolute inset-0 z-10 bg-[linear-gradient(90deg,rgba(10,17,4,.92)_0%,rgba(10,17,4,.78)_38%,rgba(10,17,4,.24)_100%)]" />
        <div className="absolute inset-x-0 bottom-0 z-10 h-48 bg-gradient-to-t from-[#0A1104]/70 to-transparent" />

        <header className="relative z-30 border-b border-white/10 bg-[#0A1104]/45 backdrop-blur-md">
          <nav aria-label="Main navigation" className="relative mx-auto flex h-[76px] max-w-7xl items-center justify-between gap-4 px-5 sm:px-8">
            <Link to="/" className="flex shrink-0 items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#88A928]">
              <BrandMark size={40} />
              <span>
                <span className="block text-base font-bold tracking-tight text-white">ArecaVision <span className="text-[#A9CF4C]">AI</span></span>
                <span className="block text-[11px] text-white/65">Arecanut crop health</span>
              </span>
            </Link>

            <div className="hidden items-center lg:flex" style={{ columnGap: "2rem" }}>
              {NAV_ITEMS.map((item) => item.href.startsWith("/") ? (
                <Link key={item.href} to={item.href} className="text-sm text-white/75 transition hover:text-white">{item.label}</Link>
              ) : (
                <a key={item.href} href={item.href} className="text-sm text-white/75 transition hover:text-white">{item.label}</a>
              ))}
            </div>

            <div className="flex shrink-0 items-center gap-1 sm:gap-2">
              <div className="relative" ref={languageMenuRef}>
                <button
                  type="button"
                  onClick={() => setLanguageMenuOpen((open) => !open)}
                  className="inline-flex h-9 items-center gap-1.5 rounded-lg px-2 text-xs font-medium text-white/80 hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#88A928] sm:px-2.5"
                  aria-expanded={languageMenuOpen}
                  aria-haspopup="menu"
                  aria-label="Choose language"
                >
                  <Globe size={15} className="text-[#A9CF4C]" />
                  <span className="hidden sm:inline">{LANGUAGES.find((item) => item.code === language)?.label ?? "English"}</span>
                  <ChevronDown size={13} />
                </button>
                {languageMenuOpen && (
                  <div role="menu" className="absolute right-0 top-full mt-2 w-40 rounded-xl border border-border bg-card p-1 text-foreground shadow-xl">
                    {LANGUAGES.map((item) => (
                      <button
                        key={item.code}
                        type="button"
                        role="menuitemradio"
                        aria-checked={language === item.code}
                        onClick={() => {
                          setLanguage(item.code)
                          setLanguageMenuOpen(false)
                        }}
                        className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm hover:bg-muted/70 ${language === item.code ? "font-semibold text-primary" : "text-foreground"}`}
                      >
                        {item.label}
                        {language === item.code && <Check size={14} />}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <ThemeToggle />
              <Link to="/login" className="hidden h-9 items-center gap-1.5 rounded-lg px-2 text-xs font-semibold text-white/85 hover:bg-white/10 sm:inline-flex">
                <LogIn size={15} /> Sign in
              </Link>
              <Link to="/detection" style={{ backgroundColor: "#88A928", color: "#0A1104" }} className="hidden h-10 items-center gap-2 rounded-full px-4 text-xs font-bold transition hover:brightness-110 sm:inline-flex">
                Scan a photo <ArrowUpRight size={15} />
              </Link>
              <button
                type="button"
                aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
                aria-expanded={mobileMenuOpen}
                onClick={() => setMobileMenuOpen((open) => !open)}
                className="flex h-9 w-9 items-center justify-center rounded-lg text-white hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#88A928] lg:hidden"
              >
                {mobileMenuOpen ? <X size={19} /> : <Menu size={19} />}
              </button>
            </div>

            {mobileMenuOpen && (
              <div className="absolute left-4 right-4 top-[68px] rounded-2xl border border-white/10 bg-[#0A1104]/95 p-2 shadow-2xl backdrop-blur-xl lg:hidden">
                {NAV_ITEMS.map((item) => item.href.startsWith("/") ? (
                  <Link key={item.href} to={item.href} onClick={closeMobileMenu} className="block rounded-xl px-4 py-3 text-sm text-white/85 hover:bg-white/10">{item.label}</Link>
                ) : (
                  <a key={item.href} href={item.href} onClick={closeMobileMenu} className="block rounded-xl px-4 py-3 text-sm text-white/85 hover:bg-white/10">{item.label}</a>
                ))}
                <Link to="/login" onClick={closeMobileMenu} className="mt-1 block rounded-xl px-4 py-3 text-sm font-semibold text-[#B8D862] hover:bg-white/10">Sign in</Link>
                <Link to="/detection" onClick={closeMobileMenu} className="mt-1 flex items-center justify-center gap-2 rounded-xl bg-[#88A928] px-4 py-3 text-sm font-bold text-[#0A1104]">Scan a photo <ArrowRight size={16} /></Link>
              </div>
            )}
          </nav>
        </header>

        <div className="relative z-20 mx-auto flex w-full max-w-7xl flex-1 items-center px-5 pb-16 pt-20 sm:px-8 lg:pb-24 lg:pt-24">
          <div className="max-w-2xl">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-[#0A1104]/35 px-3.5 py-2 text-xs font-medium text-white/90 backdrop-blur-sm">
              <span className="h-2 w-2 rounded-full bg-[#A9CF4C]" /> Built for arecanut growers
            </div>
            <h1 className="text-4xl font-semibold leading-[1.08] tracking-[-0.035em] text-white sm:text-6xl lg:text-7xl">
              See your crop clearly.<br />
              <span className="text-[#B7D957]">Know what to do next.</span>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-white/78 sm:text-lg sm:leading-8">
              Check a leaf, nut, or palm with a photo. Get a clear first look at possible problems and practical care guidance for your plantation.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link to="/detection" className="inline-flex h-12 items-center gap-2 rounded-full bg-[#88A928] px-6 text-sm font-bold text-[#0A1104] shadow-lg shadow-black/15 transition hover:bg-[#A2C43C] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[#A9CF4C]/35">
                <Camera size={18} /> Check a photo <ArrowRight size={16} />
              </Link>
              <a href="#how-it-works" className="inline-flex h-12 items-center gap-2 rounded-full border border-white/30 px-5 text-sm font-semibold text-white transition hover:bg-white/10">
                How it works <ArrowDown size={15} />
              </a>
            </div>
            <p className="mt-5 text-xs text-white/65">A phone photo is all you need to get started.</p>
          </div>
        </div>
        <a href="#conditions" className="absolute bottom-6 left-1/2 z-20 hidden -translate-x-1/2 items-center gap-2 text-xs font-medium text-white/65 transition hover:text-white sm:flex">
          Explore ArecaVision <ArrowDown size={14} />
        </a>
      </section>

      <section id="conditions" className="border-b border-white/10 bg-[#0A1104] text-[#DCDCE1]">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-7 sm:px-8 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#A9CF4C]">Know what to look for</p>
            <h2 className="mt-1 text-lg font-medium text-white">Common arecanut concerns</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {CONDITIONS.map((condition) => (
              <span key={condition} className="rounded-full border border-white/15 bg-white/[0.04] px-3.5 py-2 text-xs text-white/80">{condition}</span>
            ))}
            <Link to="/diseases" className="inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-xs font-semibold text-[#B7D957] transition hover:bg-white/10">
              View disease guide <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </section>

      <main>
        <section id="how-it-works" className="bg-background py-16 sm:py-20">
          <div className="mx-auto max-w-7xl px-5 sm:px-8">
            <div className="mb-9 grid gap-4 md:grid-cols-[1fr_360px] md:items-end">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">A simple place to begin</p>
                <h2 className="mt-3 max-w-2xl text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">From a field photo to a clearer next step.</h2>
              </div>
              <p className="max-w-md text-sm leading-6 text-muted-foreground md:justify-self-end">
                Start with what you can see. ArecaVision helps organize the signs and care information around your crop.
              </p>
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              {[
                { icon: Camera, number: "01", title: "Take a photo", text: "Capture the affected leaf, nut bunch, or trunk in clear light." },
                { icon: ScanLine, number: "02", title: "Check the signs", text: "Upload your photo for an AI-assisted crop health assessment." },
                { icon: Sprout, number: "03", title: "Review next steps", text: "Read the likely condition, supporting details, and care guidance." },
              ].map(({ icon: Icon, number, title, text }) => (
                <article key={number} className="group rounded-2xl border border-border bg-card p-5 transition hover:border-primary/40 hover:shadow-lg sm:p-6">
                  <div className="flex items-center justify-between">
                    <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary"><Icon size={20} /></span>
                    <span className="text-sm font-medium tracking-widest text-muted-foreground/60">{number}</span>
                  </div>
                  <h3 className="mt-6 text-lg font-semibold">{title}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{text}</p>
                </article>
              ))}
            </div>
            <div className="mt-7">
              <Link to="/detection" className="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
                Start with a photo <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </section>

        <section id="field-tools" className="bg-[#0A1104] py-16 text-[#DCDCE1] sm:py-20">
          <div className="mx-auto grid max-w-7xl gap-10 px-5 sm:px-8 lg:grid-cols-[1.05fr_.95fr] lg:items-center lg:gap-16">
            <div className="grid grid-cols-2 gap-3 sm:gap-4">
              <figure className="overflow-hidden rounded-2xl border border-white/10 bg-white/5">
                <img src="/samples/sample_anthracnose.jpg" alt="Close view of leaf spots on an arecanut frond" loading="lazy" className="aspect-[4/5] w-full object-cover" />
                <figcaption className="px-3 py-3 text-xs text-white/75 sm:px-4">Leaf symptoms</figcaption>
              </figure>
              <figure className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-white/5 sm:mt-12">
                <img src="/samples/sample_yellow_leaf.jpg" alt="Yellowing frond in an arecanut plantation" loading="lazy" className="aspect-[4/5] w-full object-cover" />
                <figcaption className="px-3 py-3 text-xs text-white/75 sm:px-4">Palm health</figcaption>
              </figure>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#B7D957]">Beyond one scan</p>
              <h2 className="mt-3 text-3xl font-semibold leading-tight tracking-tight text-white sm:text-4xl">Useful field tools, all in one place.</h2>
              <p className="mt-4 max-w-xl text-sm leading-7 text-white/65">
                Keep an eye on crop health over time and find the information you need to plan your next field visit.
              </p>

              <div className="mt-8 space-y-5">
                {[
                  { icon: BookOpen, title: "Disease and care library", text: "Look up common symptoms and management guidance.", to: "/diseases" },
                  { icon: Trees, title: "Plantation overview", text: "Keep blocks and scan history organized.", to: "/map" },
                  { icon: CloudRain, title: "Weather and risk", text: "Review local conditions and disease risk information.", to: "/weather" },
                ].map(({ icon: Icon, title, text, to }) => (
                  <Link key={title} to={to} className="group flex items-start gap-4 rounded-xl py-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#88A928]">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-white/[0.06] text-[#B7D957]"><Icon size={18} /></span>
                    <span className="flex-1">
                      <span className="flex items-center gap-2 text-sm font-semibold text-white">{title}<ArrowUpRight size={14} className="text-white/40 transition group-hover:text-[#B7D957]" /></span>
                      <span className="mt-1 block text-xs leading-5 text-white/55">{text}</span>
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="questions" className="bg-card py-16 sm:py-20">
          <div className="mx-auto grid max-w-7xl gap-10 px-5 sm:px-8 md:grid-cols-[.8fr_1.2fr] md:gap-16">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">Good to know</p>
              <h2 className="mt-3 text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">Questions from the field.</h2>
              <p className="mt-4 max-w-sm text-sm leading-6 text-muted-foreground">A few quick answers before you get started.</p>
              <Link to="/diseases" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
                Browse the disease guide <ArrowRight size={15} />
              </Link>
            </div>
            <div className="divide-y divide-border border-y border-border">
              {FAQS.map((item, index) => (
                <details key={item.question} open={index === 0} className="group py-4">
                  <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-semibold marker:content-none [&::-webkit-details-marker]:hidden">
                    {item.question}
                    <ChevronDown size={17} className="shrink-0 text-muted-foreground transition-transform group-open:rotate-180" />
                  </summary>
                  <p className="max-w-2xl pt-3 pr-8 text-sm leading-6 text-muted-foreground">{item.answer}</p>
                </details>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-border bg-background">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-8 sm:px-8 md:flex-row md:items-center md:justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <BrandMark size={36} />
            <span><span className="block text-sm font-bold">ArecaVision AI</span><span className="block text-xs text-muted-foreground">Arecanut crop health</span></span>
          </Link>
          <div className="flex flex-wrap items-center gap-x-6 gap-y-3 text-xs text-muted-foreground">
            <Link to="/detection" className="hover:text-foreground">Scan a photo</Link>
            <Link to="/diseases" className="hover:text-foreground">Disease guide</Link>
            <Link to="/weather" className="hover:text-foreground">Weather and risk</Link>
            <Link to="/login" className="hover:text-foreground">Sign in</Link>
          </div>
          <span className="text-xs text-muted-foreground">© {new Date().getFullYear()} ArecaVision AI</span>
        </div>
      </footer>
    </div>
  )
}
