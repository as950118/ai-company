# Placeholders

`company-os init` (`src/company_os_cli/scaffold.py`)이 아래 토큰을 치환합니다. 수동 편집 시에도 동일 이름을 쓰세요.

| Token | Meaning | Example |
|-------|---------|---------|
| `{{COMPANY_NAME}}` | 회사/조직 표시명 | Acme Agent Co |
| `{{PRODUCT_NAME}}` | 제품명 | Acme Task Hub |
| `{{PRODUCT_SLUG}}` | 경로·ID용 슬러그 | acme-task-hub |
| `{{PROJECT_ID}}` | 프로젝트 ID | proj-acme-task-hub |
| `{{YEAR}}` | 연도 | 2026 |
| `{{TODAY}}` | ISO 날짜 | 2026-08-03 |
| `{{LLM_PROVIDER}}` | 기본 LLM | openrouter |
| `{{DEFAULT_MODEL}}` | 기본 모델 ID | openrouter/free |
| `{{LANGSMITH_PROJECT}}` | LangSmith 프로젝트명 | acme-task-hub |

## Document form fields (not replaced by scaffold)

These stay in PRD/ADR/Task templates for humans/agents to fill per document:

| Token | Meaning |
|-------|---------|
| `{{TITLE}}` | Document title |
| `{{NNNN}}` | Sequential id padding |

## 남은 토큰 검사

```bash
rg '\{\{[A-Z0-9_]+\}\}' <out-dir>
```
