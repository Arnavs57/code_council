import { createContext, useContext, useMemo, type ReactNode } from "react"

import type { Repository } from "@/types"

/**
 * Repository context.
 *
 * Phase 2/3: owns the repository being reviewed (index, language stats,
 * scan progress). Foundation placeholder — components render from static
 * demo data instead of live state.
 */
interface RepositoryContextValue {
  repository: Repository | null
  /** TODO(phase-2): set by the Repository Service after upload/selection. */
}

const RepositoryContext = createContext<RepositoryContextValue | undefined>(
  undefined,
)

export function RepositoryProvider({ children }: { children: ReactNode }) {
  const value = useMemo<RepositoryContextValue>(() => ({ repository: null }), [])
  return (
    <RepositoryContext.Provider value={value}>{children}</RepositoryContext.Provider>
  )
}

export function useRepository(): RepositoryContextValue {
  const ctx = useContext(RepositoryContext)
  if (!ctx) {
    throw new Error("useRepository must be used within a RepositoryProvider")
  }
  return ctx
}
