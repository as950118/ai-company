# company-os-cli

재사용 가능한 **Multi-Agent Company Operating System** 스켈레톤을 pip으로 설치해 CLI 한 줄로 만들어내는 도구입니다.
Role · Skill · Workflow · Memory를 Git Markdown(SSOT)으로 관리하고, LangGraph/LangChain 기반 Agent가 이를 읽어 추측 없이 협업하도록 설계되었습니다.

## 설치

```bash
# PyPI에 배포된 이후
pip install company-os-cli

# 배포 전 / 최신 개발 버전을 바로 쓰고 싶다면 GitHub에서 직접 설치
pip install git+https://github.com/as950118/ai-company.git
```

설치하면 `company-os` 명령이 생깁니다.

## 빠른 시작

### A. 독립 Company OS 레포로 (SSOT 문서를 최상위에 그대로 노출)

이 프로젝트 자체가 "회사 운영체제"인 경우 — GitHub에서 열었을 때 `company/`, `roles/`, `skills/`가 바로 보이는 게 맞습니다.

```bash
company-os init \
  --name "Acme Agent Co" \
  --product "Acme Task Hub" \
  --slug acme-task-hub \
  --out ./my-company-os

cd my-company-os
```

### B. 기존 프로젝트에 얹기 (숨김 폴더로 격리)

이미 소스코드가 있는 프로젝트에 Company OS를 추가하는 경우, `--out`을 생략하면 현재 폴더의 **`.company-os/`**(`.git`, `.github`, `.vscode`, `.cursor`와 같은 패턴)에 자동으로 만들어져 기존 폴더 구조(예: 이미 있는 `docs/`, `runtime/`)와 충돌하지 않습니다.

```bash
cd my-existing-project
company-os init --name "Acme Agent Co" --product "Acme Task Hub"
# → ./.company-os/ 에 생성됨
```

```bash
company-os --version
company-os init --help
```

옵션:

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--name` | 회사 표시명 | (필수) |
| `--product` | 제품명 | (필수) |
| `--out` | 생성 경로 | 현재 폴더의 `./.company-os` |
| `--slug` | 경로/ID용 슬러그 | `--product`에서 자동 생성 |
| `--force` | 비어있지 않은 폴더에 덮어쓰기 허용 | off |
| `--llm-provider` | 기본 LLM 프로바이더 | `openrouter` |
| `--model` | 기본 모델 ID | `openrouter/free` |
| `--langsmith-project` | LangSmith 프로젝트명 | slug와 동일 |

생성 후:

1. `cd <out>` 후 `company/vision.md` 등 플레이스홀더 잔여(`{{…}}`) 검색: `rg '\{\{[A-Z0-9_]+\}\}'`
2. `runtime/.env.example` → `.env` 복사, OpenRouter / LangSmith 키 설정
3. `workflows/create-feature.md`로 첫 Feature 시작

## 생성되는 구조

```text
my-company-os/
├── README.md                  ← 제품용 README (TEMPLATE_README.md에서 렌더링됨)
├── company/                   ← Vision / Mission / Values / Org / Tech Stack / Glossary
├── roles/                     ← Role별 R&R + System Prompt (9종)
├── skills/                    ← 역할 공통 재사용 절차 (write-prd, write-adr, create-api …)
├── workflows/                 ← create-feature / fix-bug / release / incident / onboarding
├── docs/                      ← PRD·Architecture·API·Task·ADR 템플릿 + 협업 규칙
├── agents/                    ← Role별 Agent YAML (도구·메모리·핸드오프·시스템 프롬프트)
├── langgraph/                 ← Feature/BugFix/Release Graph 설계 (Markdown SSOT)
├── memory/                    ← 5종 Memory 인덱스 (company/project/decision/task/lessons-learned)
├── projects/<slug>/           ← 첫 프로젝트 (prd/architecture/adr/api)
├── tasks/                     ← Task 인덱스
└── runtime/                   ← LangChain/LangGraph 최소 Python 스텁 (company_os 패키지)
```

## 설계 원칙 (Kit이 강제하는 것)

1. **Git Markdown = SSOT** — 모든 지식은 Role/Skill/Workflow/Memory로 문서화
2. **Role / Skill / Workflow 분리** — 한 Agent가 모든 역할을 하지 않는다
3. **승인 게이트 없이 Prod 금지** — Reviewer → QA → DevOps 순서 강제
4. **ADR로 결정 기록** — 기술 선택은 반드시 `memory/decision-memory/`에 남긴다
5. **추측 금지 — 문서 없으면 질문**

## 협업 파이프라인

```text
CEO → PM → Architect → Backend/Frontend → Reviewer → QA → Release(DevOps)
                                                              ↘ Technical Writer (문서화 지원, 전 단계 개입 가능)
```

생성된 프로젝트의 [`docs/agent-collaboration-rules.md`](src/company_os_cli/template/docs/agent-collaboration-rules.md)에서 Stage Contract를 확인할 수 있습니다.

## Cursor에서 쓰기

새 프로젝트에 스캐폴드한 뒤:

```text
당신은 {{PRODUCT_NAME}} Company OS의 Architect다.
company/, roles/, workflows/를 읽고 추측하지 마라.
지금은 create-feature의 Design 단계만 수행한다.
```

## 이 레포 구조 (패키지 개발자용)

```text
ai-company/                        ← company-os-cli 패키지 소스 레포
├── pyproject.toml                  ← 패키징 메타데이터 (hatchling, entry point: company-os)
├── LICENSE
├── src/company_os_cli/
│   ├── __init__.py                 ← __version__
│   ├── cli.py                      ← Typer CLI (`company-os` 명령)
│   ├── scaffold.py                 ← 핵심 스캐폴딩 로직 (CLI 비의존, 테스트/재사용 가능)
│   └── template/                   ← 위 "생성되는 구조"의 원본 (company/, roles/, skills/ …)
├── tests/test_scaffold.py          ← scaffold() 함수 + CLI 엔드투엔드 스모크 테스트
└── .github/workflows/              ← CI (테스트) + publish (태그 push 시 PyPI 배포)
```

### 로컬 개발

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

company-os --version
python -m unittest discover -s tests -v

# 배포용 빌드 확인
python -m build
python -m zipfile -l dist/company_os_cli-*-py3-none-any.whl
```

### 릴리스 (PyPI 배포)

1. `pyproject.toml`의 `version`을 올린다
2. `git tag v0.1.0 && git push origin v0.1.0`
3. `.github/workflows/publish.yml`이 태그 push 시 테스트 → 빌드 → PyPI 업로드까지 수행
   - PyPI [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)을 이 레포/워크플로에 등록해두면 별도 토큰 없이 동작합니다
   - 대신 API 토큰을 쓰려면 `publish.yml` 주석 참고 후 `PYPI_API_TOKEN` 시크릿 추가

## 실습 산출물 안내

실제 실행 로그, Review dump 등 산출물은 이 레포(Kit)에 포함하지 않습니다. `company-os init`으로 생성한 각 프로젝트의 `memory/`, `projects/<slug>/`에 쌓아가세요.
