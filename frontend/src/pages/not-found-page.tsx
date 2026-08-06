import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { ContentWrapper } from "@/components/layout/content-wrapper"
import { PageHeader } from "@/components/layout/page-header"

export function NotFoundPage() {
  return (
    <ContentWrapper>
      <PageHeader title="404 — Sector not found" description="The page you requested does not exist in this control room." />
      <div className="flex items-center gap-3">
        <Button asChild>
          <Link to="/">Return to Mission Control</Link>
        </Button>
      </div>
    </ContentWrapper>
  )
}
