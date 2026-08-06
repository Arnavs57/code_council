/**
 * Auth service — API module placeholder (no implementation).
 * Phase 2: login/refresh/logout backed by the backend auth endpoints.
 */
import { apiClient } from "@/services/api/client"
import type { User } from "@/types"

export interface LoginCredentials {
  email: string
  password: string
}

export const authService = {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async login(_credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    return apiClient.request("/auth/login", { method: "POST" })
  },
  async logout(): Promise<void> {
    return apiClient.request("/auth/logout", { method: "POST" })
  },
  async me(): Promise<User> {
    return apiClient.request("/auth/me")
  },
}
