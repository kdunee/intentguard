# AGENTS.md

IntentGuard is a **library for natural-language code assertions**. Keep changes small, composable, and focused on the runtime package unless explicitly asked otherwise.

## What matters most

- Public API surface is intentionally tiny: `IntentGuard`, `IntentGuardOptions`, `assert_code`, `test_code`, and `set_default_options`. Preserve this unless a task explicitly expands API.
- The runtime uses three replaceable collaborators:
  - `InferenceProvider` (model backend)
  - `PromptFactory` (prompt construction)
  - `JudgementCache` (result caching)
- Default wiring happens at import time in `intentguard/__init__.py`.

## Repository map (high signal only)

- `intentguard/` — production Python package.
  - `app/` — orchestration + interfaces (core control flow lives here).
  - `domain/` — pure data and judgement logic.
  - `infrastructure/` — filesystem cache + local llamafile backend + prompt template.
- `tests/` — integration-style tests using the real `IntentGuard` API.
- `validation/` — separate model-quality evaluation tooling and docs.
- `ai_research/` — dataset generation and model-training artifacts (not required for normal library runtime work).

## Core runtime flow

1. `assert_code()` delegates to `test_code()`.
2. `params` objects are converted to source snippets via `CodeObject.from_dict()`.
3. Prompt is built by the configured `PromptFactory`.
4. Cache lookup (`JudgementCache.get`) runs before inference.
5. On miss, provider runs `num_evaluations` predictions.
6. `Judge` applies majority vote and returns `Evaluation`.
7. Result is cached and optionally raised as `AssertionError` when false.

## Design constraints to preserve

- `Judge` currently implements **strict majority** (`True > False`), so ties evaluate to false.
- Cache keys include prompt + inference options + judgement options and are versioned (`v2:` prefix in FS cache).
- Llamafile backend is lazy-initialized and stores artifacts under `.intentguard/`.
- `IntentGuardOptions` controls deterministic behavior via `num_evaluations` and `temperature`.

## Practical guidance for future edits

- Prefer changing abstractions in `app/` or `domain/` before touching infrastructure details.
- Keep infrastructure side effects explicit (downloads/process startup/cache writes).
- Avoid broad refactors across `ai_research/` unless the task is explicitly research/training-related.
- Preserve type hints and dataclass-based DTOs for low-token readability and maintainability.
