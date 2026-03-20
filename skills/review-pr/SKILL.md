---
name: review-pr
description: >-
  Reviews an open pull request: fetches the diff and description via the GitHub CLI,
  evaluates correctness, test coverage, style, DRY, and design patterns, and presents
  structured findings. Optionally posts comments or a review via gh. Use when the user
  asks to review a PR or wants feedback on a pull request.
---

# Review PR

## 1. Fetch PR

- Accept a PR number or URL from the user.
- Run `gh pr view <number> --json title,body,baseRefName,headRefName,author,state` to read the description and metadata.
- Run `gh pr diff <number>` to get the full diff.
- Run `gh pr checks <number>` to see CI status; note any failing checks upfront.

## 2. Understand intent

- Read the PR title and description to understand what the author intended.
- If the description is absent or vague, flag this — a PR without context is a review risk in itself.
- Check that the diff matches the stated intent: flag scope creep or unrelated changes.

## 3. Evaluate

Work through each lens and collect findings with file and line references:

### Correctness
- Logic errors, wrong assumptions about input ranges or types, off-by-one errors.
- Missing error handling at system boundaries (user input, external APIs, file I/O).
- Mutation of shared state, unintended side effects.

### Tests
- Are new behaviors covered by tests?
- Are changed behaviors (including call signatures) reflected in updated tests?
- Are tests fast and deterministic? Consult **implement-tests** for ML-specific notes (seeds, shape assertions, single-batch overfit, no full training loop tests).

### Design and patterns
- Consult **design-patterns-ml**: apply the reactive smell table to code introduced by this PR.
- Flag DRY violations the PR introduces (not pre-existing ones, unless they directly interact with the new code).
- Flag non-canonical Python idioms (consult **review-code** for examples).

### Engineering standards
- Apply **python-engineering-standards**: module organization, naming, single responsibility, thin entrypoints.
- Note but do not block on pre-existing violations outside the diff.

### Security
- Injection risks at new input boundaries.
- Credentials, tokens, or secrets in code or logs.
- Unsafe deserialization.

## 4. Summarize findings

Organize findings into three tiers:

- **Must fix** — correctness errors, security issues, missing tests for new behavior.
- **Should fix** — design problems, DRY violations, non-canonical idioms.
- **Consider** — minor style, naming suggestions, optional improvements.

Present the summary to the user before posting anything.

## 5. Post review (if requested)

- General review body: `gh pr review <number> --comment --body "<summary>"`
- To request changes: `gh pr review <number> --request-changes --body "<summary>"`
- To approve: `gh pr review <number> --approve --body "<summary>"`
- For inline comments on specific lines, use `gh api` with the pulls review comments endpoint.

Always confirm the intended action (approve / request changes / comment only) before posting.
