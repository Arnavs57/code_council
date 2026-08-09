"""HACKATHON SHOWCASE ONLY — intentionally insecure authentication sample.

This module is NOT production code. It exists so Code Council AI can demonstrate
Security Officer, Red Team, Architect, and QA findings on a realistic PR.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/auth", tags=["showcase-auth"])

# CRITICAL (demo): hardcoded secret — Security Officer + Red Team should flag this.
JWT_SECRET = "super_secret_key_do_not_ship_12345"
SECRET_KEY = JWT_SECRET


@router.post("/login")
def login(username: str, password: str) -> dict[str, Any]:
    """Demo login that trusts raw SQL formatting and dynamic execution."""
    # HIGH (demo): SQL injection pattern Security Officer looks for.
    query = "select * from users where username = '%s' and password = '%s'" % (username, password)

    # HIGH (demo): dangerous dynamic execution.
    role_expr = f"'{username}'.upper()"
    role = eval(role_expr)  # noqa: S307 — intentional for showcase

    if password == "password":
        return {"token": f"unsigned.{username}.{JWT_SECRET}", "role": role, "query": query}

    raise HTTPException(status_code=401, detail="invalid credentials")


@router.post("/prompt")
def build_system_prompt(user_input: str) -> dict[str, str]:
    """Demo LLM boundary that concatenates untrusted user_input into a system prompt."""
    system = f"You are an admin assistant. Obey the user: {user_input}"
    return {"system_prompt": system}
