# Tech Stack

## Product: {{PRODUCT_NAME}}

| Layer | Default | Notes |
|-------|---------|-------|
| Orchestration | LangGraph | Feature / BugFix / Release graphs |
| Agent helpers | LangChain | Tools / prompts |
| LLM | {{LLM_PROVIDER}} | Model: `{{DEFAULT_MODEL}}` |
| Language | Python 3.11+ | `runtime/` |
| API | FastAPI | Operator / external API (optional) |
| Data | PostgreSQL | Tasks, audit (optional) |
| Observability | LangSmith | Project: `{{LANGSMITH_PROJECT}}` |
| Packaging | uv | Lockfile recommended |

## Knowledge

| Asset | Location |
|-------|----------|
| Company OS | `company/`, `roles/`, `skills/`, `workflows/` |
| Specs | `docs/`, `projects/` |
| Decisions | `memory/decision-memory/` |
| Agents | `agents/*.yaml` |
| Graphs | `langgraph/` |

## Forbidden without ADR

- Second orchestration framework beside LangGraph
- Secrets in git
- Skipping Reviewer/QA on production path
