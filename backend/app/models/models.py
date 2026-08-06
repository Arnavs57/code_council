"""Database ORM models for Code Council AI."""

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return uuid.uuid4().hex


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner = Column(String(100), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    default_branch = Column(String(50), default="main")
    created_at = Column(DateTime, default=utc_now)

    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")


class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repo_id = Column(String(36), ForeignKey("repositories.id"), nullable=False)
    pr_number = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    head_sha = Column(String(40), nullable=False)
    base_sha = Column(String(40), nullable=False)
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    repository = relationship("Repository", back_populates="pull_requests")
    review_runs = relationship("ReviewRun", back_populates="pull_request", cascade="all, delete-orphan")


class ReviewRun(Base):
    __tablename__ = "review_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    pr_id = Column(String(36), ForeignKey("pull_requests.id"), nullable=False)
    status = Column(String(30), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    overall_verdict = Column(String(30), default="GO")  # GO, NEEDS_CHANGES, NO_GO
    security_score = Column(Integer, default=100)
    architecture_score = Column(Integer, default=100)
    qa_score = Column(Integer, default=100)
    devops_score = Column(Integer, default=100)
    overall_risk = Column(String(20), default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    production_readiness = Column(Integer, default=100)  # Percentage 0..100
    
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    total_llm_calls = Column(Integer, default=0)
    duration_seconds = Column(Float, default=0.0)
    execution_plan = Column(Text, nullable=True)  # JSON blob from Planning Agent

    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    pull_request = relationship("PullRequest", back_populates="review_runs")
    agent_traces = relationship("AgentTrace", back_populates="review_run", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="review_run", cascade="all, delete-orphan")


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    review_id = Column(String(36), ForeignKey("review_runs.id"), nullable=False)
    agent_role = Column(String(50), nullable=False, index=True)
    status = Column(String(30), default="COMPLETED")  # STARTED, COMPLETED, FAILED
    start_time = Column(DateTime, default=utc_now)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Float, default=0.0)

    llm_provider = Column(String(50), default="ollama")
    model = Column(String(100), default="qwen2.5-coder:14b")
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)

    llm_call_count = Column(Integer, default=0)
    tool_call_count = Column(Integer, default=0)
    files_read = Column(Integer, default=0)
    files_modified = Column(Integer, default=0)
    
    errors = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    risk_level = Column(String(20), default="LOW")
    reasoning_summary = Column(Text, nullable=True)
    confidence = Column(Integer, default=80)  # 0-100 agent self-reported confidence

    review_run = relationship("ReviewRun", back_populates="agent_traces")
    tool_calls = relationship("ToolCall", back_populates="agent_trace", cascade="all, delete-orphan")


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trace_id = Column(String(36), ForeignKey("agent_traces.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    duration_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=utc_now)

    agent_trace = relationship("AgentTrace", back_populates="tool_calls")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    review_id = Column(String(36), ForeignKey("review_runs.id"), nullable=False)
    timestamp = Column(DateTime, default=utc_now)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), default="INFO")  # INFO, SCAN, LLM_CALL, AGENT_START, AGENT_END, DECISION

    review_run = relationship("ReviewRun", back_populates="timeline_events")
