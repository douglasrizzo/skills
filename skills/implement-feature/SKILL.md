---
name: implement-feature
description: >-
  Plans with the user, asks clarifying questions, implements a feature using project
  conventions (or global python-engineering-standards when absent), runs formatters/linters
  and tests if configured, and validates the result. Use when adding functionality,
  implementing a ticket, or extending APIs or CLIs.
---

# Implement feature

## 1. Align

- Read **project** `.cursor/rules/project-context.mdc` and/or `AGENTS.md` if present.
- Global design and tooling expectations are in the **python-engineering-standards** rule (always-on when configured).

## 2. Plan and clarify

- Summarize the goal and propose a **short plan** (files to touch, data flow, risks).
- Ask **targeted questions** until requirements, edge cases, and acceptance criteria are clear enough to implement without guesswork.

## 3. Implement

- Match existing **style, types, imports, and patterns** in the repo.
- Keep the change set focused; avoid unrelated refactors.
- If the project documents module boundaries, respect them.
- If the design is **non-trivial** (new extensibility points, cloud integration, or clear code smells), read the **design-patterns-ml** skill and apply it proportionally.

## 4. Validate

- Run the project’s **formatter** on changed files if configured.
- Run **linter/type checker**; fix violations **introduced by this change**. If the repo has **no** Ruff/ty (or other) config in the project, fall back to **user-level** configs: `~/.config/ruff/ruff.toml` for Ruff and `~/.config/ty/ty.toml` for ty (`$XDG_CONFIG_HOME` if set). Use Ruff/ty CLI discovery when possible; pass `--config` only when needed.
- Run **tests** if the repo has them; add or update tests when behavior changes (see **implement-tests** skill).

## 5. Close

- Briefly note what changed, how to run it, and any follow-ups or manual steps.
