import { apiRequest, AUTH_TOKEN_KEY } from "./apiClient"
import { AuthResponse, LoginRequest, RegisterRequest, UserTokenPayload } from "../types/api"
import { safeGetItem, safeSetItem, safeRemoveItem } from "../utils/safeStorage"

/**
 * TOKEN STORAGE ARCHITECTURAL DECISION & TRADEOFF NOTE:
 * 
 * Production Recommendation: httpOnly Cookies
 * Using httpOnly, SameSite=Strict cookies is the standard recommended strategy for production backends
 * because it eliminates XSS token exfiltration risk. The browser automatically handles cookie transmission.
 * 
 * Current Development Strategy (Bearer / Memory / Fallback):
 * For API development flexibility, when Bearer authentication token is returned by `/auth/login`,
 * it is stored in `localStorage` under `arecavision_auth_token` and attached in `Authorization` headers.
 * When real backend transitions to httpOnly cookies, `localStorage` calls can be omitted with zero UI changes.
 */

const STORAGE_TOKEN_KEY = AUTH_TOKEN_KEY
const STORAGE_USER_KEY = "arecavision_auth_user"
const DEMO_AUTH_ENABLED = import.meta.env.VITE_DEMO_AUTH === "true"

function createDemoUser(email: string): UserTokenPayload {
  return {
    id: "demo-farmer",
    username: "farmer",
    name: "Ramesh Gowda",
    email,
    role: "farmer",
  }
}

export async function loginUser(credentials: LoginRequest): Promise<AuthResponse> {
  if (DEMO_AUTH_ENABLED) {
    // Demo-only shortcut: accept any entered values and always open the default farmer profile.
    void credentials
    safeRemoveItem(STORAGE_TOKEN_KEY)
    const user = createDemoUser("farmer@arecavision.ai")
    safeSetItem(STORAGE_USER_KEY, JSON.stringify(user))
    return { user }
  }

  const res = await apiRequest<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
    forceReal: true,
  })

  if (res.token) {
    safeSetItem(STORAGE_TOKEN_KEY, res.token)
  }
  safeSetItem(STORAGE_USER_KEY, JSON.stringify(res.user))
  return res
}

export async function registerUser(data: RegisterRequest): Promise<AuthResponse> {
  if (DEMO_AUTH_ENABLED) {
    throw new Error("Registration is unavailable in frontend demo mode.")
  }

  const res = await apiRequest<AuthResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
    forceReal: true,
  })

  if (res.token) {
    safeSetItem(STORAGE_TOKEN_KEY, res.token)
  }
  safeSetItem(STORAGE_USER_KEY, JSON.stringify(res.user))
  return res
}

export async function updateUserProfile(data: Pick<UserTokenPayload, "username" | "email" | "name">): Promise<UserTokenPayload> {
  if (DEMO_AUTH_ENABLED) {
    const currentUser = getStoredUser()
    if (!currentUser || currentUser.id !== "demo-farmer") throw new Error("Demo session not found. Please sign in again.")
    const updatedUser = { ...currentUser, ...data }
    safeSetItem(STORAGE_USER_KEY, JSON.stringify(updatedUser))
    return updatedUser
  }

  const user = await apiRequest<UserTokenPayload>("/auth/me", {
    method: "PUT",
    body: JSON.stringify(data),
    forceReal: true,
  })
  safeSetItem(STORAGE_USER_KEY, JSON.stringify(user))
  return user
}

export async function logoutUser(): Promise<void> {
  if (DEMO_AUTH_ENABLED) {
    safeRemoveItem(STORAGE_TOKEN_KEY)
    safeRemoveItem(STORAGE_USER_KEY)
    return
  }

  try {
    await apiRequest<void>("/auth/logout", {
      method: "POST",
      forceReal: true,
    })
  } catch {
    // Ignore backend logout errors during offline/mock cleanup
  } finally {
    safeRemoveItem(STORAGE_TOKEN_KEY)
    safeRemoveItem(STORAGE_USER_KEY)
  }
}

export async function refreshUserSession(): Promise<AuthResponse | null> {
  const savedUser = safeGetItem(STORAGE_USER_KEY)
  if (!savedUser) return null

  if (DEMO_AUTH_ENABLED) {
    try {
      const user = JSON.parse(savedUser) as UserTokenPayload
      if (user.id !== "demo-farmer" || user.role !== "farmer") return null
      return { user }
    } catch {
      safeRemoveItem(STORAGE_USER_KEY)
      return null
    }
  }

  try {
    const res = await apiRequest<AuthResponse>("/auth/refresh", {
      method: "POST",
      forceReal: true,
    })

    if (res.token) {
      safeSetItem(STORAGE_TOKEN_KEY, res.token)
    }
    safeSetItem(STORAGE_USER_KEY, JSON.stringify(res.user))
    return res
  } catch {
    safeRemoveItem(STORAGE_TOKEN_KEY)
    safeRemoveItem(STORAGE_USER_KEY)
    return null
  }
}

export function getStoredUser(): UserTokenPayload | null {
  try {
    const savedUser = safeGetItem(STORAGE_USER_KEY)
    return savedUser ? JSON.parse(savedUser) : null
  } catch {
    return null
  }
}
