import { BrowserRouter, Route, Routes } from "react-router-dom"

import { AppLayout } from "@/components/layout/app-layout"
import { AppProviders } from "@/contexts"
import { ActivityPage } from "@/pages/activity-page"
import { DashboardPage } from "@/pages/dashboard-page"
import { NotFoundPage } from "@/pages/not-found-page"
import { ProjectsPage } from "@/pages/projects-page"
import { ReportsPage } from "@/pages/reports-page"
import { RepositoryReviewPage } from "@/pages/repository-review-page"
import { SettingsPage } from "@/pages/settings-page"

export function App() {
  return (
    <AppProviders>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/review" element={<RepositoryReviewPage />} />
            <Route path="/activity" element={<ActivityPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProviders>
  )
}
