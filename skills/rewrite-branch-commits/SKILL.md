---
name: rewrite-branch-commits
description: >-
  Rewrites a branch's commit history from scratch: soft-resets all commits back to the
  merge base with the target branch, then re-commits the combined changes as clean atomic
  commits using the commit skill. Use when a feature branch has accumulated noisy,
  redundant, or partially-undone commits that need to be cleaned up before merging.
---

# Git: rewrite branch commits

## Goal

Collapse all commits on the current branch (since it diverged from the target branch)
into a clean set of atomic commits, without losing any net changes.

## When to use

- A long-running branch has accumulated many small, noisy, or contradictory commits.
- Some commits partially undo or re-do earlier commits.
- You want a coherent commit history before opening or merging a PR.

## Workflow

### 1. Confirm scope

Identify the **target branch** (the branch this one will eventually merge into):
- Default: `main` or `master` — whichever exists locally.
- If the user specifies a different base (e.g., `develop`), use that.

Find the merge base:

```bash
git merge-base HEAD <target-branch>
```

List all commits that will be rewritten so the user can confirm:

```bash
git log --oneline <merge-base>..HEAD
```

If there is only **one commit**, there is nothing to rewrite — tell the user and stop.

**Ask the user to confirm** before proceeding, because this is a destructive operation
that rewrites history. Show them the commit count and the merge-base SHA.

### 2. Check for unpushed vs pushed commits

```bash
git status -sb
git log --oneline origin/<current-branch>..HEAD 2>/dev/null || true
```

If any of the commits to be rewritten have already been **pushed to the remote**, warn
the user that they will need to force-push after rewriting. Do not force-push yourself
unless the user explicitly instructs you to.

### 3. Soft reset to merge base

```bash
git reset --soft <merge-base-sha>
```

This preserves all changes in the index (staged). Verify:

```bash
git status
git diff --stat HEAD
```

The full net diff of the branch is now staged and ready to be re-committed.

### 4. Re-commit using the commit skill

Follow the **commit** skill exactly from step 1 onward:

- Run `git status` and `git diff --cached` to survey the staged changes.
- Group related changes into logical, atomic commits.
- For each group: run pre-commit (if available), stage explicitly, write a conventional
  commit message, and verify with `git status`.

Do **not** produce a single mega-commit unless the entire diff is one cohesive change
that cannot be split meaningfully. The goal is a clean, readable history — not just
fewer commits.

### 5. Final check

After all commits are done:

```bash
git log --oneline <target-branch>..HEAD
```

Present the new commit list to the user. If pushed commits were detected in step 2,
remind them to force-push when ready:

```bash
git push --force-with-lease
```

Do not run this command yourself unless the user explicitly asks.

## Rules

- **Never force-push** unless the user explicitly instructs you to.
- **Never amend commits** on `main`/`master`.
- **Never skip pre-commit hooks** — if a hook blocks a commit, fix the root cause.
- **Always confirm with the user** before executing the soft reset (step 3), since it
  rewrites history and cannot be undone without the reflog.
- If the working tree has **uncommitted changes** before starting, stop and ask the user
  to commit or stash them first — mixing in-progress work with the rewrite is risky.

## Quick reference

```bash
# Find merge base
git merge-base HEAD main

# Preview commits to be rewritten
git log --oneline <merge-base>..HEAD

# Soft reset (preserves all changes staged)
git reset --soft <merge-base>

# Check what is now staged
git diff --cached --stat

# Force-push after rewrite (only when user asks)
git push --force-with-lease
```
