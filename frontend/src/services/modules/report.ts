/**
 * Report service — API module placeholder (no implementation).
 * Phase 3: decision summaries and evidence packs.
 */
import { apiClient } from "@/services/api/client"

export interface DecisionReport {
  verdict: string
  summary: string
  scoreBreakdown: Record<string, number>
  evidenceIds: string[]
}

export const reportService = {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async getDecision(_reviewId: string): Promise<DecisionReport> {
    return apiClient.request("/reviews/{id}/decision")
  },
}
