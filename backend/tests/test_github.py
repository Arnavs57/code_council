"""Tests for PR comment formatting and Check Run payload generation."""

from app.services.formatter import format_check_run_output, format_pr_comment


def test_format_pr_comment_structure() -> None:
    specialist_results = [
        {"agent_role": "Security Officer", "vote": "APPROVE", "score": 98, "findings": ["No secrets found"]},
        {"agent_role": "Principal Architect", "vote": "APPROVE", "score": 95, "findings": ["Clean design"]},
        {"agent_role": "QA Director", "vote": "NEEDS_CHANGES", "score": 70, "findings": ["Missing tests"], "suggested_tests": ["def test_foo(): pass"]},
        {"agent_role": "DevOps Lead", "vote": "APPROVE", "score": 96, "findings": ["Valid Dockerfile"]},
        {"agent_role": "Red Team", "vote": "APPROVE", "findings": ["Exploits passed"]},
    ]
    decision = {
        "overall_verdict": "NEEDS_CHANGES",
        "production_readiness": 82,
        "overall_risk": "MEDIUM",
        "security_score": 98,
        "architecture_score": 95,
        "qa_score": 70,
        "devops_score": 96,
        "trace": {"reasoning_summary": "QA requested unit tests"},
    }
    timeline_events = [
        {"timestamp": "10:22:10", "title": "GitHub Action Triggered"},
        {"timestamp": "10:22:12", "title": "Repository Indexed"},
    ]
    traces = [
        {"agent_role": "Security Officer", "llm_call_count": 1, "input_tokens": 4000, "output_tokens": 300, "total_tokens": 4300, "estimated_cost": 0.02, "duration_ms": 1500.0},
        {"agent_role": "Release Manager", "llm_call_count": 1, "input_tokens": 1500, "output_tokens": 100, "total_tokens": 1600, "estimated_cost": 0.01, "duration_ms": 500.0},
    ]

    comment = format_pr_comment(
        repo_name="acme/app",
        pr_number=42,
        specialist_results=specialist_results,
        decision=decision,
        timeline_events=timeline_events,
        traces=traces,
        total_tokens=5900,
        total_cost=0.03,
        total_duration_sec=2.0,
    )

    assert "# 🤖 Code Council AI Engineering Review" in comment
    assert "🛡️ Security Officer" in comment
    assert "🧪 QA Director" in comment
    assert "def test_foo(): pass" in comment
    assert "AI Engineering Observability & Token Analytics" in comment
    assert "Tool Execution Log" in comment
    assert "Execution Timeline" in comment


def test_format_check_run_output() -> None:
    decision = {
        "overall_verdict": "GO",
        "production_readiness": 96,
        "security_score": 98,
        "architecture_score": 95,
        "qa_score": 95,
        "devops_score": 96,
    }
    output = format_check_run_output(decision, [], 5000, 0.02)
    assert output["conclusion"] == "success"
    assert "GO" in output["title"]
