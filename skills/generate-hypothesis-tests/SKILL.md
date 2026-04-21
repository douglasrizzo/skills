---
name: generate-hypothesis-tests
description: >-
  Generates property-based test stubs using the hypothesis ghostwriter
  (hypothesis write), then refines them into production-quality tests with
  tight strategies and domain-specific examples. Use when the user wants to
  add hypothesis tests for a module or function, or wants auto-generated test
  scaffolding as a starting point.
---

# Generate hypothesis tests

## 1. Discover

- Identify the target module(s) and specific symbols (functions, classes) from the user's request.
- Check that hypothesis is installed: `uv run python -c "import hypothesis"`. If not: `uv add --dev hypothesis`.
- Verify the symbol is importable from the project root (e.g., `uv run python -c "from mypackage.module import fn"`). Fix import errors before proceeding.
- Find where tests live and what naming convention they follow (e.g., `tests/test_<module>.py`).

## 2. Generate stubs

For each target symbol, run:

```
uv run hypothesis write <dotted.module.path.symbol>
```

Capture the full output. These stubs are the starting point — they will need refinement.

If `hypothesis write` cannot introspect a symbol (e.g., it is a class with complex init), note it and fall back to writing `@given` tests manually in Phase 3.

## 3. Refine stubs

Work through each generated stub and improve it:

- **Narrow strategies** to realistic domain values:
  - `st.text()` → `st.text(max_size=240)` or `st.text(alphabet=st.characters(whitelist_categories=("L", "N")))`.
  - `st.floats()` → `st.floats(min_value=0.0, allow_nan=False, allow_infinity=False)` when the domain requires it.
  - `st.integers()` → `st.integers(min_value=0, max_value=1_000_000)` for bounded counts.
- **Prefer semantic strategies** over generic ones:
  - `st.sampled_from(list(MyEnum))` for enum inputs.
  - `st.builds(MyDataclass, field=st.integers(...))` for structured inputs.
  - `.map(lambda x: f"{x:.2f}")` to produce formatted strings from raw floats.
- **Replace stub assertions** with real invariants. Stubs often assert only `assert result is not None` — replace with the property the function guarantees:
  - Round-trip: `assert parse(serialize(x)) == x`.
  - Monotonicity: `assert f(a) <= f(b)` when `a <= b`.
  - Idempotency: `assert f(f(x)) == f(x)`.
  - Length invariant: `assert len(result) == len(inputs)`.
- **Add `@example(...)` decorators** for known edge cases, boundary values, or previous bugs that were fixed.
- **Delete stubs** that cannot be made to assert a meaningful property — do not keep tests that only verify the function does not crash.

## 4. Configure hypothesis profiles

Ensure `tests/conftest.py` (or the project's conftest) includes a CI profile that caps example count:

```python
from hypothesis import settings
import os

settings.register_profile("ci", max_examples=50)
if os.environ.get("CI"):
    settings.load_profile("ci")
```

Add this block if it is not already present.

## 5. Run and iterate

- Run `uv run pytest <test file> -v`.
- Fix any failures introduced during refinement.
- For each passing test, confirm the assertion is non-trivial: mentally mutate the function under test and ask whether the test would catch it. If not, strengthen the strategy or the assertion.
- Linter: ruff runs automatically via the project hook; do not invoke it manually. Also run `uv run pylint <package>` and fix any new violations it reports.
