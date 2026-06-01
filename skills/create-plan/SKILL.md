---
name: create-plan
description: >-
  Use a local .plans directory to capture a multi-phase development plan: creates
  00-master-plan.md with a high-level overview, numbered individual plan files, and
  99-to-do.md with checklists. Use when the user wants to plan a feature, project, or
  initiative before implementing it.
---

# Create plan

## Goal

Capture a structured, multi-phase plan inside the project as `.plans/` files that
`next-phase` and `review-plans` can operate on. Keep plans small enough to be
actionable and large enough to be unambiguous.

## Workflow

### 0. Determine write capability

Before starting, check whether you can write files. If you are in Plan mode or otherwise
read-only, you will not be able to create `.plans/` files. In that case:

- Instead of writing files, present the complete plan as text output — all sections, all
  phase files, the master plan, and the to-do list — formatted as they would appear on disk.
- Append this note at the end:

  > This plan was generated in read-only mode. To materialize these files, switch to Build
  > mode and re-run this skill with the prompt "Materialize the plan from the text above
  > into `.plans/` files."

If write access is available (Build mode), proceed normally with file creation below.

### 1. Understand the work

Ask targeted questions until you can write a plan that is concrete enough to implement
without guesswork:

- What is the end goal?
- What phases or milestones does the user have in mind?
- Are there constraints (dependencies, deadlines, tech choices)?
- What is out of scope?

Do not start writing files until you have enough clarity.

### 2. Set up the `.plans` directory

```bash
mkdir -p .plans/done
```

If the project is a git repository, ensure `.plans/` is ignored:

```bash
# check if already ignored
git check-ignore -q .plans 2>/dev/null || echo ".plans/" >> .gitignore
```

### 3. Write `00-master-plan.md`

Create `.plans/00-master-plan.md` with this structure:

```markdown
# Master plan: <project or feature name>

## Goal

<One-paragraph description of the end state and why it matters.>

## Phases

| # | Name | Status |
|---|------|--------|
| 01 | <Phase name> | TODO |
| 02 | <Phase name> | TODO |
| …  | …            | …    |

## Out of scope

- <item>

## Constraints

- <item>
```

Status values: `TODO`, `IN PROGRESS`, `DONE`.

### 4. Write individual plan files

For each phase, create `.plans/<NN>-<kebab-name>.md`:

```markdown
# Phase <NN>: <Phase name>

## Goal

<What this phase produces — one short paragraph.>

## Steps

1. <Concrete step>
2. <Concrete step>
…

## Acceptance criteria

- [ ] <Verifiable outcome>
- [ ] <Verifiable outcome>

## Dependencies

- Requires phase <NN> to be complete (if any)
- External: <library, API, etc.>

## Notes

<Design decisions, risks, open questions.>
```

Number files zero-padded to two digits: `01`, `02`, … `98`.
Reserve `00` for the master plan and `99` for the to-do list.

### 5. Write `99-to-do.md`

Create `.plans/99-to-do.md` as the single place `next-phase` and `review-plans`
consult to track progress:

```markdown
# To-do

## Backlog

- [ ] **Phase 01 – <name>**: <one-line summary> → `.plans/01-<kebab>.md`
- [ ] **Phase 02 – <name>**: <one-line summary> → `.plans/02-<kebab>.md`

## Done

<!-- Completed phases are moved here by next-phase or review-plans -->
```

### 6. Present the plan

Show the user a summary of what was created. Wait for their approval or corrections
before finishing. If they request changes, update the affected files in place.

## Rules

- **Do not start implementing** — this skill only plans.
- **Reserve file numbers:** `00` = master plan, `99` = to-do, `01`–`98` = phases.
- **Keep individual plans implementation-agnostic** where possible — record the *what*
  and *why*, leave the *how* to the implementer.
- **`.plans/done/`** is where completed phase files live after `next-phase` finishes
  them. Never delete phase files; only move them.
