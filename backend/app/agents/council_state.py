"""Shared Council State — mutable context object threaded through an entire review run.

Every agent reads from and writes into the CouncilState. This is the mechanism
by which agents collaborate: Security can emit a CollaborationRequest that the
orchestrator detects and fulfils before the Release Manager synthesises its decision.

Design note: deliberately kept as a plain Python dataclass (not a Pydantic model)
so the orchestrator can mutate it freely mid-run without reconstruction overhead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class CollaborationRequest:
    """A request from one agent asking another agent to perform follow-up work."""
    requesting_agent: str          # e.g. "Security Officer"
    target_agent: str              # e.g. "Red Team"
    reason: str                    # human-readable justification
    context: Dict[str, Any] = field(default_factory=dict)  # findings / extra payload
    fulfilled: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AgentMessage:
    """A structured log entry of inter-agent communication during a review."""
    from_agent: str
    to_agent: str
    message: str
    message_type: str = "INFO"   # INFO | QUESTION | ANSWER | REQUEST | ESCALATION
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CouncilState:
    """Shared mutable context for a single review run.

    Passed by reference through the orchestrator so every agent can:
    - read the execution plan
    - read historical memory
    - read other agents' completed results
    - post collaboration requests
    - log inter-agent messages
    """
    # Identifiers
    owner: str = ""
    repo: str = ""
    pr_number: int = 0
    head_sha: str = ""

    # Input
    pr_diff: str = ""
    repo_files: Dict[str, str] = field(default_factory=dict)

    # Historical memory injected by MemoryService before agents run
    historical_findings: List[Dict[str, Any]] = field(default_factory=list)
    historical_stats: Dict[str, Any] = field(default_factory=dict)

    # Planning Agent output — consumed by orchestrator routing logic
    execution_plan: Optional[Dict[str, Any]] = None

    # Completed specialist results (appended as each agent finishes)
    completed_results: List[Dict[str, Any]] = field(default_factory=list)

    # Collaboration requests posted by specialist agents
    collaboration_requests: List[CollaborationRequest] = field(default_factory=list)

    # Inter-agent message log (displayed in PR as Collaboration Log)
    messages: List[AgentMessage] = field(default_factory=list)

    # ---- Mutation helpers ------------------------------------------------

    def add_result(self, result: Dict[str, Any]) -> None:
        """Record a completed specialist result into shared state."""
        self.completed_results.append(result)

    def request_collaboration(
        self,
        requesting_agent: str,
        target_agent: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> CollaborationRequest:
        """Emit a collaboration request from one agent to another."""
        req = CollaborationRequest(
            requesting_agent=requesting_agent,
            target_agent=target_agent,
            reason=reason,
            context=context or {},
        )
        self.collaboration_requests.append(req)
        self.log_message(
            from_agent=requesting_agent,
            to_agent=target_agent,
            message=f"Requesting follow-up: {reason}",
            message_type="REQUEST",
        )
        return req

    def log_message(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        message_type: str = "INFO",
    ) -> AgentMessage:
        """Append an inter-agent message to the collaboration log."""
        msg = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message=message,
            message_type=message_type,
        )
        self.messages.append(msg)
        return msg

    def get_result_for(self, agent_role: str) -> Optional[Dict[str, Any]]:
        """Retrieve the completed result for a specific agent role (if run)."""
        for r in self.completed_results:
            if r.get("agent_role") == agent_role:
                return r
        return None

    def get_pending_requests_for(self, target_agent: str) -> List[CollaborationRequest]:
        """Return unfulfilled collaboration requests targeting a given agent."""
        return [
            r for r in self.collaboration_requests
            if r.target_agent == target_agent and not r.fulfilled
        ]

    def mark_request_fulfilled(self, request: CollaborationRequest) -> None:
        request.fulfilled = True
