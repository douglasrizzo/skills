---
name: implement-tests
description: >-
  Adds or extends automated tests from a feature description (new or existing). Matches
  the repository's test layout, runner, and naming; if none exist, uses a root-level
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

## 3. Plan before writing

Before writing any test code, produce a **test plan** — a list of scenarios, each one line:

```
- <function/method under test>: <scenario> → <expected outcome>
```

Cover, in order of priority:
1. **Core behavior** — the main thing the function is supposed to do.
2. **Edge cases and boundaries** — empty inputs, zero/one/max values, None/missing keys, off-by-one, Unicode, large inputs.
3. **Error paths** — invalid input, permissions failures, malformed data. What *should* raise or return an error?
4. **State transitions** — if the code mutates state, test before/after across meaningful transitions.

Skip scenarios that are already covered by existing tests. Present the plan and wait for confirmation before writing code.

## 3.5. Identify property-based candidates (optional)

After the test plan, scan the target module for **pure functions and data transformations** — parsers, validators, formatters, enum converters, calculators.

For each candidate, add a hypothesis scenario to the plan:

```
- <function>: property — <invariant that must always hold>
```

Then, when writing the test, use `@given` with the tightest sensible strategy:

- `st.text(max_size=240)` not bare `st.text()`.
- `st.floats(min_value=0.0, allow_nan=False)` for domain-restricted floats.
- `st.sampled_from(list(MyEnum))` for enum round-trip tests.
- Chain `.map(...)` to produce formatted inputs from raw values.
- Add `@example(...)` for known edge cases or previous regressions.

If hypothesis is not already a dev dependency, add it: `uv add --dev hypothesis`.

Ensure `conftest.py` registers a CI profile (create if it doesn't exist):

```python
from hypothesis import settings
import os

settings.register_profile("ci", max_examples=50)
if os.environ.get("CI"):
    settings.load_profile("ci")
```

Skip this phase if the module has no pure transformation logic (e.g., it is entirely stateful or side-effectful).

## 4. Write

### What to test

- **Test observable behavior through public interfaces.** Each test answers: "if this behavior broke, would a user or caller notice?" If not, skip it.
- **Each test must be able to fail meaningfully.** For every test, be able to state what bug or regression it catches. If you cannot, the test is not worth writing.
- Structure tests as **Arrange / Act / Assert** (or Given / When / Then). One behavior per test.

### What NOT to test

- Constructors, getters/setters, or simple delegation with no logic.
- Implementation details: private methods, internal call counts, ordering of internal steps.
- Anything that would break on a *refactor* but not on a *bug* — that is a test of implementation, not behavior.
- Do not write `assert True`, `assert obj is not None` as the sole assertion, or tests that simply confirm the code runs without error and nothing else.

### Mocking discipline

- **Mock only at architectural boundaries**: network, database, filesystem, clocks, external services.
- **Never mock the unit under test** or its core collaborators — use real objects with controlled inputs.
- If a test mocks so much that the assertion just checks the mock's return value, it is a tautology. Delete it and test at a higher level instead.

### ML-specific notes

- **Seeds:** Set `torch.manual_seed` / `np.random.seed` / `random.seed` at the top of each test that involves randomness, or in a shared `conftest.py` autouse fixture.
- **What to test in models:** Assert output *shape*, loss value range (finite, non-negative), and that one gradient step reduces loss on a single batch. Do **not** assert on exact weight values after training.
- **Determinism:** Where feasible, enable `torch.use_deterministic_algorithms(True)` in a session-scoped fixture; document any ops that require exceptions.
- **What not to test:** Do not write unit tests for full training loops, convergence, or final accuracy — those belong in integration/smoke tests or experiment tracking.
- **`conftest.py`:** Use session- or module-scoped fixtures for expensive setup (small toy model, synthetic dataset). Put shared fixtures in `tests/conftest.py`.
- **Mocks vs real objects:** Mock I/O (cloud storage, file systems, clocks); use real small tensors/arrays for numerical code so shape and dtype bugs surface.

## 5. Run

- Execute the same command documented in README or CI (e.g. `pytest`, `uv run pytest`).
- Fix failures and linter issues on new test files per project/global standards. If the repo has no Ruff config, rely on user-level `~/.config/ruff/ruff.toml` when running Ruff (per **python-engineering-standards**).

## 6. Self-check

After tests pass, review each test against these criteria:
- Does it test **behavior**, not implementation?
- Would a real bug actually make it **fail**?
- Is the assertion **specific** (checking a value, exception type, or state change — not just "no error")?

Delete or rewrite any test that fails these checks.
