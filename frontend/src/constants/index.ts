/**
 * Application-wide constants — single source of truth for labels, routes
 * and enums. Mirrors backend `app/core/constants.py`.
 */

export const APP_NAME = "Code Council AI"
export const APP_VERSION = "0.1.0"
export const APP_TAGLINE = "AI Engineering Governance Platform"
export const DEFAULT_ENVIRONMENT = "development"

/** Client-side routes. */
export const ROUTES = {
  dashboard: "/",
  projects: "/projects",
  review: "/review/:reviewId?",
  reviewBase: "/review",
  activity: "/activity",
  reports: "/reports",
  settings: "/settings",
} as const

export interface NavItem {
  label: string
  path: string
  section: string
}

/** Primary navigation (mission-control sections). */
export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", path: ROUTES.dashboard, section: "Mission Control" },
  { label: "Projects", path: ROUTES.projects, section: "Mission Control" },
  { label: "Repository Review", path: ROUTES.reviewBase, section: "Mission Control" },
  { label: "Activity", path: ROUTES.activity, section: "Mission Control" },
  { label: "Reports", path: ROUTES.reports, section: "Mission Control" },
  { label: "Settings", path: ROUTES.settings, section: "System" },
]

/** AI engineering roles that will appear in the live review board. */
export const AGENT_ROLES = [
  { role: "governance", label: "Governance Controller", description: "Planning, policy and budget" },
  { role: "security_officer", label: "Security Officer", description: "Threats, secrets, dependencies" },
  { role: "software_architect", label: "Software Architect", description: "Structure and design quality" },
  { role: "qa_lead", label: "QA Lead", description: "Test coverage and quality gates" },
  { role: "devops_lead", label: "DevOps Lead", description: "Deployability and operations" },
  { role: "red_team", label: "Red Team", description: "Adversarial validation" },
  { role: "release_manager", label: "Release Manager", description: "Final engineering decision" },
] as const

export type AgentRole = (typeof AGENT_ROLES)[number]["role"]

/** Status meta shared by the roster, timeline and indicators. */
export const AGENT_STATUS_META = {
  idle: { label: "Idle", tone: "muted" },
  working: { label: "Working", tone: "info" },
  questioning: { label: "Questioning", tone: "warning" },
  degraded: { label: "Degraded", tone: "warning" },
  failed: { label: "Failed", tone: "destructive" },
  done: { label: "Complete", tone: "success" },
} as const

export const SEVERITY_META = {
  critical: { label: "Critical", tone: "destructive" },
  high: { label: "High", tone: "warning" },
  medium: { label: "Medium", tone: "info" },
  low: { label: "Low", tone: "muted" },
  info: { label: "Info", tone: "muted" },
} as const

/** Severity → Badge variant — single source for findings rendering. */
export const SEVERITY_BADGE_VARIANT: Record<
  keyof typeof SEVERITY_META,
  "destructive" | "warning" | "info" | "muted"
> = {
  critical: "destructive",
  high: "warning",
  medium: "info",
  low: "muted",
  info: "muted",
}
