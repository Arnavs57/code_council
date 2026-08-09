# Code Council AI — Hackathon Showcase PR

This branch is a **deliberately insecure demo changeset** for hosts.

## What it demonstrates
- Dynamic planning (which agents run vs skip)
- Security Officer (hardcoded JWT/secrets, SQL injection, `eval`, prompt injection)
- Red Team (high-risk / secret-bearing diff + Security collaboration)
- Principal Architect + QA Director (auth business logic without tests)
- DevOps Lead (Dockerfile + committed `.env.production`)
- Release Manager verdict on GitHub (PR comment + Check Run)

## Files in this demo
| Path | Why it exists |
|------|----------------|
| `backend/app/api/v1/auth.py` | Auth surface with intentional CRITICAL/HIGH findings |
| `Dockerfile` | Weak production container config |
| `.env.production` | Committed production secrets (anti-pattern) |

**Do not merge these files into a real product branch without stripping the insecure samples.**
