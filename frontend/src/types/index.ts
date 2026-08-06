/**
 * Domain model contracts — pure TypeScript interfaces.
 *
 * These mirror the backend schemas (Pydantic) 1:1. In Phase 2 they will be
 * GENERATED from the backend OpenAPI spec instead of hand-written to avoid
 * drift. Everything here is intentionally minimal: foundation only.
 */

import type { AgentRole } from "@/constants"

/* ------------------------------------------------------------------ */
/* Identity                                                            */
/* ------------------------------------------------------------------ */
export interface User {
  id: string
  name: string
  email: string
  avatarUrl?: string
  role: "viewer" | "approver" | "admin"
}

/* ------------------------------------------------------------------ */
/* Projects & repositories                                             */
/* ------------------------------------------------------------------ */
export interface Project {
  id: string
  name: string
  slug: string
  description?: string
  repositoryIds: string[]
  createdAt: string
}

export interface Repository {
  id: string
  name: string
  url?: string
  branch?: string
  sizeBytes?: number
  fileCount?: number
  languageStats?: Record<string, number>
  scannedAt?: string
}

/* ------------------------------------------------------------------ */
/* Agents & reviews                                                    */
/* ------------------------------------------------------------------ */
export type AgentStatus =
  | "idle"
  | "working"
  | "questioning"
  | "degraded"
  | "failed"
  | "done"

export interface Agent {
  id: string
  role: AgentRole
  status: AgentStatus
  model?: string
  startedAt?: string
  finishedAt?: string
  tokenBudget?: number
  tokensUsed?: number
}

export type Verdict = "go" | "no_go" | "go_with_conditions" | "pending"
export type ReviewStatus =
  | "pending"
  | "planning"
  | "scanning"
  | "reviewing"
  | "discussing"
  | "deciding"
  | "completed"
  | "failed"
  | "cancelled"

export interface Review {
  id: string
  repositoryId: string
  status: ReviewStatus
  startedAt: string
  completedAt?: string
  verdict?: Verdict
  planStages?: ExecutionStage[]
}

export interface ExecutionStage {
  id: string
  name: string
  status: "pending" | "active" | "done" | "failed"
  startedAt?: string
}

/* ------------------------------------------------------------------ */
/* Findings & evidence                                                 */
/* ------------------------------------------------------------------ */
export type Severity = "critical" | "high" | "medium" | "low" | "info"
export type FindingStatus = "open" | "contested" | "resolved" | "accepted"

export interface Finding {
  id: string
  reviewId: string
  agentRole: AgentRole
  title: string
  description?: string
  severity: Severity
  confidence?: number
  evidenceIds: string[]
  status: FindingStatus
  createdAt: string
}

export interface Evidence {
  id: string
  reviewId: string
  agentRole: AgentRole
  kind: "scan_output" | "tool_output" | "model_response" | "artifact"
  title: string
  artifactUrl?: string
  capturedAt: string
}

/* ------------------------------------------------------------------ */
/* Timeline & discussion                                               */
/* ------------------------------------------------------------------ */
export interface TimelineEvent {
  id: string
  reviewId: string
  type: string
  agentRole?: AgentRole
  message: string
  timestamp: string
  meta?: Record<string, unknown>
}

export interface DiscussionMessage {
  id: string
  threadId: string
  authorRole?: AgentRole
  authorName?: string
  body: string
  timestamp: string
}

/* ------------------------------------------------------------------ */
/* Notifications                                                       */
/* ------------------------------------------------------------------ */
export interface Notification {
  id: string
  kind: "decision" | "finding" | "agent" | "system"
  title: string
  body?: string
  read: boolean
  createdAt: string
}
