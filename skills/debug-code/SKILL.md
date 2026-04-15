---
name: debug-code
description: >-
  Systematically investigates and fixes bugs in codebases: reads error traces, narrows
  the fault, and applies language-appropriate debugging strategies. Includes
  Python- and ML-specific checks (NaNs, infs, shape mismatches, CUDA errors, wrong
  loss curves, import/dependency problems). Use when the user reports an error,
  unexpected behavior, a model not training, or asks to investigate a bug.
---

# Debug code

## 1. Understand the symptom

- Read the **full traceback** or error message; note the file, line, and exception type.
- Ask for a **minimal reproducer** if one isn't provided and the issue isn't obvious from context.
- Clarify: is this a crash, wrong output, or unexpected behavior (e.g. loss not decreasing)?

## 2. Locate the fault

- Follow the traceback from **bottom** (root cause) to top (call site).
- Search the codebase for the failing symbol; read surrounding context before editing.
- Identify whether the fault is in: user code, a library call, a data pipeline, or configuration.

## 3. ML-specific checks

### NaNs and infs

- Bisect by adding `assert torch.isfinite(x).all()` (or `np.isfinite`) at key points to find where NaN first appears.
- Common causes: division by zero, `log(0)`, exploding gradients (add gradient clipping), missing data normalization, bad loss reduction.
- Check **input data** for NaN/inf before it enters the model (`assert dataset[i]` on a sample).

### Shape mismatches

- Print `.shape` at the failing call and one step earlier to see where dimensions diverge.
- Check batch dimension ordering, channel convention (NCHW vs NHWC), and accidental `squeeze`/`unsqueeze` mismatches.

### Loss not decreasing

- Verify the loss is computed on the correct output — pre-softmax logits vs probabilities, correct target dtype, correct reduction.
- **Single-batch overfit test:** if the model cannot overfit one batch to near-zero loss, the model architecture or loss is wrong before any data pipeline issue matters.
- Check that `optimizer.zero_grad()` is called each step, gradients are not accidentally detached, and `loss.backward()` runs before `optimizer.step()`.

### CUDA errors

- Reproduce on **CPU first** (`model.cpu()`, `tensor.cpu()`); CPU error messages are often more informative.
- `CUDA error: device-side assert triggered` typically means a tensor value is out of range (e.g. class index ≥ `num_classes`); add CPU-side assertions before the failing op.
- Mismatched devices (model on GPU, tensor on CPU) produce clear errors — search for `.to(device)` calls that may have been skipped.

### Import and dependency errors

- Isolate with `uv run python -c "import <pkg>"` to confirm the package is installed.
- Run `uv sync` to ensure the active environment matches `pyproject.toml`.

## 4. Fix

- Make the **smallest change** that addresses the root cause; do not refactor unrelated code.
- Add a regression test if the bug is reproducible and testable (see **implement-tests** skill).

## 5. Verify

- Run the previously failing code path to confirm the fix.
- Run the full test suite if the project has one.
- Briefly note the root cause and what changed.
