---
name: implement-tests
description: >-
  Adds or extends automated tests from a feature description (new or existing). Matches
  the repository’s test layout, runner, and naming; if none exist, uses a root-level
  tests/ tree mirroring the main package structure. Use when the user asks for tests,
  pytest coverage, or test cases for a module or feature.
---

# Implement tests

## 1. Discover

- Find how tests are run: `pytest`, `unittest`, `tox`, `nox`, npm, etc. (read `pyproject.toml`, `pytest.ini`, `conftest.py`, CI workflows).
- Inspect **existing** tests: directory (`tests/`, `test/`, inline), file naming (`test_*.py`, `*_test.py`), class patterns, fixtures, markers.

## 2. Default layout (no prior tests)

- Create **`tests/`** at repo root.
- Mirror import paths: e.g. code in `src/foo/bar.py` → `tests/foo/test_bar.py` (adjust if the project uses a different documented pattern).
- Use **pytest** unless the user or repo standard says otherwise.

## 3. Write

- Cover **public** behavior: modules’ public functions, classes, and CLI boundaries the user cares about.
- Prefer **fast, deterministic** unit tests; use fixtures/mocks for I/O and time.
- Match **assertion style** and **fixtures** already present in the repo.

### ML-specific notes

- **Seeds:** Set `torch.manual_seed` / `np.random.seed` / `random.seed` at the top of each test that involves randomness, or in a shared `conftest.py` autouse fixture.
- **What to test in models:** Assert output *shape*, loss value range (finite, non-negative), and that one gradient step reduces loss on a single batch. Do **not** assert on exact weight values after training.
- **Determinism:** Where feasible, enable `torch.use_deterministic_algorithms(True)` in a session-scoped fixture; document any ops that require exceptions.
- **What not to test:** Do not write unit tests for full training loops, convergence, or final accuracy — those belong in integration/smoke tests or experiment tracking.
- **`conftest.py`:** Use session- or module-scoped fixtures for expensive setup (small toy model, synthetic dataset). Put shared fixtures in `tests/conftest.py`.
- **Mocks vs real objects:** Mock I/O (cloud storage, file systems, clocks); use real small tensors/arrays for numerical code so shape and dtype bugs surface.

## 4. Run

- Execute the same command documented in README or CI (e.g. `pytest`, `uv run pytest`).
- Fix failures and linter issues on new test files per project/global standards. If the repo has no Ruff config, rely on user-level `~/.config/ruff/ruff.toml` when running Ruff (per **python-engineering-standards**).
