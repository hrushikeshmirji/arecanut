import React, { useState, useRef, useEffect } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import {
  LayoutDashboard,
  ScanLine,
  BookOpen,
  Map,
  BarChart2,
  CloudSun,
  ShieldAlert,
  History,
  FileText,
  Settings,
  Bell,
  Search,
  ChevronDown,
  Sparkles,
  FlaskConical,
  CloudDrizzle,
  Menu,
  X,
  Globe,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Activity,
  Shield,
  LogOut,
  WifiOff,
  ArrowUpRight,
} from "lucide-react"
import { ThemeToggle } from "./ThemeToggle"
import CommandPalette from "./CommandPalette"
import { useLanguage, Language } from "../contexts/LanguageContext"
import { useNotifications } from "../contexts/NotificationContext"
import { usePlantation } from "../contexts/PlantationContext"
import { useAuth } from "../contexts/AuthContext"
import { useClickOutside } from "../hooks/useClickOutside"
import { useNetworkStatus } from "../hooks/useNetworkStatus"
import BrandMark from "./BrandMark"

interface NavItem {
  icon: any
  labelKey: string
  defaultLabel: string
  path: string
  badge?: string
}

const baseNavItems: NavItem[] = [
  { icon: LayoutDashboard, labelKey: "nav.dashboard", defaultLabel: "Dashboard", path: "/dashboard" },
  { icon: ScanLine, labelKey: "nav.detection", defaultLabel: "AI Detection", path: "/detection", badge: "2.0" },
  { icon: Map, labelKey: "nav.map", defaultLabel: "Plantation Map", path: "/map" },
  { icon: BookOpen, labelKey: "nav.diseases", defaultLabel: "Disease Library", path: "/diseases" },
  { icon: CloudSun, labelKey: "nav.weather", defaultLabel: "Weather Intelligence", path: "/weather" },
  { icon: History, labelKey: "nav.scans", defaultLabel: "Scan History", path: "/scans" },
  { icon: Sparkles, labelKey: "nav.assistant", defaultLabel: "AI Assistant", path: "/assistant", badge: "New" },
  { icon: Settings, labelKey: "nav.settings", defaultLabel: "Settings", path: "/settings" },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const { language, setLanguage, t } = useLanguage()
  const { unreadCount } = useNotifications()
  const { isOnline } = useNetworkStatus()

  const navItems = React.useMemo(() => {
    if (user?.role === "admin") {
      return [
        ...baseNavItems,
        { icon: Shield, labelKey: "nav.admin", defaultLabel: "Admin Panel", path: "/admin", badge: "Admin" },
      ]
    }
    return baseNavItems
  }, [user?.role])


  // Sidebar collapsible state
  const [isCollapsed, setIsCollapsed] = useState(() => {
    return localStorage.getItem("arecavision_sidebar_collapsed") === "true"
  })

  // Mobile drawer state
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  // Header dropdown & Command Palette (Ctrl+K)
  const [langDropdownOpen, setLangDropdownOpen] = useState(false)
  const [moreMenuOpen, setMoreMenuOpen] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const [profileMenuOpen, setProfileMenuOpen] = useState(false)

  useEffect(() => {
    const onGlobalKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault()
        setCommandPaletteOpen((prev) => !prev)
      }
    }
    window.addEventListener("keydown", onGlobalKeyDown)
    return () => window.removeEventListener("keydown", onGlobalKeyDown)
  }, [])

  // Refs for click outside detection
  const langDropdownRef = useRef<HTMLDivElement>(null)
  const moreMenuRef = useRef<HTMLDivElement>(null)
  const profileMenuRef = useRef<HTMLDivElement>(null)

  useClickOutside(langDropdownRef, () => setLangDropdownOpen(false))
  useClickOutside(moreMenuRef, () => setMoreMenuOpen(false))
  useClickOutside(profileMenuRef, () => setProfileMenuOpen(false))

  const primaryNavItems = navItems.filter(({ path }) => ["/dashboard", "/detection", "/map", "/diseases", "/weather"].includes(path))
  const moreNavItems = navItems.filter(({ path }) => !["/dashboard", "/detection", "/map", "/diseases", "/weather"].includes(path))
  const isMoreActive = moreNavItems.some(({ path }) => location.pathname === path || (path === "/scans" && location.pathname === "/reports"))

  const toggleCollapse = () => {
    const nextState = !isCollapsed
    setIsCollapsed(nextState)
    localStorage.setItem("arecavision_sidebar_collapsed", String(nextState))
  }


  // Close mobile drawer on Escape key press
  useEffect(() => {
    if (!isMobileOpen) return
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsMobileOpen(false)
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isMobileOpen])

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* Skip to Main Content Link for Keyboard Accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:font-bold focus:text-xs focus:rounded-xl focus:shadow-xl focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
      >
        Skip to main content
      </a>

      {/* ===== MOBILE BACKDROP ===== */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm transition-opacity"
          aria-hidden="true"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* ===== SIDEBAR ===== */}
      <aside
        aria-label="Sidebar Navigation"
        aria-modal={isMobileOpen ? "true" : undefined}
        role={isMobileOpen ? "dialog" : undefined}
        className={`fixed inset-y-0 left-0 z-50 flex flex-col bg-sidebar border-r border-border transition-all duration-300 lg:hidden ${
          isCollapsed ? "w-20" : "w-[260px]"
        } ${isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}
      >
        {/* Sidebar Header / Logo */}
        <div
          className={`h-16 border-b border-border shrink-0 flex items-center transition-all ${
            isCollapsed ? "justify-center px-2" : "justify-between px-4"
          }`}
        >
          {isCollapsed ? (
            /* Collapsed State: Single clean, unclipped centered interactive logo with hover expand icon & tooltip */
            <button
              onClick={toggleCollapse}
              className="group relative w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 hover:scale-105 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none cursor-pointer"
              title={t("layout.expand_menu", "ArecaVision AI — Click to expand")}
              aria-label={t("layout.expand_menu", "Expand Sidebar")}
            >
              <BrandMark size={40} className="transition-opacity duration-200 group-hover:opacity-0" />
              <PanelLeftOpen
                size={20}
                className="text-white absolute transition-opacity duration-200 opacity-0 group-hover:opacity-100"
              />

              {/* Floating Tooltip */}
              <div className="absolute left-full ml-3 px-2.5 py-1.5 bg-card border border-border text-foreground text-xs rounded-lg shadow-xl whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 font-semibold">
                ArecaVision AI · {t("layout.expand_menu", "Expand Sidebar")}
              </div>
            </button>
          ) : (
            /* Expanded State: Full Logo + Brand name + Collapse button */
            <>
              <Link
                to="/dashboard"
                className="flex items-center gap-3 overflow-hidden rounded-xl p-1 -m-1 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none"
              >
                <BrandMark size={40} />
                <div className="truncate">
                  <div className="text-foreground font-bold text-sm leading-tight truncate">
                    ArecaVision AI
                  </div>
                  <div className="text-[11px] text-muted-foreground truncate">
                    Precision Agriculture
                  </div>
                </div>
              </Link>

              {/* Desktop Collapse Toggle Button */}
              <button
                onClick={toggleCollapse}
                className="hidden lg:flex p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none cursor-pointer"
                title={t("layout.collapse_menu", "Collapse Sidebar")}
                aria-label={t("layout.collapse_menu", "Collapse Sidebar")}
              >
                <PanelLeftClose size={18} />
              </button>

              {/* Mobile Close Button */}
              <button
                onClick={() => setIsMobileOpen(false)}
                className="lg:hidden p-1.5 rounded-lg text-muted-foreground hover:text-foreground focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none cursor-pointer"
                aria-label="Close Sidebar"
              >
                <X size={20} />
              </button>
            </>
          )}
        </div>

        {/* Sidebar Navigation */}
        <nav className="flex-1 overflow-y-auto sidebar-scroll px-3 py-3 space-y-1">
          {navItems.map(({ icon: Icon, labelKey, defaultLabel, path, badge }) => {
            const isActive =
              location.pathname === path ||
              (path === "/weather" && location.pathname === "/risk") ||
              (path === "/scans" && location.pathname === "/reports") ||
              (path === "/dashboard" && location.pathname === "/analytics")
            const label = t(labelKey, defaultLabel)

            return (
              <Link
                key={path}
                to={path}
                onClick={() => setIsMobileOpen(false)}
                title={isCollapsed ? label : undefined}
                className={`relative group flex items-center ${
                  isCollapsed ? "justify-center px-0 py-2.5" : "gap-3 px-3 py-2.5"
                } rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? "nav-item-active"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50 focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none"
                }`}
              >
                {/* Active Left Accent Pill */}
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 rounded-r bg-primary" />
                )}

                <Icon size={18} className={`shrink-0 ${isActive ? "nav-icon" : ""}`} />
                {!isCollapsed && <span className="flex-1 truncate">{label}</span>}
                {!isCollapsed && badge && (
                  <span
                    className={`px-1.5 py-0.5 text-[9px] font-bold rounded-full leading-none ${
                      isActive
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {badge}
                  </span>
                )}

                {/* Collapsed Tooltip */}
                {isCollapsed && (
                  <div className="absolute left-full ml-2 px-2.5 py-1.5 bg-card border border-border text-foreground text-xs rounded-lg shadow-xl whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 font-medium">
                    {label}
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Sidebar Footer */}
        {!isCollapsed ? (
          <div className="p-3 border-t border-border flex items-center justify-between text-[11px] text-muted-foreground shrink-0">
            <div className="flex items-center gap-2 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse" />
              <span>ArecaVision AI</span>
            </div>
            <button
              onClick={toggleCollapse}
              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors cursor-pointer"
              title={t("layout.collapse_menu", "Collapse Sidebar")}
              aria-label={t("layout.collapse_menu", "Collapse Sidebar")}
            >
              <PanelLeftClose size={16} />
            </button>
          </div>
        ) : (
          <div className="p-2 border-t border-border flex flex-col items-center gap-2 shrink-0">
            <button
              onClick={toggleCollapse}
              className="w-10 h-10 rounded-xl bg-card border border-border flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors cursor-pointer"
              title={t("layout.expand_menu", "Expand Sidebar")}
              aria-label={t("layout.expand_menu", "Expand Sidebar")}
            >
              <PanelLeftOpen size={18} />
            </button>
          </div>
        )}
      </aside>

      {/* ===== MAIN CONTENT AREA ===== */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Remote Field Offline Resilience Banner */}
        {!isOnline && (
          <div className="bg-amber-600 text-white text-[11px] font-semibold py-1.5 px-4 text-center flex items-center justify-center gap-2 shadow-sm z-50">
            <WifiOff size={13} />
            <span>Field Offline Mode — Operating from local specimen cache; cloud sync will resume once connected.</span>
          </div>
        )}

        {/* Header Bar */}
        <header className="h-[76px] shrink-0 bg-navbar border-b border-border px-2.5 sm:px-4 lg:px-6 flex items-center justify-between gap-2 sm:gap-3 relative z-40">
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {/* Mobile Hamburger Toggle */}
            <button
              onClick={() => setIsMobileOpen(true)}
              className="lg:hidden p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none"
              aria-label="Open navigation menu"
              aria-expanded={isMobileOpen}
            >
              <Menu size={20} />
            </button>
            <Link to="/dashboard" className="flex items-center gap-2.5 rounded-lg focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none">
              <BrandMark size={36} />
              <div>
                <div className="text-sm font-bold leading-tight">ArecaVision AI</div>
                <div className="text-[10px] text-muted-foreground">Precision Agriculture</div>
              </div>
            </Link>
          </div>

          {/* Centered primary navigation pill */}
          <nav aria-label="Main navigation" className="mx-2 hidden min-w-0 flex-1 justify-center lg:flex">
            <div className="relative flex max-w-full items-center gap-0.5 overflow-visible rounded-full border border-white/10 bg-[#0A1104]/90 p-1 text-white shadow-sm">
              {primaryNavItems.map(({ labelKey, defaultLabel, path }) => {
                const isActive = location.pathname === path ||
                  (path === "/weather" && location.pathname === "/risk") ||
                  (path === "/scans" && location.pathname === "/reports") ||
                  (path === "/dashboard" && location.pathname === "/analytics")
                return (
                  <Link
                    key={path}
                    to={path}
                    aria-current={isActive ? "page" : undefined}
                    className={`inline-flex h-9 shrink-0 items-center rounded-full px-2.5 text-[11px] font-semibold transition-colors xl:px-3 ${isActive ? "bg-[#B7D957] text-[#0A1104]" : "text-white/75 hover:bg-white/10 hover:text-white"}`}
                  >
                    {t(labelKey, defaultLabel)}
                  </Link>
                )
              })}
              {moreNavItems.length > 0 && (
                <div ref={moreMenuRef} className="relative shrink-0">
                  <button
                    type="button"
                    onClick={() => setMoreMenuOpen((open) => !open)}
                    aria-expanded={moreMenuOpen}
                    aria-haspopup="menu"
                    className={`inline-flex h-9 items-center gap-1 rounded-full px-2.5 text-[11px] font-semibold transition-colors xl:px-3 ${isMoreActive ? "bg-[#B7D957] text-[#0A1104]" : "text-white/75 hover:bg-white/10 hover:text-white"}`}
                  >
                    More <ChevronDown size={13} />
                  </button>
                  {moreMenuOpen && (
                    <div role="menu" className="absolute right-0 top-full z-50 mt-2 min-w-48 rounded-2xl border border-border bg-card p-1.5 text-foreground shadow-xl">
                      {moreNavItems.map(({ icon: Icon, labelKey, defaultLabel, path, badge }) => {
                        const isActive = location.pathname === path || (path === "/scans" && location.pathname === "/reports")
                        return (
                          <Link key={path} to={path} role="menuitem" onClick={() => setMoreMenuOpen(false)} className={`flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-xs font-semibold transition-colors ${isActive ? "bg-primary/10 text-primary" : "text-foreground hover:bg-muted"}`}>
                            <Icon size={15} />
                            <span className="flex-1">{t(labelKey, defaultLabel)}</span>
                            {badge && <span className="rounded-full bg-muted px-1.5 py-0.5 text-[9px] text-muted-foreground">{badge}</span>}
                          </Link>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          </nav>

          <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
            {/* Spotlight Command Palette Trigger (Ctrl+K) */}
            <button
              type="button"
              onClick={() => setCommandPaletteOpen(true)}
              className="hidden 2xl:flex items-center justify-between gap-2 bg-muted/50 hover:bg-muted border border-border rounded-full px-3 py-1.5 w-40 text-left transition-all focus-visible:ring-2 focus-visible:ring-primary"
              aria-label="Open Spotlight Command Palette"
            >
              <div className="flex items-center gap-2 min-w-0">
                <Search size={14} className="text-primary shrink-0" />
                <span className="text-xs text-muted-foreground truncate">
                  {t("common.search", "Spotlight...")}
                </span>
              </div>
              <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono font-bold bg-card border border-border rounded text-muted-foreground shrink-0">
                Ctrl K
              </kbd>
            </button>

            {/* Notification Bell Badge */}
            <Link
              to="/notifications"
              className="relative p-1.5 sm:p-2 rounded-xl border border-border bg-card hover:bg-muted text-muted-foreground hover:text-foreground transition-colors focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none shrink-0"
              title="Notifications"
              aria-label={`Notifications (${unreadCount} unread)`}
            >
              <Bell size={18} />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center animate-pulse">
                  {unreadCount}
                </span>
              )}
            </Link>

            {/* Multilingual Switcher */}
            <div ref={langDropdownRef} className="relative z-50 shrink-0">
              <button
                onClick={() => {
                  setLangDropdownOpen(!langDropdownOpen)
                }}
                className="flex items-center gap-1 px-2 sm:px-3 py-1.5 rounded-xl border border-border bg-card text-xs font-semibold hover:bg-muted transition-colors shadow-sm focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none"
                aria-expanded={langDropdownOpen}
                aria-haspopup="true"
              >
                <Globe size={14} className="text-primary" />
                <span className="uppercase text-[11px] sm:text-xs">{language}</span>
                <ChevronDown size={12} className="text-muted-foreground" />
              </button>

              {langDropdownOpen && (
                <div
                  className="absolute right-0 top-full mt-2 w-44 bg-card rounded-xl shadow-2xl border border-border py-1.5 z-50 opacity-100 ring-1 ring-black/5 dark:ring-white/10"
                  style={{ backgroundColor: "var(--color-card)" }}
                >
                  {[
                    { code: "en" as Language, label: "English" },
                    { code: "kn" as Language, label: "ಕನ್ನಡ (Kannada)" },
                    { code: "hi" as Language, label: "हिंदी (Hindi)" },
                  ].map((item) => (
                    <button
                      key={item.code}
                      onClick={() => {
                        setLanguage(item.code)
                        setLangDropdownOpen(false)
                      }}
                      className={`w-full text-left px-3.5 py-2 text-xs font-medium hover:bg-muted transition-colors focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none ${
                        language === item.code
                          ? "text-primary font-bold bg-primary/10"
                          : "text-foreground font-medium"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            <div className="shrink-0">
              <ThemeToggle />
            </div>

            <Link to="/detection" className="hidden sm:inline-flex h-10 items-center gap-2 rounded-full bg-[#B7D957] pl-4 pr-1.5 text-xs font-bold text-[#0A1104] transition hover:brightness-105">
              Scan a photo
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#0A1104] text-[#B7D957]"><ArrowUpRight size={15} /></span>
            </Link>

            {/* User Profile Badge */}
            <div ref={profileMenuRef} className="relative shrink-0 border-l border-border pl-2 sm:pl-3">
              <button type="button" onClick={() => setProfileMenuOpen(open => !open)} aria-expanded={profileMenuOpen} aria-haspopup="menu" aria-label="Open account menu" className="flex items-center gap-2 rounded-xl p-1 text-left transition hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-extrabold text-[#064e3b] shadow-sm">{user?.name ? user.name.slice(0, 2).toUpperCase() : "AV"}</span>
                <span className="hidden sm:block">
                  <span className="block text-xs font-bold leading-tight">{user?.name || "Guest Farmer"}</span>
                  <span className="block text-[10px] capitalize text-muted-foreground">{user?.role || "Guest"}</span>
                </span>
                <ChevronDown size={13} className="hidden text-muted-foreground sm:block" />
              </button>
              {profileMenuOpen && (
                <div role="menu" className="absolute right-0 top-full z-50 mt-2 w-48 rounded-2xl border border-border bg-card p-1.5 text-foreground shadow-xl">
                  {user ? (
                    <>
                      <Link to="/settings" role="menuitem" onClick={() => setProfileMenuOpen(false)} className="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-xs font-semibold hover:bg-muted"><Settings size={15} /> Account settings</Link>
                      <button type="button" role="menuitem" onClick={async () => { setProfileMenuOpen(false); await logout(); navigate("/login", { replace: true }) }} className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-left text-xs font-semibold text-red-600 hover:bg-red-500/10"><LogOut size={15} /> Sign out</button>
                    </>
                  ) : (
                    <Link to="/login" role="menuitem" onClick={() => setProfileMenuOpen(false)} className="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-xs font-semibold hover:bg-muted">Sign in</Link>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main id="main-content" tabIndex={-1} className="flex-1 overflow-y-auto page-enter bg-background outline-none">
          {children}
        </main>

        {/* Global Spotlight Command Palette Modal */}
        <CommandPalette isOpen={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
      </div>
    </div>
  )
}
