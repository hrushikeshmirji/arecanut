import { useEffect, useState } from "react"
import type { CSSProperties } from "react"
import { useTheme } from "../contexts/ThemeProvider"

export function useArecaPalette(): CSSProperties {
  const { theme } = useTheme()
  const [systemDark, setSystemDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)
  const isDark = theme === "dark" || (theme === "system" && systemDark)

  useEffect(() => {
    if (theme !== "system") return
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches)
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [theme])

  return {
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
}
