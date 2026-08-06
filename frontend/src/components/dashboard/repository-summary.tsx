import { FolderGit2, FileCode2, GitBranch } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Panel } from "@/components/ui/panel"
import { Skeleton } from "@/components/ui/skeleton"

/**
 * Repository summary — what is under review.
 * Phase 3: filled by the Repository Service after upload/scan.
 */
export function RepositorySummary() {
  return (
    <Panel
      icon={FolderGit2}
      title="Repository Summary"
      description="Target under review"
      className="xl:col-span-4"
      action={<Badge variant="outline">Awaiting upload</Badge>}
    >
      <div className="space-y-4">
        <div>
          <p className="font-mono text-sm font-medium text-muted-foreground">
            ~/acme-app
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {["TypeScript", "Python", "Go"].map((lang) => (
              <Badge key={lang} variant="secondary">
                {lang}
              </Badge>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-md border border-border bg-muted/30 p-3">
            <span className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-muted-foreground">
              <FileCode2 className="h-3 w-3" /> Files
            </span>
            <Skeleton className="mt-2 h-4 w-10" />
          </div>
          <div className="rounded-md border border-border bg-muted/30 p-3">
            <span className="flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-muted-foreground">
              <GitBranch className="h-3 w-3" /> Branch
            </span>
            <Skeleton className="mt-2 h-4 w-14" />
          </div>
        </div>

        <p className="text-xs leading-relaxed text-muted-foreground">
          Scan results, language statistics and the file index will appear
          here once a repository is uploaded.
        </p>
      </div>
    </Panel>
  )
}
