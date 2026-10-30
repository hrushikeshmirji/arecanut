import { useState } from "react"
import { Link } from "react-router-dom"
import {
  Sun,
  Moon,
  Globe,
  Trash2,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Lock,
  User,
  Shield,
  KeyRound,
  Database,
  Activity,
  Server,
  ExternalLink,
} from "lucide-react"
import { useTheme } from "../contexts/ThemeProvider"
import { useLanguage, Language } from "../contexts/LanguageContext"
import { useScanHistory } from "../contexts/ScanHistoryContext"
import { useAuth } from "../contexts/AuthContext"
import { useFocusTrap } from "../hooks/useFocusTrap"
import { apiRequest } from "../services/apiClient"
import { useArecaPalette } from "../hooks/useArecaPalette"

export default function Settings() {
  const { theme, setTheme } = useTheme()
  const { language, setLanguage, t } = useLanguage()
  const { clearHistory, scans } = useScanHistory()
  const { user, updateProfile } = useAuth()
  const pagePalette = useArecaPalette()

  const [showConfirmClear, setShowConfirmClear] = useState(false)
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Password Change State
  const [oldPassword, setOldPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [changingPassword, setChangingPassword] = useState(false)
  const [profileName, setProfileName] = useState(user?.name || "")
  const [profileUsername, setProfileUsername] = useState(user?.username || "")
  const [profileEmail, setProfileEmail] = useState(user?.email || "")
  const [savingProfile, setSavingProfile] = useState(false)

  const handleProfileSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setErrorMessage(null)
    setFeedbackMessage(null)
    setSavingProfile(true)
    try {
      await updateProfile({ name: profileName.trim(), username: profileUsername.trim(), email: profileEmail.trim() })
      setFeedbackMessage("Profile updated successfully.")
      setTimeout(() => setFeedbackMessage(null), 4000)
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Unable to update your profile.")
    } finally {
      setSavingProfile(false)
    }
  }


  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)
    setFeedbackMessage(null)

    if (newPassword.length < 6) {
      setErrorMessage("New password must be at least 6 characters.")
      return
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage("New passwords do not match.")
      return
    }

    setChangingPassword(true)
    try {
      const res = await apiRequest<{ message: string }>("/auth/password", {
        method: "POST",
        body: JSON.stringify({ oldPassword, newPassword }),
      })
      setFeedbackMessage(res?.message || "Password updated successfully.")
      setOldPassword("")
      setNewPassword("")
      setConfirmPassword("")
      setTimeout(() => setFeedbackMessage(null), 4000)
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to update password.")
    } finally {
      setChangingPassword(false)
    }
  }

  const confirmModalRef = useFocusTrap<HTMLDivElement>({
    isOpen: showConfirmClear,
    onClose: () => setShowConfirmClear(false),
  })

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-5 text-foreground sm:p-6 lg:p-8" style={pagePalette}>
      <div className="border-b border-border/80 pb-5">
        <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.16em] text-primary">Account and preferences</p>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">{t("settings.title", "System Settings & Security")}</h1>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          {t("settings.subtitle", "Account security, model parameters, and application preferences")}
        </p>
      </div>

      {feedbackMessage && (
        <div className="p-3 bg-primary/10 border border-primary/25 rounded-xl flex items-center justify-between text-xs text-primary animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={16} />
            <span className="font-semibold">{feedbackMessage}</span>
          </div>
          <button onClick={() => setFeedbackMessage(null)} className="text-primary hover:opacity-80 text-sm font-bold">
            ✕
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="p-3 bg-danger/10 border border-danger/25 rounded-xl flex items-center justify-between text-xs text-danger animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} />
            <span className="font-semibold">{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-danger hover:opacity-80 text-sm font-bold">
            ✕
          </button>
        </div>
      )}

      <div className="space-y-7">
        {/* Account Profile & Role */}
        <div className="p-6 rounded-2xl bg-card border border-border shadow-sm space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                <User size={18} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-foreground">User Profile</h3>
                <p className="text-[11px] text-muted-foreground">Session authentication and account credentials</p>
              </div>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary/10 text-primary border border-primary/25 uppercase">
              {user?.role || "Farmer"} Account
            </span>
          </div>

          <form onSubmit={handleProfileSubmit} className="space-y-4 border-t border-border pt-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <label className="text-[11px] font-semibold text-muted-foreground">Display name<input required maxLength={80} value={profileName} onChange={e => setProfileName(e.target.value)} className="mt-1.5 w-full rounded-xl border border-border bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary" /></label>
              <label className="text-[11px] font-semibold text-muted-foreground">Username<input required minLength={3} maxLength={32} pattern="[A-Za-z0-9._-]+" value={profileUsername} onChange={e => setProfileUsername(e.target.value)} className="mt-1.5 w-full rounded-xl border border-border bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary" /></label>
              <label className="text-[11px] font-semibold text-muted-foreground">Email address<input required type="email" value={profileEmail} onChange={e => setProfileEmail(e.target.value)} className="mt-1.5 w-full rounded-xl border border-border bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary" /></label>
            </div>
            <div className="flex justify-end"><button type="submit" disabled={savingProfile} className="btn-primary px-4 py-2 text-xs">{savingProfile ? "Saving…" : "Save profile"}</button></div>
          </form>
        </div>

        {/* Password & Security */}
        <div className="p-6 rounded-2xl bg-card border border-border shadow-sm space-y-5">
          <div className="flex items-center gap-2 text-sm font-bold text-foreground">
            <KeyRound size={18} className="text-primary" />
            <span>Change Account Password</span>
          </div>

          <form onSubmit={handlePasswordSubmit} className="pt-2 border-t border-border space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="text-[11px] font-semibold text-muted-foreground block mb-1">Current Password</label>
                <input
                  type="password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-background border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-muted-foreground block mb-1">New Password (min 6 chars)</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-background border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>

              <div>
                <label className="text-[11px] font-semibold text-muted-foreground block mb-1">Confirm New Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-background border border-border rounded-xl px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <button
                type="submit"
                disabled={changingPassword || !oldPassword || !newPassword}
                className="btn-primary text-xs px-4 py-2"
              >
                {changingPassword ? "Updating..." : "Update Password"}
              </button>
            </div>
          </form>
        </div>

        {/* Telemetry & Model Infrastructure */}
        <div className="p-5 rounded-2xl bg-card border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-bold text-foreground">
              <Cpu size={18} className="text-primary" />
              <span>AI Model & Telemetry Diagnostics</span>
            </div>
            <Link
              to="/research"
              className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
            >
              <span>View Technical Benchmarks</span>
              <ExternalLink size={12} />
            </Link>
          </div>

          <div className="pt-2 border-t border-border grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-background border border-border space-y-1">
              <span className="text-[11px] font-bold text-muted-foreground uppercase">Stage 1 Gatekeeper</span>
              <div className="font-bold text-foreground">CNN Domain Defense</div>
              <span className="text-[10px] text-primary flex items-center gap-1 font-semibold">
                <CheckCircle2 size={12} /> Active (98.6% Acc)
              </span>
            </div>

            <div className="p-3 rounded-xl bg-background border border-border space-y-1">
              <span className="text-[11px] font-bold text-muted-foreground uppercase">Stage 2 Detector</span>
              <div className="font-bold text-foreground">YOLOv8 Lesion BBox</div>
              <span className="text-[10px] text-primary flex items-center gap-1 font-semibold">
                <CheckCircle2 size={12} /> Loaded (best.pt)
              </span>
            </div>

            <div className="p-3 rounded-xl bg-background border border-border space-y-1">
              <span className="text-[11px] font-bold text-muted-foreground uppercase">Stage 3 Classifier</span>
              <div className="font-bold text-foreground">ViT-B/16 Classifier v4</div>
              <span className="text-[10px] text-primary flex items-center gap-1 font-semibold">
                <CheckCircle2 size={12} /> Active (98.6% Acc)
              </span>
            </div>
          </div>
        </div>

        {/* Appearance & Theme */}
        <div className="p-5 rounded-2xl bg-card border border-border shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-foreground">
            <Sun size={18} className="text-primary" />
            <span>{t("settings.appearance", "Appearance")}</span>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-border">
            <div>
              <div className="text-xs font-semibold text-foreground">{t("settings.dark_mode", "Dark Mode")}</div>
              <div className="text-[11px] text-muted-foreground">{t("settings.theme_desc", "Toggle between light and dark visual themes")}</div>
            </div>

            <div className="flex items-center gap-1 bg-muted p-1 rounded-xl">
              <button
                onClick={() => setTheme("light")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  theme === "light" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
                }`}
              >
                <Sun size={14} /> {t("settings.light_mode", "Light")}
              </button>
              <button
                onClick={() => setTheme("dark")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  theme === "dark" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
                }`}
              >
                <Moon size={14} /> {t("settings.dark_theme", "Dark")}
              </button>
            </div>
          </div>
        </div>

        {/* Language */}
        <div className="p-5 rounded-2xl bg-card border border-border shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-sm font-bold text-foreground">
            <Globe size={18} className="text-primary" />
            <span>{t("settings.language", "Display Language")}</span>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-border">
            <div>
              <div className="text-xs font-semibold text-foreground">{t("settings.app_lang", "Application Language")}</div>
              <div className="text-[11px] text-muted-foreground">{t("settings.lang_desc", "Applies instant translations across all screens")}</div>
            </div>

            <div className="flex items-center gap-1.5 bg-muted p-1 rounded-xl">
              <button
                onClick={() => setLanguage("en")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  language === "en" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage("kn")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  language === "kn" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
                }`}
              >
                ಕನ್ನಡ
              </button>
              <button
                onClick={() => setLanguage("hi")}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  language === "hi" ? "bg-card text-foreground shadow-sm" : "text-muted-foreground"
                }`}
              >
                हिंदी
              </button>
            </div>
          </div>
        </div>

        {/* Scan Data Cache Management */}
        <div className="p-5 rounded-2xl bg-card border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-foreground">{t("settings.clear_data", "Clear Local Scan Cache")}</div>
              <div className="text-xs text-muted-foreground mt-0.5">
                {t("settings.storing_prefix", "Currently storing")} {scans.length} {t("settings.storing_suffix", "cached scans locally.")}
              </div>
            </div>

            <button
              onClick={() => setShowConfirmClear(true)}
              disabled={scans.length === 0}
              className="px-3 py-2 rounded-xl text-xs font-bold text-danger bg-danger/10 hover:bg-danger/20 disabled:opacity-40 transition-colors flex items-center gap-1.5"
            >
              <Trash2 size={14} /> {t("settings.clear_all_btn", "Clear Cache")}
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmClear && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div
            ref={confirmModalRef}
            tabIndex={-1}
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-clear-title"
            className="bg-card border border-border rounded-2xl p-6 max-w-sm w-full space-y-4 shadow-2xl"
          >
            <div className="w-12 h-12 rounded-full bg-danger/10 text-danger flex items-center justify-center mx-auto">
              <AlertTriangle size={24} />
            </div>
            <div className="text-center space-y-1">
              <h2 id="confirm-clear-title" className="text-base font-bold text-foreground">
                {t("scans.confirm_clear_title", "Clear scan cache?")}
              </h2>
              <p className="text-xs text-muted-foreground">
                {t("scans.confirm_clear_desc", "Are you sure you want to clear your local cache? Server records in SQLite will remain preserved.")}
              </p>
            </div>
            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setShowConfirmClear(false)}
                className="flex-1 py-2 px-3 border border-border rounded-xl text-xs font-semibold text-foreground hover:bg-muted transition-colors"
              >
                {t("scans.confirm_cancel_btn", "Cancel")}
              </button>
              <button
                onClick={() => {
                  clearHistory()
                  setShowConfirmClear(false)
                  setFeedbackMessage(t("scans.history_cleared", "Scan cache successfully cleared."))
                  setTimeout(() => setFeedbackMessage(null), 4000)
                }}
                className="flex-1 py-2 px-3 bg-danger hover:bg-danger/90 text-white rounded-xl text-xs font-bold transition-colors shadow-sm"
              >
                {t("scans.confirm_clear_btn", "Yes, Clear Cache")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
