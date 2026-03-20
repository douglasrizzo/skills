---
name: open-pr
description: >-
  Opens a pull request using the GitHub CLI. Reads the project's pull request template
  from .github/, incorporates optional user-provided context, generates a title and
  body, confirms with the user, and runs gh pr create. Use when the user asks to open,
  create, or submit a PR or pull request.
---

# Open PR

## 1. Gather context

- Accept any context the user provides: ticket number, feature summary, breaking changes, reviewers, labels, target branch.
- Confirm the current branch with `git branch --show-current`; warn if it is main/master.
- Run `git log <base>..HEAD --oneline` to see which commits will be included (default base: main or master; use the repo default if different).
- Run `git diff <base>..HEAD --stat` to understand what changed.

## 2. Find the template

Search in order:

1. `.github/pull_request_template.md`
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `.github/pull_request_template/` directory — if multiple templates exist, ask the user which to use.

If no template is found, fall back to a minimal structure: **Summary**, **Changes**, **Test plan**.

## 3. Draft title and body

- **Title:** concise (≤ 72 characters), imperative mood (e.g. "Add cosine LR scheduler with warmup").
- **Body:** fill every section of the template using the commit log and diff as the source of truth. Incorporate user-provided context. Do not invent behavior that is not in the diff.
- Mark any sections the user should complete manually (e.g. screenshots, deployment notes, migration steps) with a `<!-- TODO -->` comment.

## 4. Confirm

- Show the draft title and body to the user.
- Ask for corrections before opening.

## 5. Open

- Run:
  ```
  gh pr create --title "<title>" --body "<body>"
  ```
  Append `--reviewer`, `--label`, `--base`, `--draft`, or `--assignee @me` if the user provided them or wants to self-assign.
- Return the PR URL.
