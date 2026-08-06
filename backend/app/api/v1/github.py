"""GitHub Event Webhook & Action Trigger API endpoint."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel

from app.orchestrator.orchestrator import EngineeringCouncilOrchestrator
from app.services.github import GitHubService

router = APIRouter(prefix="/github", tags=["github"])


class GitHubEventPayload(BaseModel):
    owner: str = "acme-corp"
    repo: str = "demo-app"
    pr_number: int = 42
    head_sha: str = "a1b2c3d4e5f678901234567890abcdef12345678"
    base_sha: str = "main"
    pr_title: str = "feat(auth): add JWT token refresh endpoint"
    author: str = "ai-developer"
    pr_diff: Optional[str] = None
    repo_files: Optional[Dict[str, str]] = None


@router.post("/event", summary="Trigger AI Engineering Council Review")
async def handle_github_event(
    payload: GitHubEventPayload,
    background_tasks: BackgroundTasks,
    request: Request,
) -> Dict[str, Any]:
    """Receive GitHub Action or Webhook PR event and run governance review."""
    authorization = request.headers.get("Authorization", "")
    token = authorization.removeprefix("Bearer ").strip() if authorization.startswith("Bearer ") else None
    # The action's short-lived GITHUB_TOKEN is deliberately used only for this
    # request; it is never stored with the review or written to logs.
    orchestrator = EngineeringCouncilOrchestrator(github_service=GitHubService(github_token=token))

    result = await orchestrator.run_council_review(
        owner=payload.owner,
        repo=payload.repo,
        pr_number=payload.pr_number,
        head_sha=payload.head_sha,
        base_sha=payload.base_sha,
        pr_title=payload.pr_title,
        author=payload.author,
        pr_diff=payload.pr_diff or "",
        repo_files=payload.repo_files,
    )

    return {
        "status": "success",
        "message": f"Engineering Council review executed for {payload.owner}/{payload.repo} PR #{payload.pr_number}",
        "verdict": result["overall_verdict"],
        "production_readiness": f"{result['production_readiness']}%",
        "total_tokens": result["total_tokens"],
        "total_cost_usd": result["total_cost"],
        "duration_sec": result["duration_seconds"],
        "github_comment": result["comment_markdown"],
    }
