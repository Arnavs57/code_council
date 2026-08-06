"""GitHub API integration service — posts Check Runs and Pull Request comments."""

import logging
import os
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger("app.github")


class GitHubService:
    """Client for interacting with GitHub REST API (Checks API & Issue Comments)."""

    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token or os.getenv("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def create_check_run(
        self,
        owner: str,
        repo: str,
        head_sha: str,
        name: str = "Code Council AI Governance",
        status: str = "completed",
        conclusion: str = "success",
        output: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a GitHub Check Run on the commit."""
        url = f"{self.base_url}/repos/{owner}/{repo}/check-runs"
        payload = {
            "name": name,
            "head_sha": head_sha,
            "status": status,
            "conclusion": conclusion,
        }
        if output:
            payload["output"] = output

        if not self.token:
            logger.info("GitHub Token not configured; mock check run created.", extra={"payload": payload})
            return {"id": 1001, "status": status, "conclusion": conclusion, "url": f"https://github.com/{owner}/{repo}/runs/1001"}

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self.headers, json=payload, timeout=10.0)
            if resp.status_code in (200, 201):
                return resp.json()
            logger.error("Failed to create GitHub Check Run", extra={"status": resp.status_code, "body": resp.text})
            return {"error": resp.text, "status_code": resp.status_code}

    async def create_pr_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
    ) -> Dict[str, Any]:
        """Create or update the single council comment on the Pull Request."""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        marker = "<!-- code-council-ai:governance-report -->"
        body = f"{marker}\n{body}"
        payload = {"body": body}

        if not self.token:
            logger.info("GitHub Token not configured; mock PR comment posted.", extra={"owner": owner, "repo": repo, "pr": pr_number})
            return {"id": 2002, "body": body, "html_url": f"https://github.com/{owner}/{repo}/pull/{pr_number}#issuecomment-2002"}

        async with httpx.AsyncClient() as client:
            existing = await client.get(url, headers=self.headers, params={"per_page": 100}, timeout=10.0)
            if existing.status_code == 200:
                for comment in existing.json():
                    if marker in comment.get("body", ""):
                        resp = await client.patch(
                            f"{url}/{comment['id']}", headers=self.headers, json=payload, timeout=10.0
                        )
                        if resp.status_code == 200:
                            return resp.json()
                        logger.error("Failed to update GitHub PR comment", extra={"status": resp.status_code, "body": resp.text})
                        return {"error": resp.text, "status_code": resp.status_code}
            resp = await client.post(url, headers=self.headers, json=payload, timeout=10.0)
            if resp.status_code in (200, 201):
                return resp.json()
            logger.error("Failed to post GitHub PR comment", extra={"status": resp.status_code, "body": resp.text})
            return {"error": resp.text, "status_code": resp.status_code}
