import React, { useState, useEffect, useRef } from "react"
import type { CSSProperties } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts"
import {
  TreePine,
  Heart,
  AlertTriangle,
  ScanLine,
  Bell,
  Upload,
  ChevronRight,
  Thermometer,
  Droplets,
  Wind,
  CloudRain,
  ShieldAlert,
  X,
  RefreshCw,
  ArrowRight,
  Calculator,
  Activity,
  CheckCircle2,
  Leaf,
} from "lucide-react"
import { useScanHistory } from "../contexts/ScanHistoryContext"
import { useNotifications } from "../contexts/NotificationContext"
import { usePlantation } from "../contexts/PlantationContext"
import { fetchDiseaseTrends } from "../services/dashboardService"
import { DiseaseTrendItem } from "../types/api"
import { useWeather } from "../contexts/WeatherContext"
import { useLanguage } from "../contexts/LanguageContext"
import { THEME_TOKENS } from "../theme/tokens"
import TreatmentCalculatorModal from "../components/TreatmentCalculatorModal"
import { fetchRiskForecast, RiskForecastData } from "../services/weatherService"
import { formatDiseaseName } from "../utils/imageFallback"
import { useTheme } from "../contexts/ThemeProvider"
import dashboardPhoto from "../images/image.png"

const trendLegend = [
  { label: "Anthracnose", color: THEME_TOKENS.charts.lines.anthracnose },
  { label: "Fruit Rot (Koleroga)", color: THEME_TOKENS.charts.lines.fruitRot },
  { label: "Nut Cracking", color: THEME_TOKENS.charts.lines.nutCracking },
  { label: "Sooty Mold", color: THEME_TOKENS.charts.lines.sootyMold },
]

interface TooltipPayloadItem {
  name: string
  value: number | string
  color?: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: TooltipPayloadItem[]
  label?: string
}

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (active && payload?.length) {
    return (
      <div className="bg-card rounded-xl shadow-xl border border-border px-3.5 py-2.5 text-xs">
        <p className="font-bold text-foreground mb-1.5">{label}</p>
        <div className="space-y-1">
          {payload.map((p) => (
            <div key={p.name} className="flex items-center justify-between gap-3 text-[11px]">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
                {p.name}
              </span>
              <span className="font-mono font-bold text-foreground">{p.value}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }
  return null
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { t } = useLanguage()
  const { theme } = useTheme()
  const { scans } = useScanHistory()
  const { notifications, unreadCount } = useNotifications()
  const { totalTrees, healthyTrees, diseasedTrees, topDiseasedBlocks, overallHealthScore } = usePlantation()
  const { weatherState, refreshLocationWeather } = useWeather()

  const [riskForecast, setRiskForecast] = useState<RiskForecastData | null>(null)
  const [showCalculator, setShowCalculator] = useState(false)
  const [isAlertDismissed, setIsAlertDismissed] = useState(false)
  const [trendData, setTrendData] = useState<DiseaseTrendItem[]>([])
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const isDark = theme === "dark" || (theme === "system" && systemDark)
  const dashboardPalette = {
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

  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (theme !== "system") return
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme])

  useEffect(() => {
    fetchRiskForecast()
      .then((res) => {
        if (res) setRiskForecast(res)
      })
      .catch(() => undefined)
  }, [])

  useEffect(() => {
    let isMounted = true
    if (scans.length > 0) {
      fetchDiseaseTrends()
        .then((data) => {
          if (isMounted) setTrendData(data)
        })
        .catch((err) => {
          console.error("Failed to load disease trends:", err)
        })
    } else {
      setTrendData([])
    }
    return () => {
      isMounted = false
    }
  }, [scans.length])

  // Handle Quick Photo Launch: Reads file and seamlessly passes it into the AI Detection studio
  const handleQuickPhotoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      const reader = new FileReader()
      reader.onload = (event) => {
        if (typeof event.target?.result === "string") {
          navigate("/detection", { state: { imageUrl: event.target.result } })
        }
      }
      reader.readAsDataURL(file)
    }
  }

  // Calculate high-level health metrics
  const displayTotal = totalTrees > 0 ? totalTrees : 12540
  const displayHealthy = healthyTrees > 0 ? healthyTrees : 10312
  const displayDiseased = diseasedTrees > 0 ? diseasedTrees : 2228
  const healthPercent = overallHealthScore ?? Math.round((displayHealthy / displayTotal) * 100)

  // 4 Core Executive KPI Cards
  const kpiCards = [
    {
      id: "health",
      label: t("dash.kpi.overall_health", "Plantation Health"),
      value: `${healthPercent}%`,
      sub: `${displayHealthy.toLocaleString()} of ${displayTotal.toLocaleString()} palms optimal`,
      icon: Heart,
      iconBg: "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400",
      accent: "text-emerald-600 dark:text-emerald-400",
      progress: healthPercent,
      onClick: () => navigate("/map"),
    },
    {
      id: "diseased",
      label: t("dash.kpi.under_care", "Infection Watch"),
      value: displayDiseased.toLocaleString(),
      sub: t("dash.kpi.flagged_care", "palms requiring targeted spray"),
      icon: AlertTriangle,
      iconBg: "bg-amber-500/10 border-amber-500/20 text-amber-600 dark:text-amber-400",
      accent: "text-amber-600 dark:text-amber-400",
      onClick: () => navigate("/map"),
    },
    {
      id: "risk",
      label: t("dash.kpi.threat_index", "Pathogen Spore Risk"),
      value: `${riskForecast?.compositeIndex ?? 28}%`,
      sub: riskForecast?.overallSeverity ? `${riskForecast.overallSeverity} risk profile` : "Microclimate active",
      icon: ShieldAlert,
      iconBg: "bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400",
      accent: "text-rose-600 dark:text-rose-400",
      onClick: () => navigate("/weather"),
    },
    {
      id: "alerts",
      label: t("dash.kpi.action_items", "Active Field Alerts"),
      value: String(unreadCount),
      sub: unreadCount > 0 ? t("dash.kpi.attention_req", "Unaddressed field alerts") : t("dash.kpi.all_clear", "All systems nominal"),
      icon: Bell,
      iconBg: unreadCount > 0 ? "bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400" : "bg-primary/10 border-primary/20 text-primary",
      accent: unreadCount > 0 ? "text-red-600 dark:text-red-400" : "text-primary",
      onClick: () => navigate("/notifications"),
    },
  ]

  // Recent valid scans for preview chips
  const recentValidScans = scans
    .filter((s) => s.disease !== "Not an Arecanut image" && s.severity !== "Non-Arecanut")
    .slice(0, 3)

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-4 text-foreground sm:p-6 lg:p-8" style={dashboardPalette}>
      {/* Hidden File Input for Quick Scan */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleQuickPhotoSelect}
        accept="image/*"
        className="hidden"
      />

      <section className="flex flex-col gap-4 border-b border-border/80 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.16em] text-primary">Field overview</p>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">Your plantation at a glance</h1>
          <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Check crop health, review field alerts, and decide what needs attention today.</p>
        </div>
        <button onClick={() => navigate("/detection")} className="inline-flex h-11 shrink-0 items-center justify-center gap-2 self-start rounded-full bg-primary px-5 text-sm font-bold text-primary-foreground transition hover:brightness-110 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/20 sm:self-auto">
          <ScanLine size={16} /> Check a photo <ArrowRight size={15} />
        </button>
      </section>

      {/* ============================================================
      1. REAL-TIME PATHOGEN THREAT ADVISORY BANNER (Conditional)
      ============================================================ */}
      {!isAlertDismissed && (riskForecast?.compositeIndex ?? 0) >= 55 && riskForecast?.overallSeverity !== "Healthy" && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
          <div className="flex items-start gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-700 dark:text-amber-300 shrink-0 mt-0.5">
              <AlertTriangle size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-800 dark:text-amber-200 border border-amber-500/30">
                  {riskForecast?.overallSeverity || "Elevated"} Pathogen Pressure Warning
                </span>
                <span className="text-xs text-muted-foreground font-medium">
                  Spore Germination Index: <strong>{riskForecast?.compositeIndex}%</strong>
                </span>
              </div>
              <h3 className="font-bold text-sm text-foreground mt-1">
                {riskForecast?.advisoryHeadline || "Elevated Spore Germination Microclimate Detected"}
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5 max-w-2xl leading-relaxed">
                {riskForecast?.advisoryAction || "Prophylactic spraying of 1% Bordeaux mixture recommended within the upcoming dry window."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
            <button
              onClick={() => setShowCalculator(true)}
              className="px-3.5 py-1.5 rounded-xl bg-primary text-primary-foreground text-xs font-bold hover:opacity-90 flex items-center gap-1.5 transition-opacity shadow-sm"
            >
              <Calculator size={14} />
              <span>Spray Dosage</span>
            </button>
            <button
              onClick={() => navigate("/weather")}
              className="px-3 py-1.5 rounded-xl border border-border bg-card text-foreground text-xs font-bold hover:bg-muted/50 transition-colors"
            >
              7-Day Radar
            </button>
            <button
              onClick={() => setIsAlertDismissed(true)}
              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/40 transition-colors"
              title="Dismiss Alert"
            >
              <X size={15} />
            </button>
          </div>
        </div>
      )}

      {/* ============================================================
      2. EXECUTIVE KPI GRID (4 Core Operational Metrics)
      ============================================================ */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {kpiCards.map(({ id, label, value, sub, icon: Icon, iconBg, accent, progress, onClick }) => (
          <div
            key={id}
            role="button"
            tabIndex={0}
            onClick={onClick}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault()
                onClick()
              }
            }}
            className="group bg-card rounded-2xl border border-border p-5 sm:p-6 shadow-xs hover:shadow-md hover:border-primary/40 transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none flex min-h-[188px] flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-muted-foreground">{label}</span>
                <div className={`w-9 h-9 rounded-xl border flex items-center justify-center shrink-0 ${iconBg}`}>
                  <Icon size={18} />
                </div>
              </div>
              <div className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${accent}`}>
                {value}
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-border/60">
              {progress !== undefined ? (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] text-muted-foreground gap-1">
                    <span className="line-clamp-1 leading-snug">{sub}</span>
                    <ChevronRight size={13} className="text-muted-foreground/60 group-hover:translate-x-0.5 transition-transform shrink-0" />
                  </div>
                  <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between text-[11px] text-muted-foreground gap-1">
                  <span className="line-clamp-1 leading-snug">{sub}</span>
                  <ChevronRight size={13} className="text-muted-foreground/60 group-hover:translate-x-0.5 transition-transform shrink-0" />
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* ============================================================
      3. QUICK DIAGNOSTIC ACTION STRIP (Streamlined Launcher)
      ============================================================ */}
      <div className="relative isolate overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/10 via-card to-card p-6 shadow-xs sm:p-7">
        <img src={dashboardPhoto} alt="" aria-hidden="true" className="pointer-events-none absolute inset-y-0 right-0 hidden h-full w-[38%] object-cover object-center opacity-[0.18] mix-blend-screen lg:block" />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-card via-card/95 to-card/70" />
        <div className="relative z-10 flex flex-col items-start justify-between gap-6 lg:flex-row lg:items-center">
          <div className="space-y-1.5 max-w-2xl">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-[10px] font-extrabold tracking-wide uppercase">
              <Leaf size={12} />
              <span>ArecaVision crop check</span>
            </div>
            <h2 className="text-lg sm:text-xl font-extrabold text-foreground tracking-tight">
              Check a palm with a photo
            </h2>
            <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
              Upload a clear leaf, nut bunch, or trunk photo to check for common issues and get practical next steps.
            </p>

            {/* Recent Scans Mini Preview Strip */}
            {recentValidScans.length > 0 && (
              <div className="flex items-center gap-2 pt-2 flex-wrap text-xs">
                <span className="text-[11px] text-muted-foreground font-semibold">Recent scans:</span>
                {recentValidScans.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => navigate("/detection", { state: { imageUrl: s.imageUrl } })}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-card border border-border hover:border-primary/50 text-[11px] font-medium text-foreground transition-all shadow-xs group cursor-pointer"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                    <span>{formatDiseaseName(s.disease)}</span>
                    <span className="text-muted-foreground font-mono">({s.confidence}%)</span>
                    <ChevronRight size={11} className="text-muted-foreground group-hover:translate-x-0.5 transition-transform" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Action Launcher Buttons */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 w-full lg:w-auto shrink-0">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-4 py-2.5 rounded-xl bg-card border border-border hover:border-primary text-foreground text-xs font-bold hover:bg-muted/40 flex items-center justify-center gap-2 transition-all shadow-xs cursor-pointer"
            >
              <Upload size={15} className="text-primary" />
              <span>Choose a photo</span>
            </button>

            <button
              onClick={() => navigate("/detection")}
              className="px-5 py-2.5 rounded-xl bg-primary text-primary-foreground text-xs font-extrabold hover:opacity-90 flex items-center justify-center gap-2 transition-all shadow-md group cursor-pointer"
            >
              <ScanLine size={16} />
              <span>Open AI scan</span>
              <ArrowRight size={14} className="group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {/* ============================================================
      4. LIVE CONTEXT: MICROCLIMATE & ACTIVE ALERTS (Side by Side)
      ============================================================ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left: Weather & Microclimate Card */}
        <div className="lg:col-span-6 bg-card rounded-2xl border border-border p-6 shadow-xs flex flex-col justify-between space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-border/70">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
                <CloudRain size={16} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-foreground">Microclimate Telemetry</h3>
                <p className="text-[11px] text-muted-foreground">
                  {weatherState.status === "POPULATED"
                    ? `${weatherState.data.city}, ${weatherState.data.region}`
                    : "Real-time plantation sensors"}
                </p>
              </div>
            </div>
            <Link
              to="/weather"
              className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
            >
              <span>Full Weather & Radar</span>
              <ChevronRight size={13} />
            </Link>
          </div>

          {/* Microclimate Telemetry Grid */}
          {weatherState.status === "POPULATED" ? (
            <div className="space-y-3">
              <div className="grid grid-cols-4 gap-2.5 text-center">
                <div className="p-2.5 rounded-xl bg-muted/30 border border-border/70">
                  <Thermometer size={16} className="mx-auto text-primary mb-1" />
                  <div className="text-xs font-bold text-foreground">{weatherState.data.temperature}°C</div>
                  <div className="text-[10px] text-muted-foreground">Temp</div>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/30 border border-border/70">
                  <Droplets size={16} className="mx-auto text-primary mb-1" />
                  <div className="text-xs font-bold text-foreground">{weatherState.data.humidity}%</div>
                  <div className="text-[10px] text-muted-foreground">Humidity</div>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/30 border border-border/70">
                  <CloudRain size={16} className="mx-auto text-primary mb-1" />
                  <div className="text-xs font-bold text-foreground">{weatherState.data.rainfall} mm</div>
                  <div className="text-[10px] text-muted-foreground">Rainfall</div>
                </div>
                <div className="p-2.5 rounded-xl bg-muted/30 border border-border/70">
                  <Wind size={16} className="mx-auto text-primary mb-1" />
                  <div className="text-xs font-bold text-foreground">{weatherState.data.windSpeed} km/h</div>
                  <div className="text-[10px] text-muted-foreground">Wind</div>
                </div>
              </div>

              {/* Fungal Spore Germination Window */}
              <div className="p-3 rounded-xl bg-primary/5 border border-primary/15 text-xs flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                  <span className="text-muted-foreground">
                    Fungal Infection Risk: <strong className="text-foreground">{weatherState.data.riskLevel}</strong>
                  </span>
                </div>
                <span className="text-[11px] text-primary font-bold">
                  {weatherState.data.humidity >= 80 ? "Spore Risk High" : "Low Risk Window"}
                </span>
              </div>
            </div>
          ) : (
            <div className="py-6 text-center space-y-2 border border-dashed border-border rounded-xl bg-muted/15">
              <p className="text-xs text-muted-foreground">
                Microclimate sensors active. Click to sync live location.
              </p>
              <button
                onClick={() => refreshLocationWeather()}
                className="px-3.5 py-1.5 rounded-xl btn-primary text-xs mx-auto flex items-center gap-1.5 shadow-xs cursor-pointer"
              >
                <RefreshCw size={12} />
                <span>Sync Live Microclimate</span>
              </button>
            </div>
          )}
        </div>

        {/* Right: Priority Field Alerts */}
        <div className="lg:col-span-6 bg-card rounded-2xl border border-border p-6 shadow-xs flex flex-col justify-between space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-border/70">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-600 dark:text-rose-400">
                <Bell size={16} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-foreground">Priority Field Alerts</h3>
                <p className="text-[11px] text-muted-foreground">Urgent alerts & action items</p>
              </div>
            </div>
            <Link
              to="/notifications"
              className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
            >
              <span>View All ({notifications.length})</span>
              <ChevronRight size={13} />
            </Link>
          </div>

          {/* Notifications List */}
          {notifications.length === 0 ? (
            <div className="py-6 text-center border border-dashed border-border rounded-xl bg-muted/15">
              <CheckCircle2 size={24} className="mx-auto text-emerald-500 mb-1.5" />
              <p className="text-xs font-bold text-foreground">All Clear</p>
              <p className="text-[11px] text-muted-foreground mt-0.5">No critical alarms or pending field warnings.</p>
            </div>
          ) : (
            <div className="space-y-2.5">
              {notifications.slice(0, 3).map((n) => (
                <Link
                  key={n.id}
                  to="/notifications"
                  className="flex items-start gap-3 p-2.5 rounded-xl bg-muted/20 border border-border/60 hover:border-primary/40 transition-colors group"
                >
                  <div
                    className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${
                      n.type === "critical"
                        ? "bg-rose-500 ring-4 ring-rose-500/20"
                        : n.type === "warning"
                        ? "bg-amber-500 ring-4 ring-amber-500/20"
                        : "bg-primary ring-4 ring-primary/20"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-foreground group-hover:text-primary transition-colors truncate">
                      {n.title}
                    </p>
                    <p className="text-[11px] text-muted-foreground line-clamp-1 mt-0.5">
                      {n.msg}
                    </p>
                  </div>
                  <span className="text-[10px] text-muted-foreground font-mono shrink-0">{n.time}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ============================================================
      5. FIELD STATUS: TOP DISEASED BLOCKS & INFECTION TRENDS
      ============================================================ */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left: Disease Trend Chart (7 cols) */}
        <div className="lg:col-span-7 bg-card rounded-2xl border border-border p-6 shadow-xs space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-border/70">
            <div>
              <h3 className="text-sm font-bold text-foreground">Infection Incidence Trend</h3>
              <p className="text-[11px] text-muted-foreground">Temporal pathogen distribution across recent field batches</p>
            </div>

            {trendData.length > 0 && (
              <div className="flex items-center gap-3 flex-wrap">
                {trendLegend.map(({ label, color }) => (
                  <div key={label} className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
                    <div className="w-2 h-2 rounded-full" style={{ background: color }} />
                    <span>{label}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {trendData.length === 0 ? (
            <div className="py-12 text-center border border-dashed border-border rounded-xl bg-muted/15 space-y-2">
              <Activity size={24} className="mx-auto text-muted-foreground/60" />
              <p className="text-xs font-bold text-foreground">No historical trend points yet</p>
              <p className="text-[11px] text-muted-foreground max-w-sm mx-auto">
                As you run field diagnostics in the AI Studio, pathogen progression will plot here automatically.
              </p>
            </div>
          ) : (
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.6} />
                  <XAxis dataKey="date" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} />
                  <YAxis stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="anthracnose" stroke={THEME_TOKENS.charts.lines.anthracnose} strokeWidth={2.5} dot={{ r: 3 }} name="Anthracnose" />
                  <Line type="monotone" dataKey="fruitRot" stroke={THEME_TOKENS.charts.lines.fruitRot} strokeWidth={2.5} dot={{ r: 3 }} name="Fruit Rot" />
                  <Line type="monotone" dataKey="nutCracking" stroke={THEME_TOKENS.charts.lines.nutCracking} strokeWidth={2} dot={{ r: 2.5 }} name="Nut Cracking" />
                  <Line type="monotone" dataKey="sootyMold" stroke={THEME_TOKENS.charts.lines.sootyMold} strokeWidth={2} dot={{ r: 2.5 }} name="Sooty Mold" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Right: Top Diseased Plantation Sectors (5 cols) */}
        <div className="lg:col-span-5 bg-card rounded-2xl border border-border p-6 shadow-xs space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-border/70">
            <div>
              <h3 className="text-sm font-bold text-foreground">Hotspot Plantation Sectors</h3>
              <p className="text-[11px] text-muted-foreground">Priority plots requiring spraying</p>
            </div>
            <Link
              to="/map"
              className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
            >
              <span>View Map</span>
              <ChevronRight size={13} />
            </Link>
          </div>

          {topDiseasedBlocks.length === 0 ? (
            <div className="py-12 text-center border border-dashed border-border rounded-xl bg-muted/15 space-y-2">
              <TreePine size={24} className="mx-auto text-muted-foreground/60" />
              <p className="text-xs font-bold text-foreground">No plantation blocks tagged</p>
              <p className="text-[11px] text-muted-foreground">Setup plantation acreage & sectors in the Plantation Map.</p>
              <button
                onClick={() => navigate("/map")}
                className="mt-2 px-3 py-1.5 rounded-xl btn-primary text-xs mx-auto flex items-center gap-1 cursor-pointer"
              >
                <span>Setup Map</span>
                <ChevronRight size={12} />
              </button>
            </div>
          ) : (
            <div className="space-y-3.5">
              {topDiseasedBlocks.slice(0, 4).map(({ id, diseasedTrees, status, color }) => {
                const maxTrees = 1000
                const pct = Math.min(100, Math.round((diseasedTrees / maxTrees) * 100))

                return (
                  <div key={id} className="p-2.5 rounded-xl bg-muted/20 border border-border/50 space-y-1.5">
                    <div className="flex items-center justify-between text-xs font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-foreground">{id}</span>
                        <span className="text-[11px] font-normal text-muted-foreground">
                          · {diseasedTrees} palms affected
                        </span>
                      </div>
                      <span className="text-[11px] px-2 py-0.5 rounded-md font-extrabold" style={{ color, backgroundColor: `${color}15` }}>
                        {status}
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${pct}%`, background: color }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* ============================================================
      SPRAY DOSAGE CALCULATOR MODAL (Triggered from Advisory Banner)
      ============================================================ */}
      {showCalculator && (
        <TreatmentCalculatorModal
          isOpen={showCalculator}
          onClose={() => setShowCalculator(false)}
          initialDisease="koleroga"
        />
      )}
    </div>
  )
}
