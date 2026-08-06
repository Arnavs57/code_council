import type { ReactNode } from "react"

import { AgentProvider } from "@/contexts/agent-context"
import { AppProvider } from "@/contexts/app-context"
import { DashboardProvider } from "@/contexts/dashboard-context"
import { RepositoryProvider } from "@/contexts/repository-context"
import { ThemeProvider } from "@/contexts/theme-context"

/**
 * Root provider tree. Order matters: theme is outermost (no dependencies),
 * app metadata next, then the feature placeholders.
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <AppProvider>
        <DashboardProvider>
          <AgentProvider>
            <RepositoryProvider>{children}</RepositoryProvider>
          </AgentProvider>
        </DashboardProvider>
      </AppProvider>
    </ThemeProvider>
  )
}
