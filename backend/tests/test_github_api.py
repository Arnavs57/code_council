"""Tests for GitHub API webhook endpoint /api/v1/github/event."""

def test_github_event_endpoint_success(client) -> None:
    payload = {
        "owner": "acme-corp",
        "repo": "security-service",
        "pr_number": 88,
        "head_sha": "f0e9d8c7b6a54321f0e9d8c7b6a54321f0e9d8c7",
        "base_sha": "main",
        "pr_title": "fix(security): resolve prompt injection vulnerability",
        "author": "senior-dev",
        "pr_diff": "+ def sanitize_prompt(user_input: str) -> str:\n+     return user_input.replace('system:', '')\n",
    }

    response = client.post("/api/v1/github/event", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "verdict" in data
    assert "production_readiness" in data
    assert "github_comment" in data
    assert "Code Council AI" in data["github_comment"]
