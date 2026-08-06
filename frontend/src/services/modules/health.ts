/**
 * Health service — API module placeholder (no implementation).
 * Phase 2: /health probe drives the System Health panel.
 */
import { apiClient } from "@/services/api/client"

export interface HealthStatus {
  app_name: string
  version: string
  status: string
  timestamp: string
  environment: string
}

export const healthService = {
  async get(): Promise<HealthStatus> {
    return apiClient.request("/health")
  },
}
