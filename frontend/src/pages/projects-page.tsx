import { FolderKanban } from "lucide-react"

import { ContentWrapper } from "@/components/layout/content-wrapper"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/ui/empty-state"
import { Panel } from "@/components/ui/panel"

export function ProjectsPage() {
  return (
    <ContentWrapper>
      <PageHeader
        title="Projects"
        description="Repositories and teams under governance."
        action={
          <Button variant="outline" disabled>
            New project
          </Button>
        }
      />
      <Panel icon={FolderKanban} title="Projects" description="Placeholder">
        <EmptyState
          icon={FolderKanban}
          title="No projects yet"
          description="Project management arrives with the repository upload flow in a later phase."
        />
      </Panel>
    </ContentWrapper>
  )
}
