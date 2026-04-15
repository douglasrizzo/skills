---
name: review-plans
description: >-
  Reviews the master plan against the current repository state: removes or summarizes
  completed phases from 00-master-plan.md, prunes 99-to-do.md, and updates remaining
  phase files to reflect what has actually changed. Use when the plans have drifted
  from reality or before starting a new phase.
---

# Review plans

## Goal

Bring `.plans/` back into sync with the actual state of the repository. Plans drift
when work is done outside `next-phase`, when scope changes, or when time passes.
This skill reads the code and git history to ground every update in fact.

## Workflow

### 1. Check that `.plans/` exists

If `.plans/` does not exist, tell the user and stop. Suggest running `/create-plan`.

### 2. Read all plan files

```bash
cat .plans/00-master-plan.md
cat .plans/99-to-do.md
ls .plans/          # remaining phase files
ls .plans/done/     # completed phase files
```

Also read the recent git log to understand what has been implemented:

```bash
git log --oneline -30
```

### 3. Reconcile `00-master-plan.md`

For each phase row in the master plan table:

- If the phase file is in `.plans/done/` → confirm status is `DONE`; update if not.
- If the phase file is in `.plans/` and the to-do item is checked (`- [x]`) → move
  the file to `.plans/done/` and mark the phase `DONE`.
- If git history shows the work was clearly done but plans were not updated → mark
  the phase `DONE`, move the file if present.
- If the phase's scope has changed based on current code or recent discussion →
  update the description in the master plan table to reflect the current intent.

Remove phase rows that are no longer relevant (cancelled work, merged into another
phase). Add a brief **Changelog** section at the bottom of `00-master-plan.md` when
you remove rows so there is a record.

### 4. Reconcile `99-to-do.md`

- Remove or check off items whose phase files have been moved to `.plans/done/`.
- Remove items for phases that were cancelled.
- Update one-line summaries if the phase's goal has shifted.
- Ensure the order of Backlog items reflects actual priority (consult the master plan
  phase table for order).

Do not reorder items without a clear reason — ask the user if priority is unclear.

### 5. Update remaining phase files

For each `.plans/<NN>-*.md` still in the backlog:

- Read the file.
- Read relevant current source files to check whether any steps are already partially
  done, whether acceptance criteria are already met, or whether the approach is
  outdated.
- Update the phase file to reflect current reality: mark partial steps done, revise
  outdated approaches, add new constraints discovered during implementation.
- If the phase is now fully met by existing code, treat it as done (step 3 above).

Be conservative: only update what you can verify from the code or git history. Flag
ambiguities to the user rather than guessing.

### 6. Present a diff summary

Before writing any files, show the user a summary of all proposed changes:

- Phases being marked DONE
- Phase files being moved to `.plans/done/`
- Rows being removed from the master plan
- To-do items being checked off or removed
- Phase files being updated

Wait for the user to approve before applying changes.

### 7. Apply changes and commit

Apply the approved changes, then follow the **commit** skill to commit the plan
updates:

```
chore(plans): reconcile plans with current repo state
```

Include a brief body listing which phases were closed and what was updated.

## Rules

- **Ground every change in evidence** (code, git log, or user statement). Do not
  mark a phase done based on plan files alone — verify in the repo.
- **Never delete phase files** — move them to `.plans/done/` or keep them in
  `.plans/` if still relevant.
- **Never reorder phases** without the user's explicit approval.
- **Do not implement** anything during this skill — if you spot missing work, note
  it in the phase file and tell the user. Use `/next-phase` to implement.
- **Ask before removing** a phase row from the master plan — removal is lossy.
