"""Run a complete Council review directly from a GitHub Actions checkout.

This is intentionally not an HTTP client: GitHub Actions invokes the council
on the runner, and the council uses its ephemeral ``GITHUB_TOKEN`` to publish
the Check Run and the single, updatable PR report.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path

from app.database.database import init_db
from app.orchestrator.orchestrator import EngineeringCouncilOrchestrator
from app.services.github import GitHubService


def _git(*args: str, workspace: Path) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=workspace, check=True, capture_output=True, text=True,
    )
    return completed.stdout


def _changed_files(workspace: Path, base_sha: str, head_sha: str) -> dict[str, str]:
    """Collect changed, text-like files without sending unrelated repository data."""
    files: dict[str, str] = {}
    names = _git("diff", "--name-only", f"{base_sha}...{head_sha}", workspace=workspace).splitlines()
    for name in names[:150]:
        path = workspace / name
        if not path.is_file() or path.stat().st_size > 200_000:
            continue
        try:
            files[name] = path.read_text(encoding="utf-8")[:60_000]
        except UnicodeDecodeError:
            continue
    return files


async def main() -> None:
    event_path = Path(os.environ["GITHUB_EVENT_PATH"])
    event = json.loads(event_path.read_text(encoding="utf-8"))
    pr, repository = event["pull_request"], event["repository"]
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd().parent))
    base_sha, head_sha = pr["base"]["sha"], pr["head"]["sha"]
    diff = _git("diff", "--no-ext-diff", f"{base_sha}...{head_sha}", workspace=workspace)
    files = _changed_files(workspace, base_sha, head_sha)

    print(f"[Council] Indexed {len(files)} changed text file(s); starting autonomous review.")
    init_db()
    council = EngineeringCouncilOrchestrator(GitHubService(os.environ.get("GITHUB_TOKEN")))
    result = await council.run_council_review(
        owner=repository["owner"]["login"], repo=repository["name"],
        pr_number=pr["number"], head_sha=head_sha, base_sha=base_sha,
        pr_title=pr["title"], author=pr["user"]["login"], pr_diff=diff, repo_files=files,
    )
    print(f"[Council] Verdict={result['overall_verdict']} readiness={result['production_readiness']}% "
          f"agents={', '.join(result['agents_run']) or 'none'} tokens={result['total_tokens']} cost=${result['total_cost']:.4f}")
    print("[Council] GitHub Check Run and governance PR comment published.")


if __name__ == "__main__":
    asyncio.run(main())
