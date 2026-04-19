---
name: change-verification
description: "Use for code-change verification: diff review, smoke tests, regression checks, and pre-merge confidence on modified code. Trigger on prompts like 'check my changes', 'review this diff', 'verify this fix', or any request to validate recent edits instead of implementing new code."
---

# Change Verification

Verify changed code with high signal, low waste. Start from actual diff, run smallest checks that can prove or disprove safety, then report findings and remaining risk.

## Workflow

1. Inspect worktree first with `git status` and relevant diff.
2. Read changed files and nearby tests before choosing commands.
3. Infer blast radius: docs-only, local behavior, shared abstraction, or public API.
4. Run smallest useful validation first; widen only if risk is broader.
5. Report findings first, then commands run and residual risk.

## Rules

- Never guess what changed. Read diff first.
- Ignore unrelated dirty files unless they affect verification.
- For review requests, prioritize bugs, regressions, and missing tests over summary.
- If nothing fails, say `No findings.` and still note untested risk.
- Do not modify code during pure verification unless user asked for fixes too.

## Validation Ladder

Choose lowest rung that gives real confidence.

- Inspect only: docs, comments, tiny non-executable changes.
- Targeted checks: default for most edits. Prefer touched tests, path-scoped lint, narrow type checks.
- Broad checks: use for shared abstractions, config, public API, or prompt/cache/judge/provider flow.

## IntentGuard Notes

Keep normal work focused on runtime package unless user asks otherwise.

- Main code: `intentguard/`
- Main tests: `tests/`
- Usually out of scope: `validation/`, `ai_research/`

High-risk changes:

- Public API surface: `IntentGuard`, `IntentGuardOptions`
- Runtime flow across prompt factory, cache, inference provider, and judge
- `Judge` uses strict majority, so ties must evaluate false
- Cache keys and cache versioning must stay compatible

Useful commands when scope fits:

```bash
poetry run ruff check <changed-paths>
poetry run ruff format --check <changed-paths>
poetry run mypy intentguard
poetry run python -m unittest discover tests
make test
```

## Reporting

Keep response short, concrete, evidence-based.

For review tasks, use:

```markdown
Findings:
1. [severity] `path:line` - issue and impact

Open Questions:
1. ...

Verification:
1. `command` - result

Residual Risk:
1. ...
```

If no issues found:

```markdown
No findings.

Verification:
1. `command` - result

Residual Risk:
1. ...
```
