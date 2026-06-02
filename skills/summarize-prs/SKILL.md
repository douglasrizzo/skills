---
name: summarize-prs
description: >-
  Summarizes pull requests in a GitHub repository. Categorizes open PRs into:
  those requesting your review, your PRs with pending feedback to address,
  your PRs waiting for review, other PRs waiting for review, and approved
  PRs ready to merge. Use when the user asks for a PR summary, PR dashboard,
  or to see open pull requests.
---

# Summarize PRs

## 1. Determine scope

- If the user provided a repo, use it (format: `owner/repo`).
- Otherwise, detect the current repo with `gh repo view --json nameWithOwner -q .nameWithOwner`.
- If not in a repo and none was provided, ask the user.

## 2. Authenticate

- Run `gh auth status` to confirm the CLI is authenticated.
- If not authenticated, stop and ask the user to run `gh auth login`.

## 3. Fetch open PRs

Run:
```bash
gh pr list --repo <repo> --state open -L 200 \
  --json number,title,author,url,createdAt,updatedAt,headRefName,baseRefName,isDraft,reviewDecision,reviewRequests,latestReviews,mergeStateStatus
```

If the repo has many open PRs, increase `-L` or warn that the list is truncated.

## 4. Categorize

First, determine the current user's login:
```bash
gh api user -q .login
```

Group the fetched PRs into the following non-overlapping categories (process in this order so each PR appears exactly once):

### Approved and ready to merge
- `isDraft` is `false`.
- `reviewDecision` is `APPROVED`.
- Optionally note `mergeStateStatus`:
  - `CLEAN` or `HAS_HOOKS` → ready to merge
  - `BEHIND` → needs branch update
  - `BLOCKED` → blocked by failing checks or branch protection
  - `UNSTABLE` → unstable checks
- Sort by `updatedAt` (most recently updated first).

### Your PRs — changes requested
- `author.login` matches the current user.
- `reviewDecision` is `CHANGES_REQUESTED`.
- Sort by `updatedAt` (most recently updated first).

### Requesting your review
- `reviewRequests` contains a User with `login` matching the current user.
- `isDraft` is `false`.
- Sort by `createdAt` (oldest first).

### Your PRs — waiting for review
- `author.login` matches the current user.
- `isDraft` is `false`.
- `reviewDecision` is `REVIEW_REQUIRED` or `null`.
- Sort by `createdAt` (oldest first).

### Other PRs — waiting for review
- `isDraft` is `false`.
- `reviewDecision` is `REVIEW_REQUIRED` or `null`.
- Not authored by the current user.
- Not requesting review from the current user.
- Sort by `createdAt` (oldest first).

### Draft PRs
- Any remaining PRs where `isDraft` is `true`.
- Group by author (yours vs others) if helpful.
- Sort by `updatedAt` (most recently updated first).

## 5. Present summary

Format the output as markdown with clear headings. For each PR include:
- `#<number>` linked to URL (e.g., `[#123](url) *Title*`)
- Author (for PRs not authored by the user)
- Age: opened N days/hours ago (from `createdAt`)
- Branch: `headRefName → baseRefName`
- Any relevant status note (e.g., "needs branch update", "blocked by checks")

Add a one-line summary at the top with counts per category, e.g.:
> **12 open PRs:** 2 requesting your review, 1 with changes to address, 3 of yours waiting, 4 others waiting, 2 approved.

If a category has no PRs, state **None** rather than omitting the heading.

## 6. Optional follow-up actions

If the user wants to act on a specific PR, offer to:
- Open it in the browser: `gh pr view <number> --web --repo <repo>`
- Review it: delegate to **review-pr**
- Check it out locally: `gh pr checkout <number> --repo <repo>`
- Merge an approved PR: `gh pr merge <number> --repo <repo>` (confirm squash/rebase/merge strategy first)
