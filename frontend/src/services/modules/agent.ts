/**
 * Agent service — API module placeholder (no implementation).
 * Phase 3: agent metadata, budgets, tool grants. Live status arrives over
 * the WebSocket stream, not REST.
 */
import { apiClient } from "@/services/api/client"
import type { Agent } from "@/types"

export const agentService = {
  async list(): Promise<Agent[]> {
    return apiClient.request("/agents")
  },
}
