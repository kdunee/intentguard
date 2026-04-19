---
name: prepare-release
description: "Use for release preparation: version bumping, release commit creation, release tag creation, and post-release dev bump. Trigger when user asks to cut a release, prepare a release, bump package version, make release commit/tag, or follow existing release convention in this repo."
---

# Prepare Release

Prepare releases with minimal context and exact repository conventions.

## Goal

Produce release state that matches existing history:

- release commit message: `Release vX.Y.Z`
- release tag: lightweight tag `vX.Y.Z` on release commit
- follow-up dev commit message: `Bump to vX.Y.(Z+1)-dev`

Current repo signals:

- package version lives in `pyproject.toml`
- CI publishes on GitHub `release` event, not on tag push alone
- standard validation command is `make test`

## Context Discipline

Stay lean. Start with only these sources:

1. `pyproject.toml`
2. `Makefile`
3. `.github/workflows/main.yml`
4. recent `git log --oneline`
5. recent `git tag`

Do not read broad docs or unrelated code unless release task specifically needs it.

## Workflow

1. Inspect current version in `pyproject.toml`.
2. Inspect recent release history if versioning intent is not obvious.
3. Infer target release version:
   - if current version is `X.Y.Z-dev`, release version is usually `X.Y.Z`
   - if user names a version, use it
   - if neither is clear, ask one short question
4. Update only release metadata needed for release. In this repo, that is normally `pyproject.toml` only.
5. Run `make test` before any commit.
6. If user asked to commit, create commit with exact message `Release vX.Y.Z`.
7. If user asked to tag, create lightweight tag `vX.Y.Z` pointing at release commit.
8. If user asked for full release prep, bump `pyproject.toml` to next dev version `X.Y.(Z+1)-dev` unless user requested different next version.
9. Run `make test` again if post-release bump changed anything material. If only version string changed, reuse earlier confidence unless user asked for rerun.
10. If user asked to commit post-release bump, create commit with exact message `Bump to vX.Y.(Z+1)-dev`.

## Rules

- Preserve existing convention exactly. Do not invent `chore(release): ...` messages.
- Use `v` prefix in both commit messages and tag names.
- Prefer smallest correct change. Do not edit unrelated files.
- Never push, publish, open GitHub release, or force anything unless user explicitly asked.
- Never amend prior release commits unless user explicitly asked.
- If worktree has unrelated changes, avoid touching them and continue if safe.

## Version Math

Default next dev version is patch increment after release.

Examples:

- `2.1.1-dev` -> release `2.1.1` -> next dev `2.1.2-dev`
- `3.0.0-dev` -> release `3.0.0` -> next dev `3.0.1-dev`

If user wants minor or major bump after release, follow user instruction.

## Commands

Use commands like these when scope fits:

```bash
make test
git commit -m "Release v2.1.1"
git tag v2.1.1
git commit -m "Bump to v2.1.2-dev"
```

## Report Back

Keep output compact. Include:

1. release version prepared
2. files changed
3. validation run status
4. commit hashes created
5. tag created or skipped
6. anything left for user, such as pushing or publishing
