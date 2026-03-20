---
name: bootstrap-python-project
description: >-
  Scaffolds a new Python repository from user choices, with sensible defaults: second-latest
  stable Python, uv, Ruff, ty (Astral type checker), Google-style docstrings, src layout,
  pytest. Fetches Python.gitignore from GitHub, initializes the toolchain, writes README and
  .cursor/rules/project-context.mdc. Use when the user starts a new project, greenfield repo,
  or asks to scaffold or bootstrap a Python codebase.
---

# Bootstrap Python project

## Sensible defaults (use unless the user overrides)

| Topic | Default |
|-------|---------|
| **Python** | **Second-latest** stable release (e.g. if newest is 3.14, use 3.13). Resolve with `uv python list` / official releases; set `requires-python` accordingly. |
| **Package manager** | **uv** |
| **Layout** | **`src/<package>/`** package layout |
| **Linter / formatter** | **Ruff** |
| **Type checker** | **ty** (add to dev deps; configure `[tool.ty]` or `ty.toml` in the project) |
| **Docstrings** | **Google** (`[tool.ruff.lint.pydocstyle] convention = "google"` in project `pyproject.toml`) |
| **Tests** | **pytest** |

Do **not** re-ask for each default unless the user wants something different. Confirm **project root** and **package/import name** if missing.

## Optional questionnaire

Ask only for what is still unknown after applying defaults:

1. **Package name** (import name) and human-readable **project name**.
2. **Python version** — only if the user rejects second-latest.
3. **Layout** — only if they insist on flat scripts at repo root.
4. **Extras:** pre-commit, GitHub Actions, license, CLI entry point, etc.

## Create structure

1. Create directories: `src/<package>/`, `tests/` (if tests requested—default yes).
2. **`.gitignore`:** e.g.  
   `curl -fsSL -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore`  
   Append tool-specific lines (`.venv/`, `.ruff_cache/`, `.ty_cache/` if applicable) if missing.
3. **Initialize uv:** `uv init` with appropriate flags; set `requires-python`, `[project]`, `[dependency-groups] dev` with `ruff`, `ty`, `pytest`, `pre-commit` (if requested).
4. **Ruff in the project:** Add `[tool.ruff]` / `[tool.ruff.lint]` to **project** `pyproject.toml` with **Google** pydocstyle and the same line length / rule philosophy you use elsewhere (you may take inspiration from the user’s `~/.config/ruff/ruff.toml`, but **override** pydocstyle to `google` for greenfield). If the user keeps a shared user-level Ruff file, it is Numpy-oriented for legacy repos—new projects should still set Google in the project file so it takes precedence.
5. **ty in the project:** Add `[tool.ty]` with sensible rules, or `ty.toml` beside `pyproject.toml`. If you need a baseline and the project has nothing yet, you may align with `~/.config/ty/ty.toml` and extend in-repo.
6. **Tooling config:** pytest (`[tool.pytest.ini_options]` or `pytest.ini`), pre-commit, CI per user request. If pre-commit is added: `pre-commit autoupdate` then `pre-commit install` (invoke via `uv run` if needed).
7. **`README.md`:** Install (`uv sync`), run tests, run `ruff check` / `ruff format`, run `ty`, project purpose placeholder.
8. **Agent context:** `.cursor/rules/project-context.mdc` with `alwaysApply: true`: what the project is, layout, commands for sync/lint/typecheck/tests, note that global **python-engineering-standards** applies.

If the user plans **plugins**, multiple backends, or multi-entry CLIs from day one, they may consult the **design-patterns-ml** skill for registries and boundaries—keep the scaffold simple unless they ask for that complexity.

## User-level Astral config (optional reference)

When explaining defaults, you may mention that the user can keep personal tool defaults under XDG paths: `~/.config/uv/uv.toml`, `~/.config/ruff/ruff.toml`, `~/.config/ty/ty.toml` (project files override these).

## Finish

- Run `uv sync` (and one smoke command: `uv run ruff check`, `uv run ty`, or `uv run pytest`) to verify.
- List created paths and follow-ups.
