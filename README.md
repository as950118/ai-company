# Company OS Template Kit

재사용 가능한 **Multi-Agent Company Operating System** 스켈레톤입니다.
Role · Skill · Workflow · Memory를 Git Markdown(SSOT)으로 관리하고, LangGraph/LangChain 기반 Agent가 이를 읽어 추측 없이 협업하도록 설계되었습니다.

> 이 레포 자체가 "Kit"입니다. `scaffold.py`로 새 제품용 인스턴스를 생성하거나, 이 레포를 그대로 복제해 바로 운영할 수 있습니다.

## 구조

```text
ai-company/
├── README.md                 ← 이 문서 (Kit 설명)
├── TEMPLATE_README.md         ← 스캐폴드 결과물의 README (→ README.md로 이름 변경됨)
├── PLACEHOLDERS.md            ← {{TOKEN}} 치환 변수 목록
├── scaffold.py                ← 새 프로젝트 생성기
├── company/                   ← Vision / Mission / Values / Org / Tech Stack / Glossary
├── roles/                     ← Role별 R&R + System Prompt (9종)
├── skills/                    ← 역할 공통 재사용 절차 (write-prd, write-adr, create-api …)
├── workflows/                 ← create-feature / fix-bug / release / incident / onboarding
├── docs/                      ← PRD·Architecture·API·Task·ADR 템플릿 + 협업 규칙
├── agents/                    ← Role별 Agent YAML (도구·메모리·핸드오프·시스템 프롬프트)
├── langgraph/                 ← Feature/BugFix/Release Graph 설계 (Markdown SSOT)
├── memory/                    ← 5종 Memory 인덱스 (company/project/decision/task/lessons-learned)
├── projects/_starter/         ← 첫 프로젝트 자리 (prd/architecture/adr/api)
├── tasks/                     ← Task 인덱스
├── runtime/                   ← LangChain/LangGraph 최소 Python 스텁 (company_os 패키지)
└── tests/                     ← scaffold.py 등 Kit 자체에 대한 테스트
```

## 빠른 시작

### A. 새 제품으로 스캐폴드하기

레포 루트에서:

```bash
# 기본: ./my-company-os 생성
python3 scaffold.py \
  --name "Acme Agent Co" \
  --product "Acme Task Hub" \
  --slug acme-task-hub \
  --out ./my-company-os

# 기존 폴더에 덮어쓰기(주의)
python3 scaffold.py \
  --name "Acme" --product "Acme App" --slug acme-app \
  --out ./existing --force
```

생성 후:

1. `cd <out>` 후 `company/vision.md` 등 플레이스홀더 잔여(`{{…}}`) 검색: `rg '\{\{[A-Z0-9_]+\}\}'`
2. `runtime/.env.example` → `.env` 복사, OpenRouter / LangSmith 키 설정
3. `workflows/create-feature.md`로 첫 Feature 시작

### B. 이 레포를 바로 운영 인스턴스로 쓰기

1. `company/`, `roles/` 등의 `{{PRODUCT_NAME}}` 같은 플레이스홀더를 실제 값으로 치환 (`PLACEHOLDERS.md` 참고)
2. `cd runtime && cp .env.example .env` 후 필요한 키 설정
3. `workflows/onboarding.md`로 시작

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

자세한 Stage Contract는 [`docs/agent-collaboration-rules.md`](docs/agent-collaboration-rules.md) 참고.

## 핵심 문서 지도

| 알고 싶은 것 | 문서 |
|---|---|
| 회사가 왜 존재하는가 | `company/vision.md`, `company/mission.md`, `company/values.md` |
| 누가 무엇을 결정하는가 | `company/org-chart.md` |
| 어떤 기술 스택을 쓰는가 | `company/tech-stack.md` |
| Role별 책임/권한/핸드오프 | `roles/*.md` |
| Agent가 어떤 도구·메모리로 동작하는가 | `agents/*.yaml` |
| 반복 절차(PRD 작성, 코드 리뷰 등) | `skills/*.md` |
| 언제 무엇을 승인/에스컬레이션하는가 | `workflows/*.md` |
| Feature/BugFix/Release가 그래프로 어떻게 도는가 | `langgraph/*.md` |
| 과거 결정/교훈을 어디서 찾는가 | `memory/*/README.md` |
| PRD/Architecture/API/Task/ADR을 어떻게 쓰는가 | `docs/*-template.md` |

## Cursor에서 쓰기

새 프로젝트에 스캐폴드한 뒤:

```text
당신은 {{PRODUCT_NAME}} Company OS의 Architect다.
company/, roles/, workflows/를 읽고 추측하지 마라.
지금은 create-feature의 Design 단계만 수행한다.
```

## 실습 산출물 안내

실제 실행 로그, Review dump 등 산출물은 Kit에 포함하지 않습니다. 스캐폴드 후 각 프로젝트의 `memory/`, `projects/<slug>/`에 쌓아가세요.
