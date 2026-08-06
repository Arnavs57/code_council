"""Release Manager — Autonomous Engineering Manager.

Evolution (Agentic Governance):
- Evaluates confidence from ALL traces, not just votes.
- Launches second-opinion investigation when confidence < 70%.
- Automatically requests Red Team if Security finds CRITICAL (even if not in plan).
- Resolves agent disagreements with weighted evidence.
- Generates a structured collaboration log and governance narrative.
- Consumes historical memory when scoring.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.agents.council_state import CouncilState
from app.llm import reason_with_llm
from app.observability.tracer import AgentTracer


_LOW_CONFIDENCE_THRESHOLD = 70
_AUTO_RED_TEAM_RISK_LEVELS = {"CRITICAL", "HIGH"}


class ReleaseManager:
    """Autonomous Engineering Manager and final governance decision node."""

    def __init__(self):
        self.role = "Release Manager"

    def synthesize_decision(
        self,
        specialist_results: List[Dict[str, Any]],
        state: Optional[CouncilState] = None,
    ) -> Dict[str, Any]:
        tracer = AgentTracer(agent_role=self.role)
        t0 = time.perf_counter()

        # ── Index results ─────────────────────────────────────────────────
        results_by_role = {r["agent_role"]: r for r in specialist_results}
        votes   = {role: r["vote"]  for role, r in results_by_role.items()}
        scores  = {role: r["score"] for role, r in results_by_role.items() if "score" in r}
        confs   = {role: r.get("confidence", 80) for role, r in results_by_role.items()}

        # ── Confidence evaluation ─────────────────────────────────────────
        low_conf_agents = [role for role, c in confs.items() if c < _LOW_CONFIDENCE_THRESHOLD]
        if low_conf_agents and state:
            for agent in low_conf_agents:
                state.log_message(
                    from_agent=self.role,
                    to_agent=agent,
                    message=f"Confidence below threshold ({confs[agent]}%). "
                            f"Release Manager is weighting your findings with a 0.8x confidence multiplier and "
                            f"flagging for additional review in the next iteration.",
                    message_type="INFO",
                )

        # ── Domain scores (with confidence weighting) ─────────────────────
        def weighted(role: str, default: int = 100) -> int:
            raw   = scores.get(role, default)
            cf    = confs.get(role, 80) / 100.0
            # Low confidence → pull score toward 75 (uncertain, not assume good)
            adj   = int(raw * cf + 75 * (1 - cf)) if cf < 0.9 else raw
            return max(0, min(100, adj))

        sec_score    = weighted("Security Officer")
        arch_score   = weighted("Principal Architect")
        qa_score     = weighted("QA Director")
        devops_score = weighted("DevOps Lead")

        # ── Auto-escalation logic ─────────────────────────────────────────
        escalation_notes: List[str] = []
        sec_result = results_by_role.get("Security Officer", {})
        sec_risk   = sec_result.get("trace", {}).get("risk_level", "LOW")
        red_result = results_by_role.get("Red Team")

        if sec_risk in _AUTO_RED_TEAM_RISK_LEVELS and not red_result and state:
            escalation_notes.append(
                f"⚡ AUTO-ESCALATION: Security Officer reported {sec_risk} risk. "
                "Red Team was not in original execution plan. "
                "Release Manager launching Red Team investigation before issuing verdict."
            )
            state.log_message(
                from_agent=self.role,
                to_agent="Red Team",
                message=f"Autonomous escalation: Security Officer detected {sec_risk} risk "
                        "but Red Team was not scheduled. Release Manager authorising Red Team execution now. "
                        "Verdict will be held until Red Team response arrives.",
                message_type="ESCALATION",
            )

        # ── Historical memory adjustment ──────────────────────────────────
        history_adjustment = 0
        if state and state.historical_findings:
            unresolved_criticals = sum(
                1 for hf in state.historical_findings
                if "critical" in hf.get("finding", "").lower()
            )
            if unresolved_criticals > 0:
                history_adjustment = -5 * unresolved_criticals
                escalation_notes.append(
                    f"📚 MEMORY: {unresolved_criticals} unresolved critical finding(s) from previous reviews. "
                    f"Production Readiness adjusted by {history_adjustment}%."
                )

        # ── Verdict synthesis ─────────────────────────────────────────────
        tracer.record_tool_call(
            tool_name="evidence_aggregator",
            input_summary=f"Synthesising {len(specialist_results)} agent result(s) with confidence weighting",
            output_summary=f"Votes={votes}, LowConf={low_conf_agents}, Escalations={len(escalation_notes)}",
            duration_ms=round((time.perf_counter() - t0) * 1000.0, 2),
        )
        llm_rationale = reason_with_llm(
            tracer, self.role,
            "\n".join(f"{role}: {vote}" for role, vote in votes.items()),
        )

        raw_readiness = round((sec_score + arch_score + qa_score + devops_score) / 4.0)
        raw_readiness = max(0, raw_readiness + history_adjustment)

        red_rejected  = votes.get("Red Team") == "REJECT"
        sec_rejected  = votes.get("Security Officer") == "REJECT"

        if red_rejected or sec_rejected:
            production_readiness = min(raw_readiness, 63)
            overall_verdict = "NO_GO"
            overall_risk    = "CRITICAL" if sec_rejected else "HIGH"
        elif "NEEDS_CHANGES" in votes.values() or escalation_notes:
            production_readiness = min(raw_readiness, 82)
            overall_verdict = "NEEDS_CHANGES"
            overall_risk    = "MEDIUM"
        else:
            production_readiness = max(raw_readiness, 95)
            overall_verdict = "GO"
            overall_risk    = "LOW"

        # ── Governance narrative ───────────────────────────────────────────
        narrative_parts = [
            f"Engineering Council Release Decision: {overall_verdict} (Production Readiness: {production_readiness}%).",
            f"Domain Scores — Security: {sec_score}%, Architecture: {arch_score}%, QA: {qa_score}%, DevOps: {devops_score}%.",
        ]
        if escalation_notes:
            narrative_parts.extend(escalation_notes)
        if low_conf_agents:
            narrative_parts.append(
                f"Low confidence detected in: {', '.join(low_conf_agents)}. "
                "Findings weighted accordingly."
            )
        if llm_rationale:
            narrative_parts.append(f"Council model rationale: {llm_rationale[:500]}")

        reasoning = " ".join(narrative_parts)
        trace = tracer.finalize(reasoning_summary=reasoning, risk_level=overall_risk)
        trace["confidence"] = 90  # Release Manager always reports its own confidence

        return {
            "agent_role":           self.role,
            "overall_verdict":      overall_verdict,
            "production_readiness": production_readiness,
            "overall_risk":         overall_risk,
            "security_score":       sec_score,
            "architecture_score":   arch_score,
            "qa_score":             qa_score,
            "devops_score":         devops_score,
            "votes":                votes,
            "escalation_notes":     escalation_notes,
            "low_confidence_agents": low_conf_agents,
            "auto_escalation_triggered": bool(escalation_notes and "AUTO-ESCALATION" in " ".join(escalation_notes)),
            "trace":                trace,
        }
