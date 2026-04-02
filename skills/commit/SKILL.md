---
name: commit
description: >-
  Commits changes atomically: groups related files into logical commits, runs pre-commit
  on each group before committing (if pre-commit is available), and writes conventional
  commit messages. Use when the user asks to commit changes, stage and commit, or wants
  clean atomic commits from a working tree.
---

# Git: atomic commits with pre-commit

## Goal

Produce one or more focused, atomic commits that each represent a single logical change.
Never bundle unrelated changes into one commit. Never skip pre-commit hooks.

## Workflow

### 1. Survey the working tree

Run `git status` and `git diff` (staged + unstaged) to understand what has changed.
Identify logical groups — for example:

- New feature files + their tests → one commit
- A documentation update → separate commit
- A dependency or config change → separate commit
- An independent bug fix → separate commit

If the user has already described the groupings, follow them. If the scope is unclear,
make a judgment call based on the diff; ask only if two or more plausible groupings
exist that would materially change the commit history.

### 2. Check for pre-commit

```bash
# pre-commit is available if any of these exist:
test -f .pre-commit-config.yaml && (command -v pre-commit || uv run pre-commit --version)
```

If pre-commit **is available**, run it on each group's files **before** staging and
committing that group (see step 3). Use `uv run pre-commit` if `pre-commit` is not on
PATH directly.

If pre-commit is **not available**, skip it and proceed directly to staging.

### 3. For each logical group

Repeat this sequence for every group identified in step 1:

**a. Run pre-commit (if available)**

```bash
uv run pre-commit run --files <file1> <file2> ...
```

- If pre-commit modifies files (exit code 1 + "files were modified by this hook"),
  run it **a second time** on the same files to confirm they are now clean before
  proceeding. A second failure is a real error — stop and report it.
- If pre-commit fails for a reason other than auto-fixable formatting, diagnose and
  fix the issue before committing.

**b. Stage the group**

Prefer explicit paths over `git add -A` to avoid sweeping in unrelated changes:

```bash
git add src/foo/bar.py src/foo/baz.py tests/test_bar.py
```

**c. Commit**

Write a conventional commit message (imperative subject, ≤ 72 chars, body if needed):

```
<type>(<scope>): <short description>

<optional body explaining the why, not the what>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`, `style`.
Scope is optional; use it when the change is clearly scoped to one module or area.

Always pass the message via heredoc to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add token refresh on 401

Automatically retries requests after refreshing the access token,
eliminating the need for callers to handle 401 responses manually.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

**d. Verify**

After each commit, confirm with `git status` that only the intended files were included.

### 4. Final check

After all groups are committed, run `git log --oneline -5` and present the resulting
commit list to the user.

## Rules

- **Never use `--no-verify`** — if a hook blocks a commit, fix the root cause.
- **Never amend a previous commit** unless the user explicitly asks.
- **Never force-push**.
- **Do not push** unless the user explicitly asks.
- **Untracked files**: stage them only if they are clearly part of a logical group
  being committed. Ask about untracked files that don't fit any group.
- **Empty commit**: if there is nothing to commit after filtering, tell the user rather
  than creating an empty commit.

## Pre-commit exit code reference

| Exit code | Meaning |
|-----------|---------|
| 0 | All hooks passed, no files modified |
| 1 | Hooks ran; some files were modified (auto-fix) or a hook failed |

A hook that auto-fixes files will exit 1 on the first run; re-run on the same files
to confirm clean. A hook that cannot auto-fix (e.g. mypy, failing tests) also exits 1
but will not modify files — these require manual intervention.
