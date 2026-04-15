---
name: next-phase
description: >-
  Detects the next unimplemented phase in the master plan, implements it following the
  phase's plan file, then moves the plan file to .plans/done/ and updates the to-do
  list. Use when the user wants to advance the project to the next planned phase.
---

# Next phase

## Goal

Pick up the next unchecked phase from `.plans/99-to-do.md`, implement it, and record
the completion — leaving the plan in a clean state for the phase after.

## Workflow

### 1. Read the plan state

```bash
cat .plans/99-to-do.md
cat .plans/00-master-plan.md
```

Identify the **first unchecked item** (`- [ ]`) in the Backlog section of `99-to-do.md`.
If there are no unchecked items, tell the user all phases are complete and stop.

### 2. Load the phase plan

Read the phase file referenced by that to-do item (e.g. `.plans/01-setup.md`).
Understand:

- The phase goal
- The steps
- The acceptance criteria
- Any dependencies on earlier phases

If a dependency phase is not yet `DONE` in `00-master-plan.md`, warn the user and ask
whether to proceed anyway or skip to a ready phase.

### 3. Mark the phase as in progress

Update `.plans/00-master-plan.md`: change the phase row's status from `TODO` to
`IN PROGRESS`.

Update `.plans/99-to-do.md`: replace `- [ ]` with `- [~]` for the active phase to
signal it is in progress.

### 4. Implement the phase

Follow the **implement-feature** skill from step 2 (Clarify) onward:

- Present a short plan covering scope, module placement, DRY check, and any design
  patterns. Wait for the user to confirm before writing code.
- Implement the agreed plan.
- Run the project's formatter/linter on changed files.
- Run tests if they exist; add or update tests for new behavior.

Use the acceptance criteria from the phase file as the definition of done.

### 5. Commit the work

Follow the **commit** skill to produce clean atomic commits for this phase's changes.
Use the phase name in commit messages where it adds clarity.

### 6. Record completion

After the user confirms the phase is done:

**a. Move the phase file to `.plans/done/`:**

```bash
mkdir -p .plans/done
mv .plans/<NN>-<name>.md .plans/done/
```

**b. Update `00-master-plan.md`:** change the phase row's status to `DONE`.

**c. Update `99-to-do.md`:** replace `- [~]` with `- [x]` and move the line from
`## Backlog` to `## Done`.

**d. Commit the plan updates** using the **commit** skill:

```
chore(plans): mark phase <NN> done, move plan file to done/
```

### 7. Report

Tell the user:
- What was implemented.
- What the next pending phase is (if any).
- Any follow-up tasks or manual steps from the phase's Notes section.

## Rules

- **Do not skip phases** unless the user explicitly asks.
- **Do not implement without confirming the plan** — always show the scope and wait
  for approval before writing code.
- **Do not delete phase files** — move them to `.plans/done/`.
- **Stop if `.plans/` does not exist** — tell the user to run `/create-plan` first.
- If the phase file references an external dependency (API key, service, migration),
  surface it to the user before starting the implementation.
