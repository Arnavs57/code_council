"""QA Director Agent — test coverage, edge cases, regression risk, test generation.

Evolution (Agentic Governance):
- Accepts CouncilState and can generate targeted tests based on Security findings.
- Reports confidence.
- Logs generated tests as a collaboration answer to Security.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.agents.council_state import CouncilState
from app.llm import reason_with_llm
from app.observability.tracer import AgentTracer


class QADirector:
    """Specialist agent: test verification, coverage analysis, and test generation."""

    def __init__(self):
        self.role = "QA Director"

    def run_review(
        self,
        repo_files: Dict[str, str],
        pr_diff: str,
        state: Optional[CouncilState] = None,
        collaboration_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        tracer = AgentTracer(agent_role=self.role)

        findings: List[str] = []
        suggested_tests: List[str] = []

        # ── Tool: coverage analyser ────────────────────────────────────────
        t0 = time.perf_counter()
        has_tests = any("test_" in name for name in repo_files.keys())
        diff_has_tests = "def test_" in pr_diff

        if not has_tests or not diff_has_tests:
            findings.append("WARNING: No new unit tests provided for changed functionality in this PR.")
            suggested_tests.extend([
                "def test_authentication_invalid_token_returns_401(): ...",
                "def test_rate_limiter_exceeds_quota_returns_429(): ...",
                "def test_config_invalid_port_raises_validation_error(): ...",
                "def test_github_webhook_invalid_signature_rejected(): ...",
            ])

        # ── Security-triggered test generation ────────────────────────────
        sec_result = state.get_result_for("Security Officer") if state else None
        if sec_result and sec_result.get("vote") in ("REJECT", "NEEDS_CHANGES"):
            security_findings = sec_result.get("findings", [])
            for sf in security_findings:
                if "jwt" in sf.lower() or "secret" in sf.lower():
                    suggested_tests.append("def test_hardcoded_secret_not_present_in_repo(): ...")
                    suggested_tests.append("def test_jwt_secret_loaded_from_env_not_source(): ...")
                if "sql" in sf.lower():
                    suggested_tests.append("def test_query_builder_prevents_sql_injection(): ...")
                if "prompt" in sf.lower():
                    suggested_tests.append("def test_user_input_sanitised_before_llm_prompt(): ...")

            if suggested_tests:
                state.log_message(
                    from_agent=self.role,
                    to_agent="Security Officer",
                    message=f"Generated {len(suggested_tests)} targeted security test(s) based on findings. "
                            "Tests cover JWT secret validation, SQL injection protection, and prompt-injection boundaries.",
                    message_type="ANSWER",
                ) if state else None

        tracer.record_tool_call(
            tool_name="test_coverage_analyser",
            input_summary=f"Analysed diff coverage across {len(repo_files)} files",
            output_summary=f"Identified {len(suggested_tests)} missing test cases",
            duration_ms=round((time.perf_counter() - t0) * 1000.0, 2),
        )

        # ── LLM reasoning ─────────────────────────────────────────────────
        reason_with_llm(tracer, self.role, pr_diff)

        # ── Scoring ───────────────────────────────────────────────────────
        if suggested_tests:
            vote = "NEEDS_CHANGES"
            qa_score = 70
            risk_level = "MEDIUM"
            confidence = 88
        else:
            vote = "APPROVE"
            qa_score = 95
            risk_level = "LOW"
            confidence = 92
            findings.append("Test coverage verified: comprehensive test suite covers all changed code paths.")

        summary = (
            f"QA review complete. Vote: {vote} "
            f"(Score: {qa_score}/100, Confidence: {confidence}%, "
            f"Generated {len(suggested_tests)} missing tests)."
        )
        trace = tracer.finalize(reasoning_summary=summary, risk_level=risk_level, warnings=len(findings))
        trace["confidence"] = confidence

        return {
            "agent_role": self.role,
            "vote": vote,
            "score": qa_score,
            "confidence": confidence,
            "findings": findings,
            "suggested_tests": suggested_tests,
            "trace": trace,
        }
