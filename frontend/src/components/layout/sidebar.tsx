import { NavLink } from "react-router-dom"
import {
  Activity,
  FileBarChart,
  FolderKanban,
  Gauge,
  GitPullRequestArrow,
  Settings,
} from "lucide-react"

import { NAV_ITEMS } from "@/constants"
import { useApp } from "@/contexts/app-context"
import { cn } from "@/lib/utils"

const ICONS = {
  "/": Gauge,
  "/projects": FolderKanban,
  "/review": GitPullRequestArrow,
  "/activity": Activity,
  "/reports": FileBarChart,
  "/settings": Settings,
} as const

/**
 * Left navigation rail. NavLink drives active styling so current section is
 * obvious at a glance — critical for an ops console. Collapses on small
 * screens (nav moves to the hamburger in a later phase).
 */
export function Sidebar() {
  const { version } = useApp()

  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-card/40 md:flex">
      <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-5">
        {["Mission Control", "System"].map((section) => (
          <div key={section}>
            <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
              {section}
            </p>
            <ul className="space-y-0.5">
              {NAV_ITEMS.filter((item) => item.section === section).map((item) => {
                const Icon = ICONS[item.path as keyof typeof ICONS] ?? Gauge
                return (
                  <li key={item.path}>
                    <NavLink
                      to={item.path}
                      end={item.path === "/"}
                      className={({ isActive }) =>
                        cn(
                          "group flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                          isActive
                            ? "bg-accent text-accent-foreground shadow-sm"
                            : "text-muted-foreground hover:bg-muted/60 hover:text-foreground",
                        )
                      }
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      {item.label}
                    </NavLink>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="border-t border-border px-5 py-3">
        <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
          v{version}
        </p>
      </div>
    </aside>
  )
}
