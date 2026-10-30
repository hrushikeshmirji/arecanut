import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react"
import { safeGetJSON, safeSetJSON } from "../utils/safeStorage"
import { DEFAULT_NOTIFS, markAllNotificationsReadApi, markNotificationReadApi } from "../services/notificationService"

export interface NotificationItem {
  id: string
  type: "critical" | "warning" | "info"
  title: string
  msg: string
  time: string
  unread: boolean
  blockId?: string
}

interface NotificationContextType {
  notifications: NotificationItem[]
  unreadCount: number
  markAllRead: () => void
  markAsRead: (id: string) => void
  addNotification: (item: Omit<NotificationItem, "id" | "time" | "unread">) => void
}

const STORAGE_KEY = "arecavision_notifications"

const NotificationContext = createContext<NotificationContextType>({
  notifications: DEFAULT_NOTIFS,
  unreadCount: 2,
  markAllRead: () => null,
  markAsRead: () => null,
  addNotification: () => null,
})

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>(() => {
    const loaded = safeGetJSON<NotificationItem[]>(STORAGE_KEY, DEFAULT_NOTIFS, Array.isArray)
    // Filter out temporary network disconnect artifacts from past offline testing
    const cleaned = loaded.filter(
      (n) => !(n.title === "Scan Failed" && (n.msg?.includes("Failed to fetch") || n.msg?.includes("Network Error") || n.msg?.includes("connect to backend")))
    )
    return cleaned.length > 0 ? cleaned : DEFAULT_NOTIFS
  })

  useEffect(() => {
    safeSetJSON(STORAGE_KEY, notifications)
  }, [notifications])

  const unreadCount = notifications.filter((n) => n.unread).length

  const markAllRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, unread: false })))
    markAllNotificationsReadApi().catch((err) => {
      console.error("Failed to sync mark all read to backend:", err)
    })
  }, [])

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, unread: false } : n))
    )
    markNotificationReadApi(id).catch((err) => {
      console.error("Failed to sync mark notification read to backend:", err)
    })
  }, [])

  const addNotification = useCallback((item: Omit<NotificationItem, "id" | "time" | "unread">) => {
    const newItem: NotificationItem = {
      ...item,
      id: "notif-" + Date.now(),
      time: "Just now",
      unread: true,
    }
    setNotifications((prev) => [newItem, ...prev])
  }, [])

  const contextValue = useMemo(() => ({
    notifications,
    unreadCount,
    markAllRead,
    markAsRead,
    addNotification
  }), [notifications, unreadCount, markAllRead, markAsRead, addNotification])

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  )
}

export const useNotifications = () => useContext(NotificationContext)
