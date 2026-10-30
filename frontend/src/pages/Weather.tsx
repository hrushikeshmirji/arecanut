import { useState, useEffect } from "react"
import type { CSSProperties } from "react"
import { useSearchParams } from "react-router-dom"
import {
  CloudSun,
  Thermometer,
  Droplets,
  Wind,
  Sun,
  CloudRain,
  Compass,
  Search,
  MapPin,
  RefreshCw,
  ShieldAlert,
  AlertTriangle,
  AlertCircle,
  Clock,
  Sparkles,
  Calculator,
  Calendar,
  Layers,
  CheckCircle2,
} from "lucide-react"
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts"
import { useWeather } from "../contexts/WeatherContext"
import { useLanguage } from "../contexts/LanguageContext"
import { fetchRiskForecast, RiskForecastData } from "../services/weatherService"
import TreatmentCalculatorModal from "../components/TreatmentCalculatorModal"
import { useTheme } from "../contexts/ThemeProvider"

const PLANTATION_PRESETS = [
  "Madikeri",
  "Shivamogga",
  "Mangaluru",
  "Chikkamagaluru",
  "Sirsi",
]

interface WeatherProps {
  defaultTab?: "weather" | "risk"
}

export default function Weather({ defaultTab = "weather" }: WeatherProps) {
  const { t } = useLanguage()
  const { theme } = useTheme()
  const [searchParams, setSearchParams] = useSearchParams()
  const { weatherState, refreshLocationWeather, searchCity } = useWeather()

  // Tab State: "all" | "weather" | "risk"
  const urlTab = searchParams.get("tab")
  const initialTab = urlTab === "risk" || defaultTab === "risk" ? "risk" : "all"
  const [activeTab, setActiveTab] = useState<"all" | "weather" | "risk">(initialTab)

  const [cityInput, setCityInput] = useState("")
  const [selectedLocation, setSelectedLocation] = useState<string>("Madikeri")
  const [riskData, setRiskData] = useState<RiskForecastData | null>(null)
  const [riskLoading, setRiskLoading] = useState(false)
  const [riskError, setRiskError] = useState<string | null>(null)
  const [calcModalOpen, setCalcModalOpen] = useState(false)
  const [calcDisease, setCalcDisease] = useState("koleroga")
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const isDark = theme === "dark" || (theme === "system" && systemDark)
  const weatherPalette = {
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
  } as CSSProperties

  useEffect(() => {
    if (theme !== "system") return
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme])

  // Load Epidemiological Risk Forecast
  const loadRisk = async (location: string) => {
    try {
      setRiskLoading(true)
      setRiskError(null)
      const data = await fetchRiskForecast(location)
      setRiskData(data)
    } catch (err) {
      setRiskError(err instanceof Error ? err.message : "Failed to load epidemiological risk forecast.")
    } finally {
      setRiskLoading(false)
    }
  }

  useEffect(() => {
    loadRisk(selectedLocation)
  }, [selectedLocation])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!cityInput.trim()) return
    const city = cityInput.trim()
    await searchCity(city)
    setSelectedLocation(city)
  }

  const handleSelectPreset = async (city: string) => {
    setSelectedLocation(city)
    await searchCity(city)
  }

  const getSeverityBadgeClass = (sev: string) => {
    switch (sev) {
      case "Critical":
        return "bg-danger/10 text-danger border-danger/25"
      case "Severe":
        return "bg-warning/10 text-warning border-warning/25"
      case "Moderate":
        return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/25"
      default:
        return "bg-primary/10 text-primary border-primary/25"
    }
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-5 text-foreground sm:p-6 lg:p-8" style={weatherPalette}>
      {/* Header & Controls */}
      <div className="flex flex-col gap-5 border-b border-border/80 pb-6 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.16em] text-primary">Weather for your growing area</p>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
              {t("weather.title", "Weather & Outbreak Risk Intelligence")}
            </h1>
            <span className="text-[10px] font-bold px-2 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded-full flex items-center gap-1">
              <Sparkles size={11} />
              Unified Telemetry
            </span>
          </div>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            {t("weather.subtitle", "Microclimate monitoring, precipitation analysis, and 7-day fungal infection forecasts")}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3">
          <form onSubmit={handleSearch} className="flex items-center gap-2 bg-card border border-border rounded-xl px-3 py-2 w-full sm:w-64">
            <input
              value={cityInput}
              onChange={(e) => setCityInput(e.target.value)}
              placeholder={t("weather.search_placeholder", "Search plantation city...")}
              className="bg-transparent border-none outline-none text-xs text-foreground placeholder-muted-foreground flex-1"
            />
            <button type="submit" className="p-1 rounded-lg hover:bg-muted text-primary font-bold text-xs flex items-center gap-1" title="Search City">
              <Search size={16} />
            </button>
          </form>

          <button
            onClick={refreshLocationWeather}
            disabled={weatherState.status === "LOADING"}
            className="btn-primary text-xs w-full sm:w-auto flex items-center justify-center gap-2 shadow-sm"
          >
            {weatherState.status === "LOADING" ? <RefreshCw size={14} className="animate-spin" /> : <MapPin size={14} />}
            <span>{t("weather.use_location", "Use GPS Location")}</span>
          </button>
        </div>
      </div>

      {/* Quick Plantation Presets & Segment Filter */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] text-muted-foreground font-semibold">Key Belts:</span>
          {PLANTATION_PRESETS.map((city) => (
            <button
              key={city}
              onClick={() => handleSelectPreset(city)}
              className={`px-2.5 py-1 rounded-lg border text-[11px] font-medium transition-colors focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none ${
                selectedLocation.toLowerCase() === city.toLowerCase()
                  ? "bg-primary text-white border-primary shadow-xs"
                  : "bg-card border-border text-foreground hover:border-primary hover:text-primary"
              }`}
            >
              {city}
            </button>
          ))}
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-muted p-1 rounded-xl self-start sm:self-auto">
          <button
            onClick={() => { setActiveTab("all"); setSearchParams({}); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "all" ? "bg-card text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            All Insights
          </button>
          <button
            onClick={() => { setActiveTab("weather"); setSearchParams({ tab: "weather" }); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "weather" ? "bg-card text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Microclimate
          </button>
          <button
            onClick={() => { setActiveTab("risk"); setSearchParams({ tab: "risk" }); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              activeTab === "risk" ? "bg-card text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Infection Risk
          </button>
        </div>
      </div>

      {/* SECTION 1: LIVE MICROCLIMATE */}
      {(activeTab === "all" || activeTab === "weather") && (
        <div className="space-y-8 animate-in fade-in duration-200">
          {weatherState.status === "LOADING" && (
            <div className="bg-card rounded-2xl border border-border p-12 text-center max-w-xl mx-auto my-4 space-y-4">
              <div className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto" />
              <p className="text-xs font-bold text-foreground">{t("weather.loading", "Loading Microclimate Weather Data...")}</p>
            </div>
          )}

          {weatherState.status === "POPULATED" && (
            <div className="space-y-8">
              <div className="bg-card rounded-2xl border border-border p-7 shadow-sm relative overflow-hidden">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div>
                    <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
                      <MapPin size={14} className="text-primary" />
                      <span>{weatherState.data.city}, {weatherState.data.region}</span>
                      <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold">
                        {t("weather.live_badge", "Live")}
                      </span>
                    </div>

                    <div className="flex items-baseline gap-4 mt-3">
                      <span className="text-5xl font-extrabold text-foreground tracking-tight">
                        {weatherState.data.temperature}°C
                      </span>
                      <span className="text-lg font-bold text-muted-foreground">{weatherState.data.condition}</span>
                    </div>

                    <div className="text-xs text-muted-foreground mt-2">
                      {t("weather.last_updated", "Last updated at")} {weatherState.data.lastUpdated}
                    </div>
                  </div>

                  {/* Disease Risk Warning */}
                  <div className={`p-4 rounded-xl border max-w-sm ${
                    weatherState.data.riskLevel === "High"
                      ? "bg-danger/10 border-danger/20 text-danger"
                      : "bg-warning/10 border-warning/20 text-warning"
                  }`}>
                    <div className="flex items-center gap-2 font-bold text-sm mb-1">
                      <ShieldAlert size={18} />
                      <span>{t("weather.risk", "Disease Outbreak Risk")}: {weatherState.data.riskLevel}</span>
                    </div>
                    <p className="text-xs text-foreground/80 leading-relaxed">
                      {t("weather.humidity_risk_desc", "Relative humidity significantly impacts fungal spore germination (Anthracnose & Koleroga).")}
                    </p>
                  </div>
                </div>

                {/* Grid Stats */}
                <div className="grid grid-cols-2 gap-4 border-t border-border mt-6 pt-6 sm:grid-cols-3 lg:grid-cols-6">
                  {[
                    { icon: Thermometer, label: t("weather.temp", "Temperature"), val: `${weatherState.data.temperature}°C` },
                    { icon: Droplets, label: t("weather.humidity", "Humidity"), val: `${weatherState.data.humidity}%` },
                    { icon: Wind, label: t("weather.wind", "Wind Speed"), val: `${weatherState.data.windSpeed} km/h` },
                    { icon: CloudRain, label: t("weather.rainfall", "Rainfall"), val: `${weatherState.data.rainfall} mm` },
                    { icon: Sun, label: t("weather.uv", "UV Index"), val: `${weatherState.data.uvIndex} / 10` },
                    { icon: Compass, label: t("weather.sunrise_label", "Sunrise/Sunset"), val: `${weatherState.data.sunrise}` },
                  ].map(({ icon: Icon, label, val }) => (
                    <div key={label} className="p-3 rounded-xl bg-muted/30 border border-border text-center">
                      <Icon size={18} className="mx-auto text-primary mb-1" />
                      <div className="text-sm font-extrabold text-foreground">{val}</div>
                      <div className="text-[10px] text-muted-foreground mt-0.5">{label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 5-Day Forecast Grid */}
              <div>
                <h2 className="text-base font-bold text-foreground mb-3">{t("weather.forecast_5day", "5-Day Microclimate Forecast")}</h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-5">
                  {weatherState.data.forecast.map((f) => (
                    <div key={f.day} className="bg-card rounded-2xl border border-border p-5 text-center card-hover shadow-xs">
                      <div className="text-xs font-bold text-foreground mb-2">{f.day}</div>
                      <CloudSun size={24} className="mx-auto text-warning mb-2" />
                      <div className="text-sm font-extrabold text-foreground">{f.tempMax}° / {f.tempMin}°</div>
                      <div className="text-[11px] text-muted-foreground mt-1">{f.condition}</div>
                      <div className="text-[10px] font-bold text-primary mt-2">{t("weather.rain_prefix", "Rain")}: {f.rainProb}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* SECTION 2: EPIDEMIOLOGICAL RISK FORECAST */}
      {(activeTab === "all" || activeTab === "risk") && (
        <div className="space-y-8 animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-t border-border pt-6">
            <div>
              <h2 className="text-base font-bold text-foreground flex items-center gap-2">
                <ShieldAlert size={18} className="text-danger" />
                <span>Epidemiological Infection Pressure & 7-Day Trajectory</span>
              </h2>
              <p className="text-xs text-muted-foreground">
                Pathogen sporulation probability correlated with microclimate temperature and rainfall
              </p>
            </div>

            <button
              onClick={() => { setCalcDisease("koleroga"); setCalcModalOpen(true); }}
              className="btn-primary text-xs flex items-center gap-1.5 shadow-xs"
            >
              <Calculator size={14} />
              <span>Calculate Spray Dosage</span>
            </button>
          </div>

          {riskLoading && (
            <div className="bg-card rounded-2xl border border-border p-10 text-center max-w-md mx-auto my-2 space-y-3">
              <div className="w-8 h-8 border-3 border-primary/20 border-t-primary rounded-full animate-spin mx-auto" />
              <p className="text-xs font-bold text-foreground">Calculating infection trajectories...</p>
            </div>
          )}

          {riskError && (
            <div className="p-4 rounded-xl bg-danger/10 border border-danger/25 text-xs text-danger flex items-center gap-2">
              <AlertTriangle size={16} className="shrink-0" />
              <span>{riskError}</span>
            </div>
          )}

          {riskData && (
            <div className="space-y-5">
              {/* Composite Overview Card */}
              <div className="p-6 rounded-2xl bg-card border border-border shadow-xs space-y-5">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
                  <div>
                    <div className="flex items-center gap-2.5 mb-1.5">
                      <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${getSeverityBadgeClass(riskData.overallSeverity)}`}>
                        {riskData.overallSeverity} Risk Level
                      </span>
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock size={12} /> Forecast Zone: {selectedLocation}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-foreground">{riskData.advisoryHeadline}</h3>
                    <p className="text-xs text-muted-foreground mt-1 max-w-2xl leading-relaxed">{riskData.advisoryAction}</p>
                  </div>

                  <div className="flex items-center gap-4 bg-muted/40 p-4 rounded-xl border border-border self-start md:self-auto">
                    <div className="text-center">
                      <div className="text-3xl font-extrabold text-foreground">{riskData.compositeIndex}%</div>
                      <div className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider mt-0.5">Spore Index</div>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-danger/10 border border-danger/20 flex items-center justify-center text-danger">
                      <ShieldAlert size={20} />
                    </div>
                  </div>
                </div>

                {/* Pathogen Breakdown Cards */}
                <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  {Object.entries(riskData.pathogenMetrics).map(([key, item]) => (
                    <div key={key} className="p-3.5 rounded-xl bg-background border border-border space-y-2.5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-foreground truncate pr-2">{item.name}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${getSeverityBadgeClass(item.status)}`}>
                          {item.status}
                        </span>
                      </div>
                      <div className="flex items-baseline justify-between">
                        <span className="text-xl font-extrabold text-foreground">{item.riskScore}%</span>
                        <span className="text-[11px] text-muted-foreground">Incubation: ~{item.incubationDays}d</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            item.riskScore >= 75 ? "bg-danger" : item.riskScore >= 45 ? "bg-warning" : "bg-primary"
                          }`}
                          style={{ width: `${item.riskScore}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 7-Day Trajectory Area Chart */}
              <div className="p-6 rounded-2xl bg-card border border-border shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <h3 className="text-xs font-bold text-foreground uppercase tracking-wide">7-Day Outbreak Trajectory</h3>
                    <p className="text-[11px] text-muted-foreground">Relative humidity and precipitation correlation projection</p>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#dc2626]" /> Koleroga</span>
                    <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#b45309]" /> Anthracnose</span>
                    <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]" /> Nut Cracking</span>
                  </div>
                </div>

                <div className="h-60 w-full pt-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={riskData.trajectory} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="kolerogaGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#dc2626" stopOpacity={0.25} />
                          <stop offset="95%" stopColor="#dc2626" stopOpacity={0.0} />
                        </linearGradient>
                        <linearGradient id="anthracnoseGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#b45309" stopOpacity={0.25} />
                          <stop offset="95%" stopColor="#b45309" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                      <XAxis dataKey="day" stroke="var(--color-muted-foreground)" fontSize={11} tickLine={false} />
                      <YAxis stroke="var(--color-muted-foreground)" fontSize={11} domain={[0, 100]} tickLine={false} unit="%" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--color-card)",
                          borderColor: "var(--color-border)",
                          borderRadius: "0.75rem",
                          fontSize: "12px",
                          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                        }}
                      />
                      <Area type="monotone" dataKey="kolerogaRisk" name="Fruit Rot (Koleroga)" stroke="#dc2626" strokeWidth={2} fillOpacity={1} fill="url(#kolerogaGrad)" />
                      <Area type="monotone" dataKey="anthracnoseRisk" name="Anthracnose" stroke="#b45309" strokeWidth={2} fillOpacity={1} fill="url(#anthracnoseGrad)" />
                      <Area type="monotone" dataKey="nutCrackingRisk" name="Nut Cracking" stroke="#3b82f6" strokeWidth={1.5} fillOpacity={0} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Spray Dosage Modal */}
      {calcModalOpen && (
        <TreatmentCalculatorModal
          isOpen={calcModalOpen}
          onClose={() => setCalcModalOpen(false)}
          initialDisease={calcDisease}
          initialPalms={450}
        />
      )}
    </div>
  )
}
