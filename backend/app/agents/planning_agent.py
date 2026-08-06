"""Planning Agent — analyses a Pull Request and produces a dynamic execution plan.

The Planning Agent is the first agent to run on every review. It examines:
- Which files were changed
- What categories they belong to (auth, infra, tests, docs, config, business logic)
- The overall diff complexity and estimated risk
- Estimated review cost given selected specialists

It then outputs an ExecutionPlan: a structured decision about which specialist
agents should run, in what order, and why — and which can be safely skipped.

This is the mechanism that transforms the council from a static pipeline into a
dynamic, risk-proportionate governance system.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Set

from app.observability.tracer import AgentTracer
from app.llm import reason_with_llm

# ---------------------------------------------------------------------------
# File-category classification rules
# ---------------------------------------------------------------------------

_AUTH_PATTERNS = {"auth", "jwt", "token", "oauth", "session", "login", "password", "secret", "permission", "rbac"}
_INFRA_PATTERNS = {"dockerfile", "docker-compose", ".yml", ".yaml", "terraform", "k8s", "helm", "nginx", ".env", "compose"}
_TEST_PATTERNS  = {"test_", "_test.py", "spec.", ".test.", ".spec."}
_DOC_PATTERNS   = {".md", ".rst", ".txt", "readme", "changelog", "license"}
_CONFIG_PATTERNS = {"settings", "config", "constants", "environment", ".toml", ".ini", ".cfg"}
_SECURITY_PATTERNS = {"crypto", "hash", "encrypt", "decrypt", "signature", "verify", "tls", "ssl", "cert"}


def _classify_files(files: Dict[str, str]) -> Dict[str, List[str]]:
    """Return a dict mapping category → list of file paths in that category."""
    categories: Dict[str, List[str]] = {
        "auth": [], "infra": [], "tests": [],
        "docs": [], "config": [], "security": [], "business_logic": [],
    }
    for path in files.keys():
        path_lower = path.lower()
        if any(p in path_lower for p in _AUTH_PATTERNS):
            categories["auth"].append(path)
        elif any(p in path_lower for p in _INFRA_PATTERNS):
            categories["infra"].append(path)
        elif any(p in path_lower for p in _TEST_PATTERNS):
            categories["tests"].append(path)
        elif any(p in path_lower for p in _DOC_PATTERNS):
            categories["docs"].append(path)
        elif any(p in path_lower for p in _CONFIG_PATTERNS):
            categories["config"].append(path)
        elif any(p in path_lower for p in _SECURITY_PATTERNS):
            categories["security"].append(path)
        else:
            categories["business_logic"].append(path)
    return categories


def _estimate_complexity(pr_diff: str, files: Dict[str, str]) -> str:
    """Estimate diff complexity: LOW | MEDIUM | HIGH."""
    lines = len(pr_diff.splitlines())
    file_count = len(files)
    if lines < 50 and file_count <= 3:
        return "LOW"
    if lines < 300 and file_count <= 15:
        return "MEDIUM"
    return "HIGH"


def _estimate_risk(categories: Dict[str, List[str]], pr_diff: str) -> str:
    """Estimate base risk level before any specialist runs."""
    diff_upper = pr_diff.upper()
    if (
        categories["auth"]
        or categories["security"]
        or "SECRET" in diff_upper
        or "PASSWORD" in diff_upper
        or "JWT" in diff_upper
    ):
        return "HIGH"
    if categories["infra"] or categories["config"]:
        return "MEDIUM"
    if categories["docs"] and not categories["business_logic"] and not categories["auth"]:
        return "LOW"
    return "MEDIUM"


# ---------------------------------------------------------------------------
# Execution Plan builder
# ---------------------------------------------------------------------------

_ALL_SPECIALISTS = [
    "Security Officer",
    "Principal Architect",
    "QA Director",
    "DevOps Lead",
    "Red Team",
]

_AGENT_COST_ESTIMATE = {          # approximate USD per agent at average diff size
    "Security Officer":    0.018,
    "Principal Architect": 0.014,
    "QA Director":         0.012,
    "DevOps Lead":         0.010,
    "Red Team":            0.022,
}


class ExecutionPlan:
    """Structured result from the Planning Agent."""

    def __init__(
        self,
        agents_to_run: List[str],
        agents_skipped: Dict[str, str],
        complexity: str,
        estimated_risk: str,
        categories: Dict[str, List[str]],
        estimated_cost_usd: float,
        reasoning: str,
    ):
        self.agents_to_run = agents_to_run
        self.agents_skipped = agents_skipped        # agent_role → skip reason
        self.complexity = complexity
        self.estimated_risk = estimated_risk
        self.categories = categories
        self.estimated_cost_usd = round(estimated_cost_usd, 4)
        self.reasoning = reasoning

    def should_run(self, agent_role: str) -> bool:
        return agent_role in self.agents_to_run

    def skip_reason(self, agent_role: str) -> Optional[str]:
        return self.agents_skipped.get(agent_role)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agents_to_run":       self.agents_to_run,
            "agents_skipped":      self.agents_skipped,
            "complexity":          self.complexity,
            "estimated_risk":      self.estimated_risk,
            "categories":          {k: v for k, v in self.categories.items() if v},
            "estimated_cost_usd":  self.estimated_cost_usd,
            "reasoning":           self.reasoning,
        }


class PlanningAgent:
    """Autonomous Planning Agent — determines dynamic specialist execution plan."""

    def __init__(self):
        self.role = "Planning Agent"

    def create_plan(
        self,
        pr_diff: str,
        repo_files: Dict[str, str],
        historical_stats: Optional[Dict[str, Any]] = None,
    ) -> ExecutionPlan:
        """Analyse the PR and produce an execution plan."""
        tracer = AgentTracer(agent_role=self.role)
        t0 = time.perf_counter()

        categories = _classify_files(repo_files)
        complexity  = _estimate_complexity(pr_diff, repo_files)
        risk        = _estimate_risk(categories, pr_diff)

        agents_to_run: List[str] = []
        agents_skipped: Dict[str, str] = {}
        reasons: List[str] = []

        # --- Decision logic per specialist ---

        # Security Officer: run if auth/security files changed or diff contains secrets
        diff_upper = pr_diff.upper()
        has_secret_smell = any(kw in diff_upper for kw in ["SECRET", "JWT", "PASSWORD", "TOKEN", "APIKEY", "API_KEY"])
        if categories["auth"] or categories["security"] or has_secret_smell or risk == "HIGH":
            agents_to_run.append("Security Officer")
            reasons.append("Security Officer: authentication, security, or secret-bearing files detected.")
        else:
            agents_skipped["Security Officer"] = "No authentication or security-sensitive files in changeset."

        # Principal Architect: run unless purely docs/tests
        only_docs_tests = (
            not categories["auth"]
            and not categories["business_logic"]
            and not categories["config"]
            and not categories["infra"]
            and not categories["security"]
        )
        if not only_docs_tests:
            agents_to_run.append("Principal Architect")
            reasons.append("Principal Architect: structural/logic changes require architectural evaluation.")
        else:
            agents_skipped["Principal Architect"] = "Only documentation or test files changed — no structural review needed."

        # QA Director: run if business logic changed or auth changed (missing edge-case tests likely)
        if categories["business_logic"] or categories["auth"] or complexity in ("MEDIUM", "HIGH"):
            agents_to_run.append("QA Director")
            reasons.append("QA Director: business logic or auth changes require test-coverage validation.")
        else:
            agents_skipped["QA Director"] = "Only documentation or infrastructure files changed — QA skipped."

        # DevOps Lead: run if infra/config changed
        if categories["infra"] or categories["config"]:
            agents_to_run.append("DevOps Lead")
            reasons.append("DevOps Lead: infrastructure or configuration files detected.")
        else:
            agents_skipped["DevOps Lead"] = "No infrastructure or deployment configuration changed."

        # Red Team: run only on HIGH risk (can also be triggered dynamically by Security collaboration request)
        if risk == "HIGH" or has_secret_smell:
            agents_to_run.append("Red Team")
            reasons.append("Red Team: high-risk changeset — proactive exploit simulation required.")
        else:
            agents_skipped["Red Team"] = (
                "Risk classified as non-critical. Red Team may be launched dynamically "
                "if Security Officer discovers exploitable vulnerabilities."
            )

        # If only docs changed → skip almost everything
        all_docs = all(not v for k, v in categories.items() if k != "docs") and categories["docs"]
        if all_docs:
            agents_to_run = []
            agents_skipped = {a: "Only documentation files changed — full council review skipped." for a in _ALL_SPECIALISTS}
            reasons = ["Only Markdown/documentation files detected. Governance review not required."]
            risk = "LOW"

        estimated_cost = sum(_AGENT_COST_ESTIMATE.get(a, 0.01) for a in agents_to_run)
        reasoning = " | ".join(reasons) if reasons else "Minimal changeset — no specialist execution required."

        tracer.record_tool_call(
            tool_name="file_classifier",
            input_summary=f"Classified {len(repo_files)} files into {sum(1 for v in categories.values() if v)} active categories",
            output_summary=f"Risk={risk}, Complexity={complexity}, Agents={agents_to_run}",
            duration_ms=round((time.perf_counter() - t0) * 1000.0, 2),
        )
        reason_with_llm(tracer, self.role, pr_diff)

        plan = ExecutionPlan(
            agents_to_run=agents_to_run,
            agents_skipped=agents_skipped,
            complexity=complexity,
            estimated_risk=risk,
            categories=categories,
            estimated_cost_usd=estimated_cost,
            reasoning=reasoning,
        )

        summary = (
            f"Execution plan: run {len(agents_to_run)} agent(s), "
            f"skip {len(agents_skipped)}, risk={risk}, complexity={complexity}."
        )
        tracer.finalize(reasoning_summary=summary, risk_level=risk)

        plan._tracer_dict = tracer.to_dict()  # attach trace to plan for observability
        return plan
