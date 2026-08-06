import { Bug, DraftingCompass, FlaskConical, Scale, Server, Shield, Users } from "lucide-react"

import { AGENT_ROLES, type AgentRole } from "@/constants"
import { Badge } from "@/components/ui/badge"
import { Panel } from "@/components/ui/panel"
import { StatusIndicator } from "@/components/ui/status-indicator"

const ROLE_ICONS: Record<AgentRole, typeof Shield> = {
  governance: Shield,
  security_officer: Shield,
  software_architect: DraftingCompass,
  qa_lead: FlaskConical,
  devops_lead: Server,
  red_team: Bug,
  release_manager: Scale,
}

/**
 * Live agent roster — the centerpiece of the war room.
 * Phase 3: statuses come from the event stream (AgentStarted/Heartbeat/
 * Finished); idle dots become pulsing "working" states in real time.
 */
export function AgentStatus() {
  return (
    <Panel
      icon={Users}
      title="Live Agent Status"
      description="AI engineering review board"
      className="xl:col-span-5"
      action={<Badge variant="secondary">7 roles</Badge>}
    >
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {AGENT_ROLES.map((agent) => {
          const Icon = ROLE_ICONS[agent.role]
          return (
            <div
              key={agent.role}
              className="group flex items-center gap-3 rounded-md border border-border bg-muted/20 p-3 transition-colors hover:border-info/40 hover:bg-muted/40"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border bg-card text-muted-foreground transition-colors group-hover:text-info">
                <Icon className="h-4 w-4" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{agent.label}</p>
                <p className="truncate text-[11px] text-muted-foreground">
                  {agent.description}
                </p>
              </div>
              <StatusIndicator tone="muted" />
            </div>
          )
        })}
      </div>
    </Panel>
  )
}
