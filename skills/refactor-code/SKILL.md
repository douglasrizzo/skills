---
name: refactor-code
description: >-
  Refactors named functions, classes, or modules using solid structure and design
  practices: analyzes code, chooses patterns, plans with the user, implements, formats
  and lints touched files, and reviews the final structure. Use when the user asks to
  refactor, restructure, simplify, or extract code without changing external behavior.
---

# Refactor code

## Principles (apply with global + project rules)

- Prefer **composition**, **clear module boundaries**, **small functions**, and **single responsibility**.
- Preserve **behavior** unless the user agrees to semantic changes; treat refactors as behavior-preserving unless documented otherwise.
- **DRY** duplicated logic into one place; avoid speculative abstractions.

## Workflow

### 1. Scope

- List targets: files, symbols, or subsystems. Confirm **in scope / out of scope**.

### 2. Analyze

- Map **callers and callees**, shared state, and side effects (I/O, globals, mutation).
- Note **tests** that lock behavior; identify gaps before editing.
- If **smells** are present (long dispatch chains, duplicated SDK usage, god modules) or **scope is large**, read the **design-patterns-ml** skill for pattern options; stay proportional to the problem.

### 3. Plan

- Propose **end state** (module map, renamed pieces, extracted types).
- Call out **risks** (API breaks, pickling, serialization, plugins).
- Present the plan; **wait for user confirmation** on large or API-changing refactors.

### 4. Implement

- Apply changes in **small steps** when helpful; keep diffs reviewable.
- Update imports and re-exports; run **formatter** on touched files.

### 5. Verify

- Run **linter/type checker**; fix new issues from the refactor. If the project defines no Ruff or ty settings, use the user-level defaults at `~/.config/ruff/ruff.toml` and `~/.config/ty/ty.toml` (see **python-engineering-standards**).
- Run **tests**; update tests if structure changed but behavior should stay the same.

### 6. Final pass

- Re-read the new structure: is it **concise**, **navigable**, and **consistent** with the repo?
- Summarize what moved where and any follow-ups.
