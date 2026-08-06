import { File, FileCode2, Folder, FolderOpen, GitBranch } from "lucide-react"

import { Panel } from "@/components/ui/panel"

const TREE = [
  { kind: "folder", name: "src", depth: 0, open: true },
  { kind: "folder", name: "services", depth: 1, open: false },
  { kind: "file", name: "auth.ts", depth: 2 },
  { kind: "file", name: "api.ts", depth: 2 },
  { kind: "folder", name: "tests", depth: 1, open: false },
  { kind: "file", name: "pyproject.toml", depth: 0 },
  { kind: "file", name: "Dockerfile", depth: 0 },
] as const

/**
 * Repository explorer — the file tree being scanned.
 * Phase 3: backed by the scan index; rows will show scan status, language
 * and per-file findings badges.
 */
export function RepoExplorer() {
  return (
    <Panel
      icon={GitBranch}
      title="Repository Explorer"
      description="File tree under review"
      className="xl:col-span-4"
    >
      <ul className="space-y-0.5 font-mono text-[13px]">
        {TREE.map((entry, index) => (
          <li
            key={index}
            className="flex items-center gap-2 rounded px-2 py-1 text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground"
            style={{ paddingLeft: `${12 + entry.depth * 16}px` }}
          >
            {entry.kind === "folder" ? (
              entry.open ? (
                <FolderOpen className="h-3.5 w-3.5 shrink-0 text-info/80" />
              ) : (
                <Folder className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
              )
            ) : (
              <FileCode2 className="h-3.5 w-3.5 shrink-0 text-muted-foreground/70" />
            )}
            <span className="truncate">{entry.name}</span>
          </li>
        ))}
        <li className="flex items-center gap-2 rounded px-2 py-1 text-muted-foreground/50">
          <File className="h-3.5 w-3.5" />
          <span className="italic">…file index appears after scan</span>
        </li>
      </ul>
    </Panel>
  )
}
