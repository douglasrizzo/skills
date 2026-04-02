---
name: git-new-branch
description: >-
  Creates a Git branch with a conventional prefix (feat/, fix/, chore/, etc.), optionally
  commits and pushes staged or unstaged work. Use when the user asks for a new branch,
  wants to start work on a feature branch, or wants branch + commit + push in one go.
---

# Git: new branch (and optional commit/push)

## Branch name prefixes

Use a **type prefix + short slug** (lowercase, hyphenated). Pick the prefix from intent:

| Prefix | Use when |
|--------|----------|
| **feat/** | New user-facing capability or behavior |
| **fix/** | Bug fix |
| **chore/** | Maintenance, tooling, deps, configs without product behavior change |
| **docs/** | Documentation only |
| **refactor/** | Internal restructuring, no intended behavior change |
| **test/** | Tests only |
| **ci/** | CI/CD, pipelines |
| **perf/** | Performance improvements |
| **style/** | Formatting, lint-only, no logic change |

**Examples:** `feat/ohem-training`, `fix/dataloader-drop-last`, `chore/ruff-0.15`.

If the user gives no prefix, infer from their wording (feature → `feat/`, bug → `fix/`, deps/config → `chore/`). If unclear, ask once.

**Slug rules:** ASCII letters, numbers, hyphens; no spaces; avoid trailing punctuation.

## Two workflows (confirm implicitly from the user message)

### A) New branch only

User wants to **branch off the current HEAD** with **no commit and no push**.

1. `git status -sb` — note current branch and cleanliness (informational).
2. `git checkout -b <prefix>/<slug>` (or `git switch -c`).
3. Tell them they are on the new branch; they can commit when ready.

### B) New branch + commit + push

User wants a **new branch** and to **record and publish** work (staged and/or unstaged).

1. `git status` — see staged vs unstaged.
2. **Staging scope** (infer from wording; if ambiguous, ask once):
   - **”Commit what I staged” / “staged only”** → `git diff --cached --stat`, then commit **without** `git add -A` of unstaged files.
   - **”Commit everything” / “all changes” / “including unstaged”** → `git add` only the paths relevant to the task (prefer explicit paths from context); avoid sweeping unrelated files. If the user explicitly wants the whole repo: `git add -A` with a warning if unrelated changes appear.
3. **Branch, commit, and push:** create the branch from the current tip, then follow the **commit** skill for pre-commit hooks, staging, and commit message format. Typical sequence:
   - `git switch -c <branch>` → stage → commit per **commit** skill → `git push -u origin <branch>`.

If there is **nothing to commit** (clean tree), still create the branch and push only if they asked to push; otherwise explain there was nothing to commit.

## Safety checks

- Do **not** force-push unless the user explicitly asks.
- If on **main/master** with uncommitted work and they want a new branch, branching first preserves work on the new branch (same as `switch -c`).
- If **multiple remotes**, default to `origin` unless they specify.

## Quick reference commands

```bash
# Branch only
git switch -c feat/my-feature

# Staged-only commit then push
git commit -m "feat: short description"
git push -u origin feat/my-feature

# Include unstaged tracked files (review status first)
git add -u
git add path/to/new/file
git commit -m "feat: short description"
git push -u origin feat/my-feature
```
