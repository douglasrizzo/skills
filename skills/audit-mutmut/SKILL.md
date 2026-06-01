---
name: audit-mutmut
description: >-
  Runs mutmut to detect surviving mutants (code changes the test suite did not
  catch), then writes targeted tests to kill them. Use when the user wants to
  audit test quality, find gaps in test coverage, or ensure tests catch real
  bugs — not just achieve line coverage.
---

# Audit tests with mutmut

## 1. Configure

Check `pyproject.toml` for `[tool.mutmut]`. If the section is absent, ask the user which source files or directories matter most for correctness, then write:

```toml
[tool.mutmut]
paths_to_mutate = [
    "src/mypackage/core.py",
]
also_copy = ["src/mypackage"]
do_not_mutate = [
    "*/__init__.py",
]
max_stack_depth = 8
```

Guidelines for `do_not_mutate`:
- Always exclude `*/__init__.py`.
- Exclude UI, plotting, logging, and bootstrap modules — mutations there are hard to observe via unit tests and produce noise.

Ensure mutmut is installed: `uv add --dev "mutmut>=3.5"`.

## 2. Run mutmut

Prefer a project-local wrapper if it exists:

```bash
# If scripts/run_mutmut.py exists in the project:
uv run scripts/run_mutmut.py run

# Otherwise, use the skill's bundled wrapper (handles macOS setproctitle crash):
uv run ~/.agents/skills/audit-mutmut/run_mutmut.py run
```

Mutmut can take several minutes on a large project. Capture the summary line at the end (killed / survived / timeout counts).

## 3. Triage survivors

List surviving mutants:

```bash
uv run ~/.agents/skills/audit-mutmut/run_mutmut.py results
```

Group survivors by source file and mutation type. Common mutation types and what they reveal:

| Type | Mutmut changes | Gap it exposes |
|------|---------------|---------------|
| Arithmetic | `+` → `-`, `*` → `/` | Missing boundary assertions |
| Comparison | `<` → `<=`, `==` → `!=` | Off-by-one tests absent |
| Boolean | `and` → `or`, `not x` → `x` | Short-circuit logic not tested |
| Return value | `return x` → `return None` | Callers don't assert on output |
| String literal | `"ok"` → `""` | String content not validated |

Focus first on survivors in core logic paths; ignore survivors in logging or error-message formatting unless they represent real behavioral gaps.

Mark any survivor as an **equivalent mutant** (safe to ignore) only when the mutated code is provably indistinguishable from the original under all reachable inputs. Document these in a comment or `do_not_mutate` pattern.

## 4. Write killing tests

For each survivor that is NOT an equivalent mutant:

1. Read the mutated line and understand what behavior it breaks.
2. Write the minimal test that passes on the original code and fails on the mutant.
3. Prefer `@given` (hypothesis) when the survivor is a boundary or comparison mutation — a property-based test will naturally probe the boundary.
4. Prefer a focused unit test over an integration test: test the function directly.
5. Name the test to describe the invariant: `test_calculate_returns_zero_for_empty_list`, not `test_mutant_42`.

Place new tests in the existing test file for that module. Follow the project's fixture and naming conventions.

## 5. Verify

Re-run mutmut:

```bash
uv run ~/.agents/skills/audit-mutmut/run_mutmut.py run
```

Confirm the survivor count dropped. Report:

- How many mutants were killed by the new tests.
- Any remaining survivors and whether they are equivalent mutants.
- Suggested `do_not_mutate` patterns for confirmed equivalent mutants.

If survivors remain that are not equivalent mutants, repeat phases 3–4.
