---
name: find-dead-and-duplicate-code
description: >-
  Runs vulture, pylint similarities, and deepcsim on a Python project and
  returns a single filtered report of dead code and duplicate code suitable
  for refactor planning. Use when the user asks to find unused code, find
  duplicates, audit a package before cleanup, or look for refactoring
  opportunities in Python.
---

# Find dead and duplicate code

## 1. Confirm target

- Default target is `src/` under the project root, or the package named in `pyproject.toml`.
- Ask the user if the repo layout is non-standard or if they want a narrower target (a single subpackage, for example).

## 2. Run the detector

One command — the script runs vulture, pylint similarities, and deepcsim, applies noise filters, and emits a single Markdown report:

```bash
uv run ~/.agents/skills/find-dead-and-duplicate-code/find_code_smells.py <target>
```

Pass `--format json` only when piping into downstream tooling. Default Markdown is for reading.

Useful flags:

- `--min-func-lines N` — raise this if the structural-duplicates section is noisy (default 8).
- `--min-struct N` / `--min-composite N` — raise these to tighten the structural-duplicates gate (default 85 / 85).
- `--skip-dead` / `--skip-dup-text` / `--skip-dup-struct` — disable individual tools.
- `--skip-globs "tests/**,**/ui/**"` — suppress dead-code hits in paths that routinely contain framework-callback code.
- `--output PATH` — write to a file instead of stdout (useful for very large projects).

## 3. Interpret the report

- **Dead code**: the script already drops symbols in `__all__` and symbols matching the skip-globs. Anything remaining is *likely* dead, but verify callers before deletion — Streamlit callbacks, pytest fixtures, CLI entrypoints, and any symbol invoked by string (registries, dispatch tables) can escape static analysis. Use Grep across the repo before removing.
- **Textual duplicates**: highest signal. Each block shows exact `file:line` ranges on both sides and the duplicated snippet. These are usually real extract-to-utility candidates.
- **Structural duplicates**: already filtered to function length ≥ 8 lines and structural + composite ≥ 85. Even so, judge carefully — two functions with the same AST shape can be semantically unrelated (dispatch-table lookups, type-dispatched helpers). Read both sides before recommending a merge.

## 4. Propose a refactor plan

- Group findings by probable fix: **delete**, **extract helper**, **merge**, or **inline**.
- Present the plan to the user and wait for confirmation before editing.
- When unifying duplicates, delegate style decisions to the `simplify` and `review-code` skills: shared helpers go into the narrower of the two modules' dependency levels; tests for the retained site must continue to pass.

## 5. Implement

- Apply changes in small, reviewable steps.
- Re-run the script after non-trivial refactors to confirm the report shrinks and nothing new regresses.
- Run the project's tests and type checker (see `AGENTS.md` for the project's commands).

## 6. Close

- Report what was removed / consolidated, what was left alone and why, and any follow-ups (e.g. dead code that looked live and needs a runtime check, or structural duplicates that were deliberately left because the shape is coincidental).
