import { Boxes, Cpu, Database, Radio } from "lucide-react"

import { MetricCard } from "@/components/ui/metric-card"
import { Panel } from "@/components/ui/panel"

/**
 * System health — infrastructure status rail.
 * Phase 3: becomes a real readiness probe (API / database / event bus /
 * worker queues) exposed by the backend /health endpoint.
 */
export function SystemHealth() {
  return (
    <Panel
      icon={Cpu}
      title="System Health"
      description="Platform infrastructure"
      className="xl:col-span-4"
    >
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <MetricCard
          icon={Cpu}
          label="API"
          value="online"
          status={{ label: "Healthy", variant: "success" }}
        />
        <MetricCard
          icon={Database}
          label="Database"
          value="—"
          status={{ label: "Pending", variant: "outline" }}
        />
        <MetricCard
          icon={Boxes}
          label="Event Bus"
          value="—"
          status={{ label: "Idle", variant: "outline" }}
        />
        <MetricCard
          icon={Radio}
          label="Workers"
          value="0"
          status={{ label: "0 active", variant: "outline" }}
        />
      </div>
    </Panel>
  )
}
