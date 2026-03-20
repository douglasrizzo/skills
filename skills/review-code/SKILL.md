---
name: review-code
description: >-
  Reviews existing Python code for quality and correctness: checks canonical idiom
  usage, DRY violations, module organization, naming, and design pattern opportunities.
  Makes improvements and updates affected tests. Use when the user asks to review,
  improve, clean up, simplify, or restructure code without adding new behavior.
---

# Review code

## 1. Align

- Read **project** `.cursor/rules/project-context.mdc` and/or `AGENTS.md` if present.
- Global design and tooling expectations are in the **python-engineering-standards** rule (always-on when configured).

## 2. Read and understand

- Read the full target code (file, class, or function as specified).
- Map callers and callees, shared state, and side effects (I/O, globals, mutation).
- Note tests that lock the current behavior before touching anything.

## 3. Evaluate

Work through each lens and collect findings before writing any code:

- **Canonical idioms:** flag non-canonical implementations and name the preferred modern alternative (e.g. dataclass over manual `__init__`, `Enum` over bare string constants, `pathlib` over `os.path`, structural pattern matching over long `if/elif` chains where it improves clarity).
- **DRY:** identify logic duplicated within the target code or elsewhere in the repo; plan to consolidate.
- **Module organization:** are symbols in the right modules? Flag anything that belongs elsewhere or should be extracted to a new module per **python-engineering-standards**.
- **Design patterns:** consult the **design-patterns-ml** skill. Apply the reactive smell table to what you see; apply the proactive table only if extensibility is clearly needed. Make an explicit decision — chosen pattern with brief justification, or "no pattern warranted."
- **Naming and size:** names that repeat module or type context, functions doing more than one thing, classes mixing unrelated responsibilities.

## 4. Plan and confirm

- Present findings as a prioritized list: what you will change and what you will leave alone and why.
- For changes that affect public API, module structure, or call signatures, **wait for user confirmation** before proceeding.

## 5. Implement

- Apply changes in small, reviewable steps.
- Update imports and re-exports after any moves.
- Run the **formatter** on all touched files.

## 6. Update tests

- For any behavior or call signature that changed, update existing tests to match.
- If tests are absent for the reviewed code, note this as a follow-up rather than adding tests silently — use **implement-tests** if the user asks.

## 7. Validate

- Run **linter/type checker**; fix new issues introduced by your changes. Fall back to user-level configs (`~/.config/ruff/ruff.toml`, `~/.config/ty/ty.toml`) if no project config exists.
- Run **tests**; all pre-existing tests must still pass.

## 8. Close

- Summarize what changed, what was left alone and why, and any recommended follow-ups.
