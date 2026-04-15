## Python projects

_Apply when `.py` files, `pyproject.toml`, or `setup.cfg` are present._

### Tooling

- **Ruff:** A `PostToolUse` hook runs ruff automatically after every file edit in Claude Code. Do NOT run `ruff check` or `ruff format` manually — it is redundant and wastes a turn.
- **Type checker:** Fix only issues your changes introduced. If no project config exists, fall back to `~/.config/ty/ty.toml` (ty) and `~/.config/ruff/ruff.toml` (ruff).
- **Package manager:** Use `uv` for installs and environment management (`uv sync`, `uv add`, `uv run`).
- **Tests:** Use `pytest`; run via `uv run pytest` unless the project documents otherwise.

### Idiomatic Python

Prefer the idiomatic form when it reads clearly; don't force it when a plain approach is more readable (e.g. multiline loop body that wouldn't fit a comprehension).

- **Comprehensions over loops:** `[x * 2 for x in items]` not `result = []; for x in items: result.append(x * 2)` — single-line only.
- **Builtins first:** reach for `enumerate`, `zip`, `any`, `all`, `sum`, `min`, `max`, `sorted` before writing a loop.
- **Standard library before custom:** check `itertools`, `functools`, `collections`, `contextlib`, `pathlib` before writing a utility.
- **f-strings:** always use f-strings for interpolation, not `.format()` or `%`.
- **`pathlib` over `os.path`:** use `pathlib.Path` for all filesystem operations.
- **Guard clauses:** use early returns to flatten nested `if` blocks.
- **`@dataclass` / `NamedTuple` over manual `__init__`:** for data-holding classes.
- **`Enum` over string/int constants:** for any symbolic set of values.

### Type annotations

- Annotate all public function signatures and class attributes.
- Avoid `Any` unless bridging untyped external code.

For before/after examples of complex idioms, read `rules/python-examples.md`.
