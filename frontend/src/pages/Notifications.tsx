import { Check, ShieldAlert, Info, AlertTriangle, CheckCircle2 } from "lucide-react"
import { useNotifications } from "../contexts/NotificationContext"
import { useLanguage } from "../contexts/LanguageContext"
import { useArecaPalette } from "../hooks/useArecaPalette"

export default function Notifications() {
  const { notifications, markAllRead, markAsRead } = useNotifications()
  const { t } = useLanguage()
  const pagePalette = useArecaPalette()

  const hasUnread = notifications.some((n) => n.unread)

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-5 text-foreground sm:p-6 lg:p-8" style={pagePalette}>
      <div className="flex items-end justify-between gap-4 border-b border-border/80 pb-5">
        <div>
          <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.16em] text-primary">Field updates</p>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">{t("nav.notifications", "Notifications")}</h1>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">{t("notif.subtitle", "Alerts and updates from your plantation")}</p>
        </div>

        {notifications.length > 0 && (
          <button
            onClick={markAllRead}
            disabled={!hasUnread}
            className="btn-secondary text-xs flex items-center gap-1.5 disabled:opacity-40 disabled:pointer-events-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none"
          >
            <Check size={14} /> {t("notif.mark_all_read", "Mark All Read")}
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="bg-card rounded-2xl border border-border p-12 text-center flex flex-col items-center justify-center min-h-[360px]">
          <div className="w-16 h-16 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-4 shadow-sm">
            <CheckCircle2 size={32} />
          </div>
          <h2 className="text-lg font-bold text-foreground mb-1.5">
            {t("notif.empty_title", "You're all caught up")}
          </h2>
          <p className="text-xs text-muted-foreground max-w-sm leading-relaxed">
            {t("notif.empty_desc", "No active alerts or system notifications at this time.")}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {notifications.map((n) => (
            <div
              key={n.id}
              role="button"
              tabIndex={0}
              onClick={() => markAsRead(n.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault()
                  markAsRead(n.id)
                }
              }}
              className={`p-5 rounded-2xl border flex items-start gap-4 transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-primary focus-visible:outline-none ${
                n.unread ? "bg-card border-primary/40 shadow-sm" : "bg-card/60 border-border opacity-80"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                  n.type === "critical"
                    ? "bg-danger/10 text-danger"
                    : n.type === "warning"
                    ? "bg-warning/10 text-warning"
                    : "bg-primary/10 text-primary"
                }`}
              >
                {n.type === "critical" ? (
                  <AlertTriangle size={16} />
                ) : n.type === "warning" ? (
                  <ShieldAlert size={16} />
                ) : (
                  <Info size={16} />
                )}
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-foreground">{n.title}</h3>
                  <span className="text-[10px] text-muted-foreground">{n.time}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">{n.msg}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
