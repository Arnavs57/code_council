import { GitPullRequestArrow } from "lucide-react"

import { ContentWrapper } from "@/components/layout/content-wrapper"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/ui/empty-state"
import { Panel } from "@/components/ui/panel"

export function RepositoryReviewPage() {
  return (
    <ContentWrapper>
      <PageHeader
        title="Repository Review"
        description="Start a new review run or open a running one."
        action={
          <Button disabled>
            <GitPullRequestArrow className="h-4 w-4" />
            Upload repository
          </Button>
        }
      />
      <Panel
        icon={GitPullRequestArrow}
        title="Review runs"
        description="Placeholder — upload flow comes online in the next phase"
      >
        <EmptyState
          icon={GitPullRequestArrow}
          title="No review runs"
          description="Once upload is enabled, runs will list here and open into the Mission Control dashboard."
        />
      </Panel>
    </ContentWrapper>
  )
}
