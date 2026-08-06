import { createContext, useContext, useMemo, type ReactNode } from "react"

import {
  APP_NAME,
  APP_TAGLINE,
  APP_VERSION,
  DEFAULT_ENVIRONMENT,
} from "@/constants"

/** Static platform metadata surfaced in the shell (navbar/footer). */
interface AppContextValue {
  appName: string
  tagline: string
  version: string
  environment: string
  // TODO(phase-2): user, tenant and feature flags will be resolved here.
}

const AppContext = createContext<AppContextValue | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const value = useMemo<AppContextValue>(
    () => ({
      appName: APP_NAME,
      tagline: APP_TAGLINE,
      version: APP_VERSION,
      environment: import.meta.env.VITE_ENVIRONMENT ?? DEFAULT_ENVIRONMENT,
    }),
    [],
  )
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp(): AppContextValue {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error("useApp must be used within an AppProvider")
  return ctx
}
