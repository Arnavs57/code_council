import { createContext, useContext, useMemo, useState, type ReactNode } from "react"

import type { ReviewStatus } from "@/types"

/**
 * Dashboard (mission control) state.
 *
 * Phase 2/3: this context will own the LIVE run projection — the event
 * stream reducer, current review id, scan progress and phase transitions.
 * For the foundation it only carries a status so components can demo
 * different states without business logic.
 */
interface DashboardContextValue {
  status: ReviewStatus
  /** TODO(phase-3): set from the live WebSocket stream. */
  setStatus: (status: ReviewStatus) => void
  /** TODO(phase-3): active review id once runs exist. */
  activeReviewId: string | null
}

const DashboardContext = createContext<DashboardContextValue | undefined>(undefined)

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<ReviewStatus>("planning")
  const value = useMemo(
    () => ({ status, setStatus, activeReviewId: null }),
    [status],
  )
  return (
    <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>
  )
}

export function useDashboard(): DashboardContextValue {
  const ctx = useContext(DashboardContext)
  if (!ctx) throw new Error("useDashboard must be used within a DashboardProvider")
  return ctx
}
