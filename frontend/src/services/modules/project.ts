/**
 * Project service — API module placeholder (no implementation).
 */
import { apiClient } from "@/services/api/client"
import type { Project } from "@/types"

export const projectService = {
  async list(): Promise<Project[]> {
    return apiClient.request("/projects")
  },
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  async get(_projectId: string): Promise<Project> {
    return apiClient.request("/projects/{id}")
  },
}
