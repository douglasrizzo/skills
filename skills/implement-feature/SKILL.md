---
name: implement-feature
description: >-
  Plans with the user via clarifying questions, ponders module placement, DRY, and
  design patterns, then implements a feature using project conventions (or global
  python-engineering-standards when absent), runs formatters/linters and tests if
  configured, and validates the result. Use when adding functionality, implementing
  a ticket, or extending APIs or CLIs.
---

# Implement feature

## 1. Align

- Read **project** `.cursor/rules/project-context.mdc` and/or `AGENTS.md` if present.
- Global design and tooling expectations are in the engineering standards (`AGENTS.md` / `CLAUDE.md`).

## 2. Clarify

- Ask **targeted questions** until requirements, edge cases, and acceptance criteria are clear enough to implement without guesswork. Do not start planning until you have a clear picture.

## 3. Plan

Present a short written plan covering:

- **Scope:** what the feature does and what it does not do.
- **Module placement:** for each new symbol (class, function, type alias), state which existing module it belongs in, or name a new module if nothing fits. Justify the placement.
- **DRY check:** scan existing code for behavior similar to what you are about to write. If it exists, plan to reuse or extend it; flag it explicitly.
- **Design patterns:** consult the **design-patterns-ml** skill and make an explicit decision. Use the proactive table if the task clearly warrants extensibility; use the reactive smell table if the existing context shows smells. State the chosen pattern and why, or state "no pattern needed — plain functions sufficient" if neither table applies. Do not leave this open.
- **Risks:** API breaks, serialization, data contracts, backward compatibility.

Wait for confirmation on the plan before writing code.

## 4. Implement

- Follow the agreed plan; surface deviations before making them.
- Match existing **style, types, imports, and patterns** in the repo.
- Keep the change set focused; avoid unrelated refactors.
- **Canonical idioms:** choose the single most correct and modern approach for the language. For Python projects, apply the idiomatic choices from the `## Python projects` section of the engineering standards (dataclass vs TypedDict, Enum vs string constants, pathlib, etc.). Note the choice briefly if non-obvious.

## 5. Validate

- Run the project's **formatter** on changed files if configured.
- Run **linter/type checker**; fix violations **introduced by this change**. If the repo has no Ruff/ty config in the project, fall back to user-level configs: `~/.config/ruff/ruff.toml` and `~/.config/ty/ty.toml` (`$XDG_CONFIG_HOME` if set).
- Run **tests** if the repo has them; add or update tests when behavior changes (see **implement-tests** skill).

## 6. Close

- Briefly note what changed, how to run it, and any follow-ups or manual steps.
