---
name: create-jira-ticket
description: >-
  Drafts a Jira-style ticket (description + acceptance criteria) by reading the current
  Git branch’s commits and diff against a base branch, written as a short “quest” narrative.
  Use when the user wants to backfill a ticket from implemented work, document what a
  branch delivered, or produce copy for Jira/Linear after the fact.
---

# Create Jira ticket (from branch contents)

## When to use

The user has (or will have) work on a branch and wants **retroactive** ticket text: a **Description** that reads like a **game quest briefing**, plus **Acceptance criteria** grounded in what the branch actually contains.

## 1. Gather Git facts

Run from the repository root (or ask the user for the repo path):

1. **Current branch:** `git branch --show-current`
2. **Base branch:** default `main`, then `master`, or the user’s named base (e.g. `develop`).
3. **Scope of work:**  
   - `git log <base>..HEAD --oneline`  
   - `git diff <base>..HEAD --stat`  
   - Optionally `git diff <base>..HEAD --name-only` for a concise file list.
4. If the branch is **not** ahead of base (empty range), say so and either use `git log -n 20 --oneline` on the branch only or ask the user which commits count.

**Rules:** Do not invent features, files, or behavior that do not appear in the log/diff. If the diff is huge, summarize by **theme** (areas touched) and call out **high-signal** paths.

## 2. Propose a short title (Summary)

One line, **imperative**, suitable for Jira **Summary** (roughly ≤ 80 characters). Derive it from the dominant change (e.g. “Add training-only OHEM with Hydra knobs”), not from branch name alone unless the name is clearly the product of record.

## 3. Write the Description (“quest” style)

Use **two paragraphs** in this order:

### Paragraph 1 — Background / situation (the “quest setup”)

- **Tone:** Short, neutral, in-world enough to feel like a quest log **without** RPG fluff or jokes unless the user asks.
- **Content:** Why this work exists or what gap it addresses, inferred only from commits/diff (e.g. new capability, bug class fixed, tooling added). One tight paragraph (about 3–6 sentences max).

### Paragraph 2 — The objective (what “the party” must do)

- **Opening:** Use a variant of obligation language, rotating or picking the best fit:
  - “We should …”
  - “We must …”
  - “We need to …”
  - “We will …” (only if the branch clearly completes the work and the ticket documents done scope)
- **Body:** State **what** will be done, always in the future tense, regardless of whether the work was already completed.

**Do not** use bullet lists in the Description unless the user asks; keep it as **two paragraphs**.

## 4. Acceptance criteria

After the Description, add a section titled **Acceptance criteria** (or paste into Jira’s AC field).

- **Format:** One line **or** a **small** bullet list (2–5 items), each **testable** and aligned with the diff.
- **Pick patterns** that match what the branch actually delivers, for example:
  - “A merged PR containing the changes described above.”
  - “Implementation pushed to branch `<current-branch>` and reviewed.”
  - “Training pipeline supports `<feature>` (config flag / docs updated as in repo).”
  - “Automated tests added or updated for `<area>` (see `tests/…`).”
  - “A Notion / Confluence doc linked in the ticket with `<analysis|runbook|results>`.”
- Avoid vague AC (“works fine”, “tested”) unless the user supplies specifics.

## 5. Output shape (copy-paste ready)

Deliver to the user in this order:

1. **Summary** (one line)
2. **Description** (two paragraphs as above)
3. **Acceptance criteria** (one-liner or bullets)

Optionally add a **Notes for Jira** line: suggested **Issue type**, **Component**, or **Epic** only if the user provided them—do not guess organizational metadata.

## 6. Clarify when needed

Ask only if blocking:

- Which **base** branch to diff against.
- Whether the ticket should describe work as **already done** vs **to be verified after merge**.
- If multiple unrelated concerns appear in one branch, whether to **split** into more than one ticket narrative.
