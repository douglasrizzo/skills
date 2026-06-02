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
- Global design and tooling expectations are in the engineering standards (`AGENTS.md`).

## 2. Read and understand

- Read the full target code (file, class, or function as specified).
- Map callers and callees, shared state, and side effects (I/O, globals, mutation).
- Note tests that lock the current behavior before touching anything.

## 3. Evaluate

Launch all **six** in parallel so they run concurrently (if the diff includes SQL files or BigQuery Python code, include `review-bigquery-sql`; otherwise skip it):

```
task(
  description="review types",
  prompt="""Review the following diff for type annotation issues:

<paste the full diff or list of changed files here>

Project: <brief context about what was changed>""",
  subagent_type="review-types")

task(
  description="review architecture",
  prompt="""Review the following diff for architecture issues:

<diff>

Project: <context>""",
  subagent_type="review-architecture")

task(
  description="review python style",
  prompt="""Review the following diff for idiomatic Python, naming, and
docstring issues:

<diff>

Project: <context>""",
  subagent_type="review-python")

task(
  description="review training safety",
  prompt="""Review the following diff for training pipeline safety issues
(model forward contract, optimizer hygiene, Lightning hooks,
reproducibility, config defaults, logging, SQL):

<diff>

Project: <context>""",
  subagent_type="review-ml-safety")

task(
  description="review data safety",
  prompt="""Review the following diff for data pipeline safety issues
(DataLoader, multiprocessing, file validation, transforms,
normalization, timm config):

<diff>

Project: <context>""",
  subagent_type="review-data-safety")

task(
  description="review bigquery sql",
  prompt="""Review the following diff for BigQuery SQL issues (safety, performance,
cost, correctness):

<diff>

Project: <context>
Focus on parameterized queries, SELECT *, partition filters,
LIMIT/ORDER BY, UNION ALL, and string interpolation risks.""",
  subagent_type="review-bigquery-sql")
```

**Only include `review-bigquery-sql` when the diff touches `.sql` files or Python files with BigQuery patterns** (`client.query`, `QueryJobConfig`, `query_parameters`, large f-string SQL blocks). Skip it for pure application-code reviews.

### Agent responsibilities

| Agent | Scope | Example checks |
|---|---|---|
| `review-types` | Type annotations, `Optional`, `TYPE_CHECKING`, `Any` | `Callable[...] \| None` when runtime rejects `None` |
| `review-architecture` | Module placement, DRY, thin entrypoints, patterns, YAGNI | Business logic in `cli/`, `forward()` vs `training_step()` separation |
| `review-python` | Idiomatic Python, naming, docstrings | f-strings, `pathlib`, entry-point guards, `@dataclass`/`Enum` |
| `review-ml-safety` | Training pipeline: forward contract, optimizer, Lightning hooks, reproducibility, config, logging, SQL | `squeeze()` axis safety, `model.eval()`, `save_hyperparameters()`, `bf16-mixed` |
| `review-data-safety` | Data pipeline: DataLoader, multiprocessing, file validation, transforms, normalization, timm config | `pin_memory`, worker seeds, transform order, augmentation leakage, gRPC lazy-init |
| `review-bigquery-sql` | BigQuery SQL in `.sql` files and Python: safety, performance, cost, correctness | String interpolation, `SELECT *`, partition filters, `LIMIT`/`ORDER BY`, `UNION ALL`, parameterization |

### After all return

- **Deduplicate** — the same issue may be caught by multiple agents (e.g., `if not x` flagged by both `review-types` and `review-data-safety`; SQL injection flagged by both `review-ml-safety` and `review-bigquery-sql`). Merge into one finding under the most relevant category.
- **Prioritize** — order by severity: data safety > training safety > bigquery SQL > architecture > types > style.
- **Present** — grouped by category, each finding with file:line, issue description, and suggested fix.
- **Pre-existing issues** — note them as "pre-existing, not in scope" and skip them unless the user asks to fix them.

The original evaluation lenses (canonical idioms, DRY, module organization, design patterns, naming) are covered by the agents — do not re-evaluate manually what the agents already checked.

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

- Run **linter/type checker**; fix new issues introduced by your changes. Fall back to user-level configs (`~/.config/ruff/ruff.toml`, `~/.config/ty/ty.toml`) if no project config exists. Also run `uv run pylint <package>`; the global baseline is `~/.config/pylintrc` and project-level `[tool.pylint.*]` in `pyproject.toml` overrides it.
- Run **tests**; all pre-existing tests must still pass.

## 8. Close

- Summarize what changed, what was left alone and why, and any recommended follow-ups.
