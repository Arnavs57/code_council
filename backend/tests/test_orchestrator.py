"""Tests for EngineeringCouncilOrchestrator and complete 6-agent review execution."""

import pytest

from app.orchestrator.orchestrator import EngineeringCouncilOrchestrator


@pytest.mark.asyncio
async def test_council_orchestrator_execution() -> None:
    orchestrator = EngineeringCouncilOrchestrator()
    result = await orchestrator.run_council_review(
        owner="acme-test",
        repo="demo-repo",
        pr_number=101,
        head_sha="1234567890abcdef1234567890abcdef12345678",
        pr_title="feat: add new endpoint",
        author="developer",
        pr_diff="+ def new_function(): return True\n",
        repo_files={"app/main.py": "print('hello')", "tests/test_main.py": "def test_main(): pass"},
    )

    assert result["overall_verdict"] in ("GO", "NEEDS_CHANGES", "NO_GO")
    assert result["production_readiness"] > 0
    # Offline test runs do not fabricate token counts when no provider is live.
    assert result["total_tokens"] >= 0
    assert result["total_cost"] >= 0
    assert "Code Council AI" in result["comment_markdown"]
