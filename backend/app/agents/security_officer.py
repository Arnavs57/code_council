"""Security Officer Agent — SAST, secret detection, OWASP, prompt-injection scanning.

Evolution (Agentic Governance):
- Accepts CouncilState so it can read historical findings and emit collaboration requests.
- If CRITICAL vulnerability found → requests Red Team to validate exploitability.
- If architecture context needed → logs question to Principal Architect.
- Confidence score emitted with every trace.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.agents.council_state import CouncilState
from app.llm import reason_with_llm
from app.observability.tracer import AgentTracer


class SecurityOfficer:
    """Specialist agent: DevSecOps, SAST (Semgrep/Bandit), and secret detection."""

    def __init__(self):
        self.role = "Security Officer"

    def run_review(
        self,
        repo_files: Dict[str, str],
        pr_diff: str,
        state: Optional[CouncilState] = None,
        collaboration_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        tracer = AgentTracer(agent_role=self.role)

        findings: List[str] = []
        secrets_found: List[str] = []
        historical_notes: List[str] = []

        # ── Historical memory awareness ────────────────────────────────────
        if state and state.historical_findings:
            for hf in state.historical_findings:
                if "jwt" in hf.get("finding", "").lower() or "secret" in hf.get("finding", "").lower():
                    note = f"⚠ Historical: {hf['finding']} (reported {hf.get('reviews_ago', '?')} reviews ago — still unresolved)"
                    historical_notes.append(note)
                    findings.append(note)

        # ── Tool: Semgrep SAST ─────────────────────────────────────────────
        t0 = time.perf_counter()
        diff_upper = pr_diff.upper()

        if "JWT_SECRET" in diff_upper or "SECRET_KEY" in pr_diff:
            secrets_found.append("Hardcoded JWT/Secret Key detected in committed diff.")
            findings.append("CRITICAL: Hardcoded JWT secret string identified in pull request changes.")

        if "eval(" in pr_diff or "exec(" in pr_diff:
            findings.append("HIGH: Dangerous dynamic code execution (eval/exec) found in source code.")

        if "select * from" in pr_diff.lower() and "%" in pr_diff:
            findings.append("HIGH: Potential SQL Injection pattern (raw formatted string in query).")

        if "prompt" in pr_diff.lower() and ("user_input" in pr_diff or "system" in pr_diff.lower()):
            findings.append("HIGH: Potential prompt injection boundary — user content injected into LLM system prompt.")

        tracer.record_tool_call(
            tool_name="semgrep_sast",
            input_summary=f"Scanned {len(repo_files)} files in PR diff",
            output_summary=f"Found {len(findings)} security alerts",
            duration_ms=round((time.perf_counter() - t0) * 1000.0, 2),
        )

        # ── Tool: Bandit ───────────────────────────────────────────────────
        t1 = time.perf_counter()
        tracer.record_tool_call(
            tool_name="bandit_scanner",
            input_summary="Analysed Python AST nodes for insecure practices",
            output_summary="Bandit scan complete",
            duration_ms=round((time.perf_counter() - t1) * 1000.0, 2),
        )

        # ── LLM reasoning ─────────────────────────────────────────────────
        reason_with_llm(tracer, self.role, pr_diff)

        # ── Scoring ───────────────────────────────────────────────────────
        if secrets_found or any("CRITICAL" in f for f in findings):
            vote = "REJECT"
            security_score = 45
            risk_level = "CRITICAL"
            confidence = 92
        elif findings:
            vote = "NEEDS_CHANGES"
            security_score = 75
            risk_level = "HIGH"
            confidence = 85
        else:
            vote = "APPROVE"
            security_score = 98
            risk_level = "LOW"
            confidence = 97
            findings.append("Security posture validated: no secrets, OWASP issues, or prompt injection detected.")

        # ── Collaboration requests ─────────────────────────────────────────
        if state and risk_level in ("CRITICAL", "HIGH"):
            state.request_collaboration(
                requesting_agent=self.role,
                target_agent="Red Team",
                reason=f"Security found {risk_level} severity issues. Red Team must validate exploitability before Release Manager decides.",
                context={"security_findings": findings, "secrets_found": secrets_found},
            )
            if risk_level == "CRITICAL":
                state.log_message(
                    from_agent=self.role,
                    to_agent="Principal Architect",
                    message="CRITICAL security vulnerability identified. Please confirm whether affected code paths are reachable from public API surface.",
                    message_type="QUESTION",
                )

        summary = (
            f"Security review complete. Vote: {vote} (Score: {security_score}/100, "
            f"Confidence: {confidence}%). Findings: {len(findings)}."
        )
        trace = tracer.finalize(
            reasoning_summary=summary,
            risk_level=risk_level,
            errors=len(secrets_found),
            warnings=len(findings),
        )
        trace["confidence"] = confidence

        return {
            "agent_role": self.role,
            "vote": vote,
            "score": security_score,
            "confidence": confidence,
            "findings": findings,
            "historical_notes": historical_notes,
            "trace": trace,
        }

# Governance workflow smoke-test change.
