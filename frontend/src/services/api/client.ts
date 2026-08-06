/**
 * REST client — architecture only. No implementation in this phase.
 *
 * Phase 2: a thin typed wrapper around fetch (or TanStack Query) that
 * attaches the auth token, base URL and error normalization. All module
 * services (auth.ts, repository.ts, ...) will build on this one client.
 */

export interface ApiClientConfig {
  baseUrl: string
  /** TODO(phase-2): token provider (from Auth context / storage). */
  getAccessToken?: () => Promise<string | null>
  timeoutMs?: number
}

export class ApiClient {
  constructor(private readonly config: ApiClientConfig) {}

  /**
   * Generic request. Throws until Phase 2 wires the transport.
   * TODO(phase-2): implement fetch wrapper, retries, error mapping.
   */
  async request<T>(path: string, init?: RequestInit): Promise<T> {
    // Reference the wiring so the contract stays visible even without a
    // transport; path/config/init are consumed here in Phase 2.
    void path
    void init
    throw new Error(
      `ApiClient is a placeholder (base: ${this.config.baseUrl}) — implemented in Phase 2`,
    )
  }
}

/** Shared instance — configured from env once the backend exists. */
export const apiClient = new ApiClient({
  baseUrl: import.meta.env.VITE_API_BASE_URL ?? "/api/v1",
})
