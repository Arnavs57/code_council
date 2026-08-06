"""GitHub PR Markdown Comment & Check Run Report Formatter.

Generates the full governance report published as a PR comment and GitHub Check Run.

Sections:
  1. Header & Verdict
  2. Engineering Council Summary (per-agent)
  3. Planning Decision (agents run vs. skipped + rationale)
  4. Agent Collaboration Log (inter-agent messages)
  5. Historical Memory (unresolved findings from prior reviews)
  6. AI Observability & Token Analytics Table
  7. Execution Timeline
  8. Footer
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def format_pr_comment(
    repo_name: str,
    pr_number: int,
    specialist_results: List[Dict[str, Any]],
    decision: Dict[str, Any],
    timeline_events: List[Dict[str, Any]],
    traces: List[Dict[str, Any]],
    total_tokens: int,
    total_cost: float,
    total_duration_sec: float,
    execution_plan: Optional[Dict[str, Any]] = None,
    collaboration_messages: Optional[List[Any]] = None,
    historical_stats: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate rich, enterprise-grade GitHub PR Markdown governance report."""

    verdict  = decision["overall_verdict"]
    readiness = decision["production_readiness"]

    verdict_emoji = {
        "GO":             "✅ **GO FOR RELEASE**",
        "NEEDS_CHANGES":  "⚠️ **NEEDS CHANGES BEFORE MERGE**",
        "NO_GO":          "❌ **NO GO — RELEASE BLOCKED**",
    }.get(verdict, "❓ **PENDING**")

    md: List[str] = []

    # ── Section 1: Header ─────────────────────────────────────────────────
    md += [
        "# 🤖 Code Council AI — Autonomous Engineering Governance",
        "",
        f"### Release Decision: {verdict_emoji}",
        f"**Production Readiness Score:** `{readiness}%` | **Overall Risk:** `{decision['overall_risk']}`",
        "",
        "---",
        "",
    ]

    # ── Section 2: Engineering Council Summary ────────────────────────────
    md.append("## 🏛️ Engineering Council Summary")
    md.append("")

    vote_emoji = {
        "APPROVE":       "✅ Approve",
        "NEEDS_CHANGES": "⚠️ Needs Changes",
        "REJECT":        "❌ Reject",
    }

    role_icon = {
        "Security Officer":   "🛡️ Security Officer",
        "Principal Architect": "🏗️ Principal Architect",
        "QA Director":        "🧪 QA Director",
        "DevOps Lead":        "⚙️ DevOps Lead",
        "Red Team":           "🔴 Red Team",
    }

    for res in specialist_results:
        role = res["agent_role"]
        vote = res["vote"]
        conf = res.get("confidence", "?")

        md.append(f"### {role_icon.get(role, role)}")
        md.append(f"**Vote:** {vote_emoji.get(vote, vote)} | **Confidence:** `{conf}%`")
        if "score" in res:
            md.append(f"**Score:** `{res['score']}/100`")

        if res.get("launched_by_collaboration"):
            md.append("> 🔗 *This agent was launched via inter-agent collaboration request — not in original execution plan.*")

        md.append("")

        if res.get("findings"):
            for f in res["findings"]:
                md.append(f"- {f}")
            md.append("")

        if res.get("historical_notes"):
            md.append("**⚠️ Recurring from History:**")
            for hn in res["historical_notes"]:
                md.append(f"- {hn}")
            md.append("")

        if res.get("suggested_tests"):
            md.append("**📋 Suggested Unit Tests:**")
            md.append("```python")
            for t in res["suggested_tests"]:
                md.append(t)
            md.append("```")
            md.append("")

        md.append("---")
        md.append("")

    # Release Manager verdict
    md += [
        "### 👨‍✈️ Release Manager — Autonomous Governance Verdict",
        f"**Verdict:** `{verdict}` | **Production Readiness:** `{readiness}%`",
        "",
        f"> {decision['trace']['reasoning_summary']}",
        "",
    ]

    if decision.get("escalation_notes"):
        md.append("**Governance Interventions:**")
        for note in decision["escalation_notes"]:
            md.append(f"- {note}")
        md.append("")

    md += ["---", ""]

    # ── Section 3: Planning Decision ──────────────────────────────────────
    if execution_plan:
        md.append("## 🧭 Planning Decision")
        md.append("")
        md.append(f"**Complexity:** `{execution_plan.get('complexity', '?')}` | "
                  f"**Estimated Risk:** `{execution_plan.get('estimated_risk', '?')}` | "
                  f"**Est. Cost:** `${execution_plan.get('estimated_cost_usd', 0):.4f}`")
        md.append("")

        if execution_plan.get("agents_to_run"):
            md.append(f"**Agents Scheduled:** {', '.join(f'`{a}`' for a in execution_plan['agents_to_run'])}")

        if execution_plan.get("agents_skipped"):
            md.append("")
            md.append("**Agents Skipped:**")
            for agent, reason in execution_plan["agents_skipped"].items():
                md.append(f"- **{agent}**: *{reason}*")

        if execution_plan.get("reasoning"):
            md.append("")
            md.append(f"> 💡 **Planning Rationale:** {execution_plan['reasoning']}")

        md += ["", "---", ""]

    # ── Section 4: Agent Collaboration Log ────────────────────────────────
    if collaboration_messages:
        md.append("## 🔗 Agent Collaboration Log")
        md.append("")
        md.append("| From | To | Type | Message |")
        md.append("| :--- | :--- | :---: | :--- |")

        type_emoji = {
            "REQUEST":    "📩",
            "ANSWER":     "💬",
            "QUESTION":   "❓",
            "ESCALATION": "⚡",
            "INFO":       "ℹ️",
        }

        for msg in collaboration_messages:
            from_agent  = msg.from_agent if hasattr(msg, "from_agent") else msg.get("from_agent", "?")
            to_agent    = msg.to_agent if hasattr(msg, "to_agent") else msg.get("to_agent", "?")
            msg_type    = msg.message_type if hasattr(msg, "message_type") else msg.get("message_type", "INFO")
            message_txt = msg.message if hasattr(msg, "message") else msg.get("message", "")
            emoji       = type_emoji.get(msg_type, "ℹ️")
            short_msg   = message_txt[:120] + ("..." if len(message_txt) > 120 else "")
            md.append(f"| {from_agent} | {to_agent} | {emoji} {msg_type} | {short_msg} |")

        md += ["", "---", ""]

    # ── Section 5: Historical Memory ─────────────────────────────────────
    if historical_stats and historical_stats.get("reviews_analysed", 0) > 0:
        md.append("## 📚 Organisational Memory")
        md.append("")
        md.append(
            f"**Reviews Analysed:** `{historical_stats['reviews_analysed']}` | "
            f"**Avg Tokens:** `{historical_stats.get('avg_tokens', 0):,}` | "
            f"**Avg Cost:** `${historical_stats.get('avg_cost_usd', 0):.4f}` | "
            f"**Avg Duration:** `{historical_stats.get('avg_duration_sec', 0):.2f}s`"
        )
        unresolved = historical_stats.get("unresolved_highs", 0)
        if unresolved > 0:
            md.append(f"> ⚠️ **{unresolved} unresolved HIGH/CRITICAL finding(s)** from previous reviews were surfaced to agents.")
        md += ["", "---", ""]

    # ── Section 6: Observability & Token Analytics ────────────────────────
    md.append("## 📊 AI Engineering Observability & Token Analytics")
    md.append("")
    md.append("| Agent | LLM Calls | Input Tokens | Output Tokens | Total Tokens | Cost (USD) | Confidence | Duration |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    for trace in traces:
        agent = trace["agent_role"]
        calls = trace["llm_call_count"]
        inp   = trace["input_tokens"]
        outp  = trace["output_tokens"]
        tot   = trace["total_tokens"]
        cost  = f"${trace['estimated_cost']:.4f}"
        conf  = f"{trace.get('confidence', '?')}%"
        dur   = f"{trace['duration_ms'] / 1000.0:.2f}s"
        md.append(f"| **{agent}** | {calls} | {inp:,} | {outp:,} | {tot:,} | {cost} | {conf} | {dur} |")

    total_calls = sum(t["llm_call_count"] for t in traces)
    total_inp   = sum(t["input_tokens"] for t in traces)
    total_outp  = sum(t["output_tokens"] for t in traces)
    md.append(
        f"| **Total Review** | **{total_calls}** | **{total_inp:,}** | **{total_outp:,}** | "
        f"**{total_tokens:,}** | **${total_cost:.4f}** | — | **{total_duration_sec:.2f}s** |"
    )
    md += ["", "---", ""]

    # Tool-level evidence is deliberately shown in GitHub, not hidden in a
    # backend log. This makes every council decision auditable from the PR.
    md.append("## Tool Execution Log")
    md.append("")
    md.append("| Agent | Tool | Duration | Result |")
    md.append("| :--- | :--- | :---: | :--- |")
    tool_rows = 0
    for trace in traces:
        for tool in trace.get("tool_calls", []):
            result = str(tool.get("output_summary", ""))[:180].replace("|", "\\|")
            md.append(f"| {trace['agent_role']} | `{tool.get('tool_name', 'unknown')}` | "
                      f"{tool.get('duration_ms', 0):.1f}ms | {result} |")
            tool_rows += 1
    if not tool_rows:
        md.append("| — | — | — | No tools were required for this review. |")
    md += ["", "---", ""]

    # ── Section 7: Execution Timeline ─────────────────────────────────────
    md.append("## ⏱️ Execution Timeline")
    md.append("")
    for event in timeline_events:
        ts     = event.get("timestamp", "")
        title  = event.get("title", "")
        desc   = event.get("description", "")
        e_type = event.get("event_type", "INFO")
        icon   = {"TRIGGER": "📥", "INDEX": "🗂️", "AGENT_START": "▶️", "AGENT_END": "✅", "DECISION": "⚖️"}.get(e_type, "•")
        desc_s = f" — *{desc}*" if desc else ""
        md.append(f"`{ts}`  {icon}  **{title}**{desc_s}")
        md.append("↓")

    md.append("`DONE`  🎉  **Autonomous Governance Review Completed**")
    md += [
        "",
        "---",
        "*Powered by **Code Council AI** — GitHub-Native Autonomous Engineering Governance Platform*",
    ]

    return "\n".join(md)


def format_check_run_output(
    decision: Dict[str, Any],
    specialist_results: List[Dict[str, Any]],
    total_tokens: int,
    total_cost: float,
) -> Dict[str, Any]:
    """Format payload for GitHub Checks API Check Run."""

    verdict   = decision["overall_verdict"]
    readiness = decision["production_readiness"]

    conclusion_map = {
        "GO":            "success",
        "NEEDS_CHANGES": "neutral",
        "NO_GO":         "failure",
    }
    conclusion = conclusion_map.get(verdict, "neutral")

    title   = f"Code Council AI Verdict: {verdict} ({readiness}% Readiness)"
    summary = (
        f"### Production Readiness: {readiness}%\n"
        f"**Security Score:** {decision['security_score']}/100 | "
        f"**Architecture Score:** {decision['architecture_score']}/100 | "
        f"**QA Score:** {decision['qa_score']}/100 | "
        f"**DevOps Score:** {decision['devops_score']}/100\n\n"
        f"**Total Tokens Consumed:** {total_tokens:,} (${total_cost:.4f})"
    )

    return {
        "name":       "Code Council AI Governance",
        "conclusion": conclusion,
        "title":      title,
        "summary":    summary,
    }
