"""Agent Observability Tracer & Cost Analytics Engine."""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional

# Standard Pricing Matrix per 1M Tokens (USD)
PRICING_MATRIX: Dict[str, Dict[str, float]] = {
    "qwen2.5-coder:14b": {"input": 0.0, "output": 0.0},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "default": {"input": 3.00, "output": 15.00},
}


def calculate_token_cost(provider_model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute token cost in USD based on input/output token counts."""
    pricing = PRICING_MATRIX.get(provider_model, PRICING_MATRIX["default"])
    input_cost = (input_tokens / 1_000_000.0) * pricing["input"]
    output_cost = (output_tokens / 1_000_000.0) * pricing["output"]
    return round(input_cost + output_cost, 6)


class AgentTracer:
    """Trace collector for an individual AI agent execution."""

    def __init__(self, agent_role: str, llm_provider: str = "ollama", model: str = "qwen2.5-coder:14b"):
        self.agent_role = agent_role
        self.llm_provider = llm_provider
        self.model = model
        self.start_time = datetime.now(timezone.utc)
        self._start_perf = time.perf_counter()
        
        self.end_time: Optional[datetime] = None
        self.duration_ms: float = 0.0
        
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.total_tokens: int = 0
        self.estimated_cost: float = 0.0
        
        self.llm_call_count: int = 0
        self.tool_call_count: int = 0
        self.files_read: int = 0
        self.files_modified: int = 0
        self.errors: int = 0
        self.warnings: int = 0
        
        self.risk_level: str = "LOW"
        self.reasoning_summary: str = ""
        self.tool_calls: List[Dict[str, Any]] = []

    def set_llm_identity(self, provider: str, model: str) -> None:
        self.llm_provider, self.model = provider, model

    def record_llm_call(self, input_tokens: int, output_tokens: int, duration_ms: float = 0.0, estimated: bool = False) -> None:
        """Record an LLM call invocation and update token/cost metrics."""
        self.llm_call_count += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens += (input_tokens + output_tokens)
        cost = calculate_token_cost(self.model, input_tokens, output_tokens)
        self.estimated_cost = round(self.estimated_cost + cost, 6)
        if estimated:
            self.warnings += 1

    def record_tool_call(self, tool_name: str, input_summary: str, output_summary: str, duration_ms: float = 0.0) -> Dict[str, Any]:
        """Record a tool execution (Semgrep, Bandit, GitHub API, Repo Parser)."""
        self.tool_call_count += 1
        call_record = {
            "tool_name": tool_name,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.tool_calls.append(call_record)
        return call_record

    def finalize(self, reasoning_summary: str, risk_level: str = "LOW", errors: int = 0, warnings: int = 0) -> Dict[str, Any]:
        """Stop timing and finalize agent trace summary."""
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = round((time.perf_counter() - self._start_perf) * 1000.0, 2)
        self.reasoning_summary = reasoning_summary
        self.risk_level = risk_level
        self.errors = errors
        self.warnings = warnings

        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_role": self.agent_role,
            "status": "COMPLETED",
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "llm_provider": self.llm_provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "llm_call_count": self.llm_call_count,
            "tool_call_count": self.tool_call_count,
            "files_read": self.files_read,
            "files_modified": self.files_modified,
            "errors": self.errors,
            "warnings": self.warnings,
            "risk_level": self.risk_level,
            "reasoning_summary": self.reasoning_summary,
            "tool_calls": self.tool_calls,
        }
