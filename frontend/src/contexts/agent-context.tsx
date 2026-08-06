import { createContext, useContext, useMemo, type ReactNode } from "react"

import { AGENT_ROLES, type AgentRole } from "@/constants"
import type { AgentStatus } from "@/types"

/**
 * Agent board state.
 *
 * Phase 3: populated from the live event stream (AgentStarted /
 * AgentHeartbeat / AgentFinished). For the foundation it exposes the
 * registry of roles and a default idle status per role.
 */
interface AgentContextValue {
  roles: readonly AgentRole[]
  /** TODO(phase-3): status map keyed by role, fed by the event reducer. */
  defaultStatus: AgentStatus
  labelFor: (role: AgentRole) => string
}

const AgentContext = createContext<AgentContextValue | undefined>(undefined)

export function AgentProvider({ children }: { children: ReactNode }) {
  const value = useMemo<AgentContextValue>(
    () => ({
      roles: AGENT_ROLES.map((entry) => entry.role),
      defaultStatus: "idle",
      labelFor: (role) =>
        AGENT_ROLES.find((entry) => entry.role === role)?.label ?? role,
    }),
    [],
  )
  return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>
}

export function useAgents(): AgentContextValue {
  const ctx = useContext(AgentContext)
  if (!ctx) throw new Error("useAgents must be used within an AgentProvider")
  return ctx
}
