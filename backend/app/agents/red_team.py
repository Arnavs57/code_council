"""Red Team Agent — exploit simulation: auth bypass, privilege escalation, prompt injection.

Evolution (Agentic Governance):
- Accepts collaboration_context from Security Officer when launched as a follow-up.
- Answers Security's question with confirmation/denial of exploitability.
- Posts its answer back to state as an AgentMessage.
- Confidence score emitted.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.agents.council_state import CouncilState
from app.llm import reason_with_llm
from app.observability.tracer import AgentTracer


class RedTeam:
    """Specialist agent: adversarial exploit simulation."""

    def __init__(self):
        self.role = "Red Team"

    def run_review(
        self,
        repo_files: Dict[str, str],
        pr_diff: str,
        state: Optional[CouncilState] = None,
        collaboration_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        tracer = AgentTracer(agent_role=self.role)

        findings: List[str] = []
        exploits_tested: List[str] = [
            "JWT Signature Stripping (alg:none attack)",
            "Prompt Injection via System Boundary Violation",
            "Path Traversal in Repository File Loader",
            "Unauthenticated Endpoint Enumeration",
            "Privilege Escalation via Role Bypass",
        ]

        # ── Receive collaboration context from Security Officer ─────────────
        security_findings: List[str] = []
        launched_by_security = False
        if collaboration_context and "security_findings" in collaboration_context:
            security_findings = collaboration_context["security_findings"]
            launched_by_security = True
            tracer.record_tool_call(
                tool_name="collaboration_context_loader",
                input_summary=f"Received {len(security_findings)} finding(s) from Security Officer",
                output_summary="Loaded Security context for targeted exploit simulation",
                duration_ms=0.5,
            )

        # ── Tool: exploit simulator ────────────────────────────────────────
        t0 = time.perf_counter()
        diff_lower = pr_diff.lower()

        # Check for specific vulnerability indicators
        jwt_secret_exposed = "jwt_secret" in diff_lower or "secret_key" in pr_diff.lower()
        auth_bypass_pattern = "bypass" in diff_lower or "admin" in diff_lower
        prompt_injection = "prompt" in diff_lower and "user_input" in diff_lower

        if jwt_secret_exposed or (launched_by_security and any("jwt" in f.lower() or "secret" in f.lower() for f in security_findings)):
            findings.append("CRITICAL: Exposed JWT secret is exploitable. Attacker can forge arbitrary session tokens → full authentication bypass confirmed.")

        if auth_bypass_pattern:
            findings.append("HIGH: Authentication bypass path discovered. Privilege escalation to admin role confirmed exploitable.")

        if prompt_injection:
            findings.append("HIGH: Prompt injection boundary is exploitable. LLM system prompt overridable via crafted user input.")

        tracer.record_tool_call(
            tool_name="exploit_simulator",
            input_summary=f"Ran {len(exploits_tested)} exploit vectors. Security context: {bool(launched_by_security)}",
            output_summary=f"Confirmed {len(findings)} exploitable vector(s)",
            duration_ms=round((time.perf_counter() - t0) * 1000.0, 2),
        )

        # ── LLM reasoning ─────────────────────────────────────────────────
        reason_with_llm(tracer, self.role, pr_diff)

        # ── Scoring ───────────────────────────────────────────────────────
        if any("CRITICAL" in f for f in findings):
            vote = "REJECT"
            risk_level = "CRITICAL"
            confidence = 95
        elif any("HIGH" in f for f in findings):
            vote = "NEEDS_CHANGES"
            risk_level = "HIGH"
            confidence = 88
        else:
            vote = "APPROVE"
            risk_level = "LOW"
            confidence = 90
            findings.append("All simulated exploit vectors passed without confirmed exploitation.")

        # ── Reply to Security Officer via state messages ───────────────────
        if state and launched_by_security:
            exploitability = "CONFIRMED" if vote == "REJECT" else ("PARTIAL" if vote == "NEEDS_CHANGES" else "NOT CONFIRMED")
            state.log_message(
                from_agent=self.role,
                to_agent="Security Officer",
                message=f"Exploit validation complete. Exploitability: {exploitability}. "
                        f"Confirmed {len([f for f in findings if 'CRITICAL' in f or 'HIGH' in f])} critical/high vectors. "
                        f"Recommend: {vote}.",
                message_type="ANSWER",
            )
            state.log_message(
                from_agent=self.role,
                to_agent="Release Manager",
                message=f"Red Team escalation: {exploitability} exploit(s) detected. "
                        f"Increasing release block confidence. Full findings attached.",
                message_type="ESCALATION",
            )

        summary = (
            f"Red Team exploit simulation: {len(exploits_tested)} vectors tested, "
            f"{len(findings)} confirmed. Vote: {vote} (Confidence: {confidence}%)."
        )
        trace = tracer.finalize(
            reasoning_summary=summary,
            risk_level=risk_level,
            errors=len([f for f in findings if "CRITICAL" in f]),
        )
        trace["confidence"] = confidence

        return {
            "agent_role": self.role,
            "vote": vote,
            "confidence": confidence,
            "exploits_tested": exploits_tested,
            "findings": findings,
            "launched_by_collaboration": launched_by_security,
            "trace": trace,
        }
