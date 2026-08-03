# Organization Chart

## Structure

```text
              CEO
         /     |     \
       PM   Architect  DevOps
      / \      |         |
 Backend Frontend      QA
         \     |      /
          Reviewer
              |
       Technical Writer
```

## Decision Authority

| Decision | Owner | Approver |
|----------|-------|----------|
| Product Scope | PM | CEO (strategic) |
| Architecture | Architect | CEO (high-risk) |
| Implementation | Backend / Frontend | Reviewer |
| Release Go/No-Go | QA + DevOps | CEO (prod major) |
| Incident SEV-1 | DevOps | CEO / Operator |
