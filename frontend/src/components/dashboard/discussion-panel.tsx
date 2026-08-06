import { MessagesSquare } from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Panel } from "@/components/ui/panel"

const THREADS = [
  { role: "Security Officer", initials: "SO", text: "Contesting the severity of finding #12…" },
  { role: "Red Team", initials: "RT", text: "Requesting evidence for the auth claim…" },
  { role: "QA Lead", initials: "QA", text: "Asking DevOps about the test harness…" },
] as const

/**
 * Engineering discussion — agent Q&A visible to the operator.
 * Phase 3: QuestionAsked/AnswerPosted events append to threads; agree/
 * disagree actions become interactive.
 */
export function DiscussionPanel() {
  return (
    <Panel
      icon={MessagesSquare}
      title="Engineering Discussion"
      description="Agents consulting each other"
      className="xl:col-span-5"
      action={<Badge variant="outline">0 threads</Badge>}
    >
      <div className="space-y-3">
        {THREADS.map((thread) => (
          <div
            key={thread.role}
            className="flex gap-3 rounded-md border border-border/60 bg-muted/20 p-3"
          >
            <Avatar className="h-7 w-7">
              <AvatarFallback className="text-[9px]">{thread.initials}</AvatarFallback>
            </Avatar>
            <div className="min-w-0">
              <p className="text-xs font-medium text-muted-foreground">{thread.role}</p>
              <p className="mt-0.5 truncate text-sm text-muted-foreground/80">
                {thread.text}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
