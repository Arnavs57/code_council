"""Memory Service — provides persistent organisational memory across review runs.

Queries the database for historical reviews on the same repository and returns:
- Unresolved findings from previous reviews
- Repeated vulnerability patterns
- Historical token/cost/duration statistics

This data is injected into CouncilState before agents run, enabling every agent
to reference and act on organisational history.
"""

from __future__ import annotations

from typing import Any, Dict, List

from app.database.database import SessionLocal
from app.models.models import AgentTrace, Repository, ReviewRun


class MemoryService:
    """Queries persistent storage to surface relevant historical context."""

    def get_historical_context(self, owner: str, repo: str, limit: int = 5) -> Dict[str, Any]:
        """Return historical findings and statistics for a given repository."""
        db = SessionLocal()
        try:
            db_repo = db.query(Repository).filter_by(owner=owner, name=repo).first()
            if not db_repo:
                return {"historical_findings": [], "historical_stats": {}}

            # Fetch last N completed review runs
            recent_runs = (
                db.query(ReviewRun)
                .filter_by()
                .filter(ReviewRun.id.in_(
                    [pr.id for pr in db_repo.pull_requests]
                    if db_repo.pull_requests else []
                ))
                .order_by(ReviewRun.started_at.desc())
                .limit(limit)
                .all()
            )

            # Collect historical findings from agent traces
            historical_findings: List[Dict[str, Any]] = []
            total_tokens_history: List[int] = []
            total_cost_history: List[float] = []
            total_duration_history: List[float] = []

            for idx, run in enumerate(recent_runs):
                total_tokens_history.append(run.total_tokens or 0)
                total_cost_history.append(run.total_cost or 0.0)
                total_duration_history.append(run.duration_seconds or 0.0)

                for trace in run.agent_traces:
                    summary = trace.reasoning_summary or ""
                    # Surface unresolved security / critical findings
                    if trace.risk_level in ("HIGH", "CRITICAL") and summary:
                        historical_findings.append({
                            "agent": trace.agent_role,
                            "risk_level": trace.risk_level,
                            "finding": summary[:200],
                            "reviews_ago": idx + 1,
                            "verdict": run.overall_verdict,
                        })

            avg_tokens   = int(sum(total_tokens_history) / len(total_tokens_history)) if total_tokens_history else 0
            avg_cost     = round(sum(total_cost_history) / len(total_cost_history), 6) if total_cost_history else 0.0
            avg_duration = round(sum(total_duration_history) / len(total_duration_history), 2) if total_duration_history else 0.0

            return {
                "historical_findings": historical_findings,
                "historical_stats": {
                    "reviews_analysed":  len(recent_runs),
                    "avg_tokens":        avg_tokens,
                    "avg_cost_usd":      avg_cost,
                    "avg_duration_sec":  avg_duration,
                    "unresolved_highs":  sum(1 for hf in historical_findings if hf["risk_level"] in ("HIGH", "CRITICAL")),
                },
            }
        finally:
            db.close()
