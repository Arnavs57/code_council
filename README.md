<div align="center">

# 🏛️ Code Council AI

### AI Engineering Governance Platform

**An Autonomous Multi-Agent Pull Request Review Board for GitHub**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)]()
[![React](https://img.shields.io/badge/React-19-61DAFB)]()
[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF)]()
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black)]()
[![License](https://img.shields.io/badge/License-MIT-green)]()

*"A software engineering review board—not just another AI code reviewer."*

</div>

---

# 🚀 Overview

Code Council AI is an **AI-powered engineering governance platform** that transforms traditional pull request reviews into a collaborative decision-making process using multiple specialized AI agents.

Instead of relying on a single AI reviewer, Code Council AI dynamically assembles an expert review board consisting of specialists such as:

- 🔒 Security Officer
- 🏗 Principal Architect
- 🧪 QA Director
- ⚙️ DevOps Lead
- 🛡 Red Team
- 👑 Release Manager

Each agent independently evaluates the pull request, collaborates through a shared orchestration layer, and contributes toward a final release decision.

The result is an **auditable, explainable, and enforceable** review process directly integrated into GitHub.

---

# ✨ Key Features

## 🤖 Multi-Agent AI Review

Different AI agents specialize in different engineering domains rather than relying on one generic LLM.

---

## 🧠 Intelligent Planning Agent

Before reviewing begins, a Planning Agent determines:

- Which agents should participate
- Which agents can safely be skipped
- Estimated review cost
- Risk level
- Review complexity

This dramatically reduces unnecessary LLM usage.

---

## 🤝 Collaborative Decision Making

Agents don't work independently.

Instead they communicate through a structured shared state where they can:

- Request additional investigation
- Ask questions
- Escalate risks
- Validate findings
- Share evidence

---

## 🚦 Release Governance

Instead of simply commenting on a PR, Code Council AI produces one of three enforceable outcomes:

| Verdict | Meaning |
|----------|----------|
| ✅ GO | Safe to merge |
| ⚠ NEEDS_CHANGES | Improvements required |
| ❌ NO_GO | Merge blocked |

The verdict is published as a **GitHub Check Run**, allowing organizations to enforce engineering policies automatically.

---

## 📊 Full Observability

Every review stores:

- Timeline
- Tool usage
- Token consumption
- Confidence scores
- Risk scores
- Agent reasoning
- Historical memory

making every decision completely auditable.

---

# 🏗 System Architecture

```text
          Pull Request Opened
                   │
                   ▼
          GitHub Actions Workflow
                   │
                   ▼
         Engineering Orchestrator
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
 Planning Agent         Memory Service
        │
        ▼
 Dynamic Agent Selection
        │
        ▼
 ┌───────────────────────────────┐
 │ Security Officer              │
 │ Principal Architect           │
 │ QA Director                   │
 │ DevOps Lead                   │
 │ Red Team                      │
 └───────────────────────────────┘
               │
               ▼
        Release Manager
               │
               ▼
GitHub PR Comment + Check Run
```

---

# 🛠 Technology Stack

## Backend

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic Settings
- HTTPX

## AI

- Ollama
- Qwen2.5-Coder
- OpenAI (Fallback)

## Frontend

- React 19
- Vite
- Tailwind CSS
- Radix UI

## DevOps

- GitHub Actions
- Self-hosted Runner

---

# 📂 Repository Structure

```text
code_council/
│
├── backend/
│   ├── agents/
│   ├── orchestrator/
│   ├── llm/
│   ├── services/
│   ├── observability/
│   ├── models/
│   └── api/
│
├── frontend/
│
├── demo/
│
├── .github/
│   └── workflows/
│
├── ARCHITECTURE.md
├── CONFIGURATION_ARCHITECTURE.md
└── REPOSITORY_STRUCTURE.md
```

---

# 🧩 AI Agent Roles

| Agent | Responsibility |
|--------|----------------|
| 🧠 Planning Agent | Determines review strategy |
| 🔒 Security Officer | Security vulnerabilities & secrets |
| 🏗 Principal Architect | Code quality & architecture |
| 🧪 QA Director | Testing & coverage |
| ⚙️ DevOps Lead | Infrastructure & deployment |
| 🛡 Red Team | Exploit validation |
| 👑 Release Manager | Final engineering verdict |

---

# 🔄 Review Workflow

1. Pull Request is opened
2. GitHub Action starts
3. Files are indexed
4. Historical memory is loaded
5. Planning Agent selects reviewers
6. Specialists perform analysis
7. Agents collaborate
8. Release Manager combines findings
9. GitHub Check Run is updated
10. PR receives an engineering governance report

---

# 📈 Sample Verdicts

## ✅ GO

- No critical findings
- High readiness
- Safe to merge

---

## ⚠ NEEDS_CHANGES

- Minor issues detected
- Tests missing
- Improvements recommended

---

## ❌ NO_GO

- Critical vulnerabilities
- High deployment risk
- Merge blocked

---

# ⚡ Running Locally

## Backend

```bash
cd backend

pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Requirements

- Python 3.10+
- Node.js
- Ollama
- GitHub Self-hosted Runner

---

# 🎯 Why Code Council AI?

Traditional AI code reviewers:

- One opinion
- Static analysis
- No collaboration
- No governance
- Limited explainability

Code Council AI provides:

✅ Multiple engineering experts

✅ Dynamic review planning

✅ Cross-agent collaboration

✅ Engineering governance

✅ GitHub-native integration

✅ Explainable AI decisions

✅ Complete audit trail

---

# 🔮 Future Roadmap

- Redis Event Bus
- LangGraph orchestration
- Multi-tenant SaaS
- WebSocket Mission Control
- Live Engineering War Room
- Enterprise dashboards
- Sandbox execution
- Advanced security scanning

---

# 🏆 Built For

- AI Hackathons
- Engineering Teams
- DevSecOps
- Platform Engineering
- Enterprise CI/CD
- Software Governance

---

# 👨‍💻 Team

Built with ❤️ to reimagine software engineering governance using autonomous AI agents.

---

<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

**Engineering Governance. Powered by AI.**

Frontend Demo simulation file showing agent conversation streams and llm and api call stats present here : "https://github.com/vixkumar/Agentic-AI-Code-Council"

</div>
