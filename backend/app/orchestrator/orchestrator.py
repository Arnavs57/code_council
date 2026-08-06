"""LangGraph AI Engineering Council Orchestrator — Agentic Governance Evolution.

The orchestrator is the central control loop that:
1. Loads historical memory from persistent storage
2. Runs the Planning Agent to create a dynamic execution plan
3. Executes specialist agents according to the plan (skipping unnecessary ones)
4. Detects collaboration requests emitted by agents and fulfils them (e.g. Security → Red Team)
5. Allows the Release Manager to trigger auto-escalation
6. Persists all traces, events, messages, and decisions to the database
7. Publishes the final governance report to GitHub PR as comment + Check Run

This is not a static pipeline. It is an autonomous governance loop.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.agents import (
    CouncilState,
    DevOpsLead,
    PlanningAgent,
    PrincipalArchitect,
    QADirector,
    RedTeam,
    ReleaseManager,
    SecurityOfficer,
)
from app.database.database import SessionLocal
from app.models.models import AgentTrace, PullRequest, Repository, ReviewRun, TimelineEvent, ToolCall
from app.observability.timeline import TimelineEngine
from app.services.formatter import format_check_run_output, format_pr_comment
from app.services.github import GitHubService
from app.services.memory import MemoryService

# ---------------------------------------------------------------------------
# Agent registry — maps role name to class
# ---------------------------------------------------------------------------

_AGENT_REGISTRY = {
    "Security Officer":   SecurityOfficer,
    "Principal Architect": PrincipalArchitect,
    "QA Director":        QADirector,
    "DevOps Lead":        DevOpsLead,
    "Red Team":           RedTeam,
}


class EngineeringCouncilOrchestrator:
    """Autonomous Engineering Council Orchestrator."""

    def __init__(self, github_service: Optional[GitHubService] = None):
        self.github_service = github_service or GitHubService()
        self.timeline = TimelineEngine()

    # ── Public entry point ─────────────────────────────────────────────────

    async def run_council_review(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        head_sha: str,
        base_sha: str = "main",
        pr_title: str = "AI Assisted Pull Request",
        author: str = "ai-developer",
        pr_diff: str = "",
        repo_files: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Execute complete autonomous engineering governance workflow."""
        start_perf = time.perf_counter()
        files    = repo_files or {"app/main.py": "# Main FastAPI entry", "Dockerfile": "FROM python:3.11"}
        diff_text = pr_diff or "+ CCAI_ENVIRONMENT=development\n+ CCAI_JWT_SECRET=super_secret_key"

        # ── 1. Initialise shared state ────────────────────────────────────
        state = CouncilState(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            head_sha=head_sha,
            pr_diff=diff_text,
            repo_files=files,
        )

        self.timeline.add_event("GitHub Action Triggered", f"PR #{pr_number} by @{author}", "TRIGGER")
        self.timeline.add_event("Repository Indexed", f"Analysed {len(files)} files and commit {head_sha[:7]}", "INDEX")

        # ── 2. Inject historical memory ───────────────────────────────────
        self.timeline.add_event("Memory Service", "Loading organisational review history", "INDEX")
        memory_svc = MemoryService()
        try:
            memory = memory_svc.get_historical_context(owner=owner, repo=repo)
            state.historical_findings = memory.get("historical_findings", [])
            state.historical_stats    = memory.get("historical_stats", {})
        except Exception:
            state.historical_findings = []
            state.historical_stats    = {}

        if state.historical_findings:
            self.timeline.add_event(
                "Memory Loaded",
                f"Surfaced {len(state.historical_findings)} historical finding(s) from {state.historical_stats.get('reviews_analysed', 0)} prior review(s)",
                "INDEX",
            )

        # ── 3. Planning Agent — dynamic execution plan ────────────────────
        self.timeline.add_event("Planning Agent", "Analysing changeset and computing execution plan", "AGENT_START")
        planner = PlanningAgent()
        plan    = planner.create_plan(
            pr_diff=diff_text,
            repo_files=files,
            historical_stats=state.historical_stats,
        )
        state.execution_plan = plan.to_dict()

        self.timeline.add_event(
            "Execution Plan Ready",
            f"Run: [{', '.join(plan.agents_to_run)}] | Skip: [{', '.join(plan.agents_skipped.keys())}]",
            "DECISION",
        )

        # ── 4. Specialist agent execution loop ────────────────────────────
        specialist_results: List[Dict[str, Any]] = []
        plan_trace: Optional[Dict[str, Any]] = getattr(plan, "_tracer_dict", None)

        ordered_agents = [
            "Security Officer",
            "Principal Architect",
            "QA Director",
            "DevOps Lead",
            "Red Team",
        ]

        executed_roles: set = set()

        for agent_role in ordered_agents:
            if not plan.should_run(agent_role):
                self.timeline.add_event(
                    f"{agent_role} Skipped",
                    plan.skip_reason(agent_role) or "Skipped per execution plan",
                    "INFO",
                )
                continue

            result = self._run_agent(agent_role, files, diff_text, state)
            specialist_results.append(result)
            state.add_result(result)
            executed_roles.add(agent_role)

        # ── 5. Fulfilment pass — collaboration requests ───────────────────
        fulfilled_results = self._fulfill_collaboration_requests(
            state=state,
            files=files,
            diff_text=diff_text,
            executed_roles=executed_roles,
        )
        specialist_results.extend(fulfilled_results)
        for r in fulfilled_results:
            state.add_result(r)
            executed_roles.add(r["agent_role"])

        # ── 6. Release Manager — autonomous convergence ───────────────────
        self.timeline.add_event("Release Manager", "Synthesising evidence, resolving disputes, issuing verdict", "DECISION")
        rm_agent = ReleaseManager()
        decision = rm_agent.synthesize_decision(specialist_results, state=state)

        # ── 7. Handle Release Manager auto-escalation ─────────────────────
        if decision.get("auto_escalation_triggered") and "Red Team" not in executed_roles:
            self.timeline.add_event("Auto-Escalation", "Release Manager launching Red Team (not in plan)", "DECISION")
            red_result = self._run_agent(
                "Red Team", files, diff_text, state,
                collaboration_context=decision.get("trace", {}),
            )
            specialist_results.append(red_result)
            state.add_result(red_result)
            # Re-run RM with Red Team included
            decision = rm_agent.synthesize_decision(specialist_results, state=state)
            self.timeline.add_event(
                "Verdict Revised",
                f"Re-synthesised after Red Team escalation: {decision['overall_verdict']}",
                "DECISION",
            )

        # ── 8. Collect traces & totals ────────────────────────────────────
        traces = [r["trace"] for r in specialist_results] + [decision["trace"]]
        if plan_trace:
            traces = [plan_trace] + traces

        total_tokens      = sum(t["total_tokens"]    for t in traces)
        total_cost        = round(sum(t["estimated_cost"] for t in traces), 6)
        total_llm_calls   = sum(t["llm_call_count"]  for t in traces)
        total_duration_sec = round(time.perf_counter() - start_perf, 2)

        events = self.timeline.get_events()

        # ── 9. GitHub publication ─────────────────────────────────────────
        comment_markdown = format_pr_comment(
            repo_name=f"{owner}/{repo}",
            pr_number=pr_number,
            specialist_results=specialist_results,
            decision=decision,
            execution_plan=plan.to_dict(),
            timeline_events=events,
            traces=traces,
            total_tokens=total_tokens,
            total_cost=total_cost,
            total_duration_sec=total_duration_sec,
            collaboration_messages=state.messages,
            historical_stats=state.historical_stats,
        )

        check_output = format_check_run_output(decision, specialist_results, total_tokens, total_cost)

        pr_comment_res = await self.github_service.create_pr_comment(owner, repo, pr_number, comment_markdown)
        check_run_res  = await self.github_service.create_check_run(
            owner, repo, head_sha,
            status="completed",
            conclusion=check_output["conclusion"],
            output={
                "title":   check_output["title"],
                "summary": check_output["summary"],
                "text":    comment_markdown,
            },
        )

        # ── 10. Database persistence ──────────────────────────────────────
        self._persist_review_to_db(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            pr_title=pr_title,
            head_sha=head_sha,
            base_sha=base_sha,
            author=author,
            decision=decision,
            traces=traces,
            events=events,
            total_tokens=total_tokens,
            total_cost=total_cost,
            total_llm_calls=total_llm_calls,
            duration_seconds=total_duration_sec,
            execution_plan=state.execution_plan or {},
        )

        return {
            "overall_verdict":      decision["overall_verdict"],
            "production_readiness": decision["production_readiness"],
            "total_tokens":         total_tokens,
            "total_cost":           total_cost,
            "duration_seconds":     total_duration_sec,
            "agents_run":           list(executed_roles),
            "agents_skipped":       plan.agents_skipped,
            "collaboration_messages": len(state.messages),
            "auto_escalation":      decision.get("auto_escalation_triggered", False),
            "pr_comment_result":    pr_comment_res,
            "check_run_result":     check_run_res,
            "comment_markdown":     comment_markdown,
        }

    # ── Internal helpers ───────────────────────────────────────────────────

    def _run_agent(
        self,
        agent_role: str,
        files: Dict[str, str],
        diff_text: str,
        state: CouncilState,
        collaboration_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Instantiate and run a single specialist agent, recording timeline events."""
        self.timeline.add_event(f"{agent_role} Started", f"Executing review pass", "AGENT_START")

        agent_cls = _AGENT_REGISTRY[agent_role]
        agent     = agent_cls()
        result    = agent.run_review(
            repo_files=files,
            pr_diff=diff_text,
            state=state,
            collaboration_context=collaboration_context,
        )

        self.timeline.add_event(
            f"{agent_role} Completed",
            f"Vote: {result['vote']} | Confidence: {result.get('confidence', '?')}%",
            "AGENT_END",
        )
        return result

    def _fulfill_collaboration_requests(
        self,
        state: CouncilState,
        files: Dict[str, str],
        diff_text: str,
        executed_roles: set,
    ) -> List[Dict[str, Any]]:
        """Process all pending collaboration requests.

        If Security asked Red Team to run (but Red Team was skipped by the plan),
        this method runs it now with the security context attached.
        """
        additional_results: List[Dict[str, Any]] = []

        for req in state.collaboration_requests:
            if req.fulfilled:
                continue
            if req.target_agent in executed_roles:
                req.fulfilled = True
                continue

            self.timeline.add_event(
                f"Collaboration: {req.requesting_agent} → {req.target_agent}",
                f"Reason: {req.reason[:100]}",
                "DECISION",
            )

            result = self._run_agent(
                agent_role=req.target_agent,
                files=files,
                diff_text=diff_text,
                state=state,
                collaboration_context=req.context,
            )
            additional_results.append(result)
            state.mark_request_fulfilled(req)

        return additional_results

    # ── Persistence ────────────────────────────────────────────────────────

    def _persist_review_to_db(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        pr_title: str,
        head_sha: str,
        base_sha: str,
        author: str,
        decision: Dict[str, Any],
        traces: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        total_tokens: int,
        total_cost: float,
        total_llm_calls: int,
        duration_seconds: float,
        execution_plan: Dict[str, Any],
    ) -> None:
        """Persist all review artefacts into SQLite / PostgreSQL."""
        import json

        db = SessionLocal()
        try:
            # Repo
            db_repo = db.query(Repository).filter_by(owner=owner, name=repo).first()
            if not db_repo:
                db_repo = Repository(owner=owner, name=repo)
                db.add(db_repo)
                db.flush()

            # PR
            db_pr = db.query(PullRequest).filter_by(repo_id=db_repo.id, pr_number=pr_number).first()
            if not db_pr:
                db_pr = PullRequest(
                    repo_id=db_repo.id,
                    pr_number=pr_number,
                    title=pr_title,
                    head_sha=head_sha,
                    base_sha=base_sha,
                    author=author,
                )
                db.add(db_pr)
                db.flush()

            # Review Run
            db_review = ReviewRun(
                pr_id=db_pr.id,
                status="COMPLETED",
                overall_verdict=decision["overall_verdict"],
                security_score=decision["security_score"],
                architecture_score=decision["architecture_score"],
                qa_score=decision["qa_score"],
                devops_score=decision["devops_score"],
                overall_risk=decision["overall_risk"],
                production_readiness=decision["production_readiness"],
                total_tokens=total_tokens,
                total_cost=total_cost,
                total_llm_calls=total_llm_calls,
                duration_seconds=duration_seconds,
                execution_plan=json.dumps(execution_plan),
            )
            db.add(db_review)
            db.flush()

            # Agent Traces & Tool Calls
            for tr in traces:
                db_trace = AgentTrace(
                    review_id=db_review.id,
                    agent_role=tr["agent_role"],
                    status=tr["status"],
                    duration_ms=tr["duration_ms"],
                    llm_provider=tr["llm_provider"],
                    model=tr["model"],
                    input_tokens=tr["input_tokens"],
                    output_tokens=tr["output_tokens"],
                    total_tokens=tr["total_tokens"],
                    estimated_cost=tr["estimated_cost"],
                    llm_call_count=tr["llm_call_count"],
                    tool_call_count=tr["tool_call_count"],
                    files_read=tr.get("files_read", 0),
                    files_modified=tr.get("files_modified", 0),
                    errors=tr.get("errors", 0),
                    warnings=tr.get("warnings", 0),
                    risk_level=tr.get("risk_level", "LOW"),
                    reasoning_summary=tr.get("reasoning_summary", ""),
                    confidence=tr.get("confidence", 80),
                )
                db.add(db_trace)
                db.flush()

                for tc in tr.get("tool_calls", []):
                    db_tool = ToolCall(
                        trace_id=db_trace.id,
                        tool_name=tc["tool_name"],
                        input_summary=tc["input_summary"],
                        output_summary=tc["output_summary"],
                        duration_ms=tc.get("duration_ms", 0.0),
                    )
                    db.add(db_tool)

            # Timeline Events
            for ev in events:
                db_event = TimelineEvent(
                    review_id=db_review.id,
                    title=ev["title"],
                    description=ev.get("description", ""),
                    event_type=ev.get("event_type", "INFO"),
                )
                db.add(db_event)

            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
