/**
 * Repository service — API module placeholder (no implementation).
 * Phase 2/3: upload tarball, fetch scan index, subscribe to scan progress.
 */
import { apiClient } from "@/services/api/client"
import type { Repository } from "@/types"

export const repositoryService = {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async upload(_file: File): Promise<{ repository: Repository; reviewId: string }> {
    return apiClient.request("/repositories", { method: "POST" })
  },
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async get(_repositoryId: string): Promise<Repository> {
    return apiClient.request("/repositories/{id}")
  },
}
