import { Outlet } from "react-router-dom"

import { ActivityPanel } from "@/components/layout/activity-panel"
import { Footer } from "@/components/layout/footer"
import { Navbar } from "@/components/layout/navbar"
import { PageContainer } from "@/components/layout/page-container"
import { Sidebar } from "@/components/layout/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"

/**
 * Application shell.
 *
 *   ┌─────────────── Navbar ───────────────┐
 *   │ Sidebar │  Page (Outlet)   │ Activity │
 *   ├───────────────────────────────────────┤
 *   │               Footer                  │
 *
 * The right rail is intentionally hidden below `xl` so the main dashboard
 * keeps priority on laptop screens; the layout is a fixed frame around
 * route content rendered through the Outlet.
 */
export function AppLayout() {
  return (
    <TooltipProvider>
      <div className="flex h-dvh flex-col overflow-hidden">
        <Navbar />
        <div className="flex min-h-0 flex-1">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <PageContainer>
              <Outlet />
            </PageContainer>
          </div>
          <ActivityPanel />
        </div>
        <Footer />
      </div>
    </TooltipProvider>
  )
}
