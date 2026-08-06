"""Tests for AgentTracer, token analytics, and cost calculations."""

from app.observability.tracer import AgentTracer, calculate_token_cost


def test_calculate_token_cost_claude_3_5() -> None:
    # 1,000,000 input tokens = $3.00, 1,000,000 output tokens = $15.00
    cost = calculate_token_cost("claude-3-5-sonnet-20241022", 1_000_000, 1_000_000)
    assert cost == 18.00


def test_agent_tracer_llm_calls() -> None:
    tracer = AgentTracer(agent_role="Security Officer", llm_provider="openai", model="gpt-4o")
    tracer.record_llm_call(input_tokens=10_000, output_tokens=1_000)
    tracer.record_tool_call(tool_name="semgrep", input_summary="diff", output_summary="clean")
    
    summary = tracer.finalize(reasoning_summary="Security approved", risk_level="LOW")
    
    assert summary["agent_role"] == "Security Officer"
    assert summary["llm_call_count"] == 1
    assert summary["tool_call_count"] == 1
    assert summary["input_tokens"] == 10_000
    assert summary["output_tokens"] == 1_000
    assert summary["total_tokens"] == 11_000
    assert summary["estimated_cost"] > 0
    assert summary["risk_level"] == "LOW"
