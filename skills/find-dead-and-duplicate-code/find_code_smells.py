#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "vulture>=2.14",
#   "pylint>=3.3",
#   "deepcsim>=0.1",
# ]
# ///
"""Run vulture, pylint similarities, and deepcsim on a Python project and emit a single filtered report.

The report is agent-friendly: one Markdown document (or JSON) with three sections
(dead code, textual duplicates, structural duplicates), pre-filtered to drop the
common false positives each tool is known to produce.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import io
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Record types
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class DeadCodeHit:
  path: str
  line: int
  kind: str
  name: str
  confidence: int
  suppressed_reason: str | None = None


@dataclass(slots=True)
class DupSite:
  path: str
  start: int
  end: int


@dataclass(slots=True)
class TextualDupBlock:
  line_count: int
  sites: list[DupSite]
  snippet: str


@dataclass(slots=True)
class StructuralDupPair:
  structural: float
  semantic: float
  metric: float
  composite: float
  a_path: str
  a_lines: str
  a_name: str
  b_path: str
  b_lines: str
  b_name: str


@dataclass(slots=True)
class Report:
  target: str
  scanned_at: str
  dead_code: list[DeadCodeHit] = field(default_factory=list)
  dead_code_suppressed: list[DeadCodeHit] = field(default_factory=list)
  textual_duplicates: list[TextualDupBlock] = field(default_factory=list)
  structural_duplicates: list[StructuralDupPair] = field(default_factory=list)
  structural_suppressed_count: int = 0


# ---------------------------------------------------------------------------
# Dead code: vulture
# ---------------------------------------------------------------------------

# Symbols that third-party frameworks reach by name. Dropping these avoids the
# most common false-positive class (SQLite row_factory, Streamlit callbacks,
# pytest fixtures with conventional prefixes).
_FRAMEWORK_NAME_ALLOWLIST = re.compile(
  r"^(?:"
  r"row_factory|text_factory|isolation_level|"  # sqlite3.Connection attrs
  r"pytest_\w+|fixture_\w+|"  # pytest hooks/fixtures
  r"st_\w+|"  # streamlit callback convention
  r"setUp|tearDown|setUpClass|tearDownClass"  # unittest
  r")$"
)


def _run_vulture(target: Path, min_confidence: int) -> list[DeadCodeHit]:
  """Invoke vulture programmatically and return unfiltered hits with display-relative paths."""
  try:
    from vulture import Vulture
  except ImportError as err:
    raise SystemExit(f"vulture is not available: {err}") from err

  v = Vulture(verbose=False)
  v.scavenge([str(target)])
  display_root = _display_root(target)
  hits: list[DeadCodeHit] = []
  for item in v.get_unused_code(min_confidence=min_confidence):
    hits.append(
      DeadCodeHit(
        path=_display_path(item.filename, display_root),
        line=item.first_lineno,
        kind=item.typ,
        name=item.name,
        confidence=item.confidence,
      )
    )
  return hits


def _module_all_names(path: Path) -> set[str]:
  """Return the names listed in the module's top-level ``__all__``, or empty set."""
  try:
    source = path.read_text(encoding="utf-8")
  except OSError:
    return set()
  try:
    tree = ast.parse(source, filename=str(path))
  except SyntaxError:
    return set()
  for node in tree.body:
    if not isinstance(node, ast.Assign):
      continue
    if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
      continue
    value = node.value
    if isinstance(value, (ast.List, ast.Tuple)):
      return {elt.value for elt in value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)}
  return set()


def _filter_dead_code(
  hits: list[DeadCodeHit],
  target: Path,
  skip_globs: list[str],
) -> tuple[list[DeadCodeHit], list[DeadCodeHit]]:
  """Split hits into (kept, suppressed) after applying suppression rules."""
  display_root = _display_root(target)
  all_cache: dict[Path, set[str]] = {}
  kept: list[DeadCodeHit] = []
  suppressed: list[DeadCodeHit] = []
  for hit in hits:
    if any(fnmatch.fnmatch(hit.path, pattern) for pattern in skip_globs):
      hit.suppressed_reason = "skip-glob"
      suppressed.append(hit)
      continue
    if _FRAMEWORK_NAME_ALLOWLIST.match(hit.name):
      hit.suppressed_reason = "framework-name"
      suppressed.append(hit)
      continue
    path = Path(hit.path) if Path(hit.path).is_absolute() else display_root / hit.path
    if path not in all_cache:
      all_cache[path] = _module_all_names(path)
    if hit.name in all_cache[path]:
      hit.suppressed_reason = "__all__"
      suppressed.append(hit)
      continue
    kept.append(hit)
  return kept, suppressed


# ---------------------------------------------------------------------------
# Textual duplicates: pylint similarities
# ---------------------------------------------------------------------------


_PYLINT_HEADER_RE = re.compile(r"^==([^:]+):\[(\d+):(\d+)\]$")


def _run_pylint_similarities(target: Path, min_lines: int) -> list[TextualDupBlock]:
  """Run pylint's similarities checker and parse its human-readable output into blocks."""
  cmd = [
    sys.executable,
    "-m",
    "pylint",
    "--disable=all",
    "--enable=similarities",
    f"--min-similarity-lines={min_lines}",
    str(target),
  ]
  completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
  return _parse_pylint_text(completed.stdout)


def _parse_pylint_text(text: str) -> list[TextualDupBlock]:
  """Parse pylint's ``R0801`` text output into ``TextualDupBlock`` records.

  Each report has the shape::

      path/a.py:1:0: R0801: Similar lines in N files
      ==module.a:[12:34]
      ==module.b:[56:78]
        <duplicated source>
        <duplicated source> (duplicate-code)
  """
  blocks: list[TextualDupBlock] = []
  lines = text.splitlines()
  i = 0
  while i < len(lines):
    line = lines[i]
    if ": R0801:" not in line:
      i += 1
      continue
    i += 1
    sites: list[DupSite] = []
    while i < len(lines) and (match := _PYLINT_HEADER_RE.match(lines[i])):
      module, start, end = match.groups()
      sites.append(DupSite(path=module, start=int(start), end=int(end)))
      i += 1
    snippet_lines: list[str] = []
    while i < len(lines):
      current = lines[i]
      if current.startswith("==") or ": R0801:" in current:
        break
      if current.startswith("-----------------") or current.startswith("Your code has been rated"):
        break
      snippet_lines.append(current)
      i += 1
      if current.rstrip().endswith("(duplicate-code)"):
        break
    if sites and snippet_lines:
      snippet = "\n".join(ln for ln in snippet_lines if ln.strip()).rstrip()
      snippet = snippet.removesuffix("(duplicate-code)").rstrip()
      line_count = max(site.end - site.start for site in sites)
      blocks.append(TextualDupBlock(line_count=line_count, sites=sites, snippet=snippet))
  return blocks


# ---------------------------------------------------------------------------
# Structural duplicates: deepcsim
# ---------------------------------------------------------------------------


def _run_deepcsim(target: Path, threshold: int) -> list[StructuralDupPair]:
  """Run deepcsim-cli and flatten its JSON into per-function-pair records."""
  cmd = ["deepcsim-cli", "--threshold", str(threshold), "--json", str(target)]
  try:
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
  except FileNotFoundError as err:
    raise SystemExit(
      "deepcsim-cli not found on PATH. Install deepcsim (it is declared in this script's "
      "PEP 723 deps; running via `uv run` should handle it)."
    ) from err
  stdout = completed.stdout
  start = stdout.find("{")
  if start < 0:
    return []
  try:
    data = json.loads(stdout[start:])
  except json.JSONDecodeError:
    return []
  pairs: list[StructuralDupPair] = []
  for pair in data.get("results", []):
    for comp in pair.get("comparisons", []):
      sim = comp.get("similarity", {})
      pairs.append(
        StructuralDupPair(
          structural=float(sim.get("structural", 0.0)),
          semantic=float(sim.get("semantic", 0.0)),
          metric=float(sim.get("metric", 0.0)),
          composite=float(sim.get("composite", 0.0)),
          a_path=pair.get("file1", ""),
          a_lines=comp.get("func1_lines", ""),
          a_name=comp.get("func1_name", ""),
          b_path=pair.get("file2", ""),
          b_lines=comp.get("func2_lines", ""),
          b_name=comp.get("func2_name", ""),
        )
      )
  return pairs


def _parse_line_range(value: str) -> tuple[int, int]:
  """Parse deepcsim's ``"123-145"`` line-range string into ``(start, end)``."""
  if "-" not in value:
    return (0, 0)
  start_s, end_s = value.split("-", 1)
  try:
    return (int(start_s), int(end_s))
  except ValueError:
    return (0, 0)


def _ranges_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
  return not (a[1] < b[0] or b[1] < a[0])


def _filter_structural(
  pairs: list[StructuralDupPair],
  textual: list[TextualDupBlock],
  target: Path,
  min_struct: float,
  min_composite: float,
  min_func_lines: int,
) -> tuple[list[StructuralDupPair], int]:
  """Apply score, length, and cross-tool-dedup filters; return (kept, suppressed_count)."""
  # Index textual-duplicate sites by normalized path for cross-tool dedup.
  textual_sites: dict[str, list[tuple[int, int]]] = {}
  for block in textual:
    for site in block.sites:
      textual_sites.setdefault(_normalize_module_path(site.path, target), []).append((site.start, site.end))

  kept: list[StructuralDupPair] = []
  suppressed = 0
  for pair in pairs:
    if pair.structural < min_struct or pair.composite < min_composite:
      suppressed += 1
      continue
    a_range = _parse_line_range(pair.a_lines)
    b_range = _parse_line_range(pair.b_lines)
    a_len = max(a_range[1] - a_range[0] + 1, 0)
    b_len = max(b_range[1] - b_range[0] + 1, 0)
    if a_len < min_func_lines or b_len < min_func_lines:
      suppressed += 1
      continue
    a_key = _normalize_module_path(pair.a_path, target)
    b_key = _normalize_module_path(pair.b_path, target)
    if any(_ranges_overlap(a_range, r) for r in textual_sites.get(a_key, ())) or any(
      _ranges_overlap(b_range, r) for r in textual_sites.get(b_key, ())
    ):
      suppressed += 1
      continue
    kept.append(pair)
  kept.sort(key=lambda p: (-p.composite, -p.structural))
  return kept, suppressed


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def _display_root(target: Path) -> Path:
  """Return the directory paths should be displayed relative to.

  Uses ``target``'s parent so paths render as e.g. ``src/portfolio/foo.py`` when
  the user scanned ``src/portfolio``, which is the most readable form.
  """
  resolved = target.resolve()
  base = resolved.parent if resolved.is_file() else resolved
  parent = base.parent
  return parent if parent != base else base


def _display_path(path_str: str, display_root: Path) -> str:
  """Render ``path_str`` relative to ``display_root`` when possible, else return as-is."""
  try:
    return str(Path(path_str).resolve().relative_to(display_root))
  except ValueError:
    return str(path_str)


def _relativize(path_str: str, target: Path) -> str:
  """Return ``path_str`` relative to ``target``'s parent for skip-glob matching."""
  return _display_path(path_str, _display_root(target))


def _normalize_module_path(value: str, target: Path) -> str:
  """Normalize pylint-style ``module.a`` and filesystem paths to a common form for dedup."""
  if value.endswith(".py"):
    return str(Path(value).resolve())
  # Pylint emits fully-qualified module paths like ``portfolio.bootstrap``. If the
  # target directory's basename matches the first segment (the package name), drop
  # that segment before joining, so ``src/portfolio`` + ``portfolio.bootstrap``
  # becomes ``src/portfolio/bootstrap.py`` rather than ``src/portfolio/portfolio/bootstrap.py``.
  parts = value.split(".")
  target_resolved = target.resolve()
  if parts and parts[0] == target_resolved.name:
    parts = parts[1:]
  path_guess = target_resolved.joinpath(*parts).with_suffix(".py") if parts else target_resolved
  return str(path_guess)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _render_markdown(report: Report, *, include_dead: bool, include_text: bool, include_struct: bool) -> str:
  """Render the report as a single Markdown document."""
  out = io.StringIO()
  out.write(f"# Code smells: {report.target}\n")
  out.write(f"_Scanned {report.scanned_at}_\n\n")

  if include_dead:
    kept = report.dead_code
    out.write(f"## Dead code ({len(kept)} after filters, {len(report.dead_code_suppressed)} suppressed)\n\n")
    if kept:
      out.write("| File:Line | Kind | Name | Confidence |\n")
      out.write("|---|---|---|---|\n")
      for hit in kept:
        out.write(f"| `{hit.path}:{hit.line}` | {hit.kind} | `{hit.name}` | {hit.confidence}% |\n")
      out.write("\n")
    else:
      out.write("_No dead-code hits above threshold._\n\n")
    if report.dead_code_suppressed:
      reasons: dict[str, list[str]] = {}
      for hit in report.dead_code_suppressed:
        reasons.setdefault(hit.suppressed_reason or "other", []).append(f"`{hit.path}:{hit.line}` `{hit.name}`")
      out.write("<details><summary>Suppressed</summary>\n\n")
      for reason, entries in sorted(reasons.items()):
        out.write(f"- **{reason}** ({len(entries)}): {', '.join(entries)}\n")
      out.write("\n</details>\n\n")

  if include_text:
    out.write(f"## Textual duplicates ({len(report.textual_duplicates)} blocks)\n\n")
    if report.textual_duplicates:
      for idx, block in enumerate(report.textual_duplicates, start=1):
        out.write(f"### Block {idx} — {block.line_count} lines, {len(block.sites)} sites\n\n")
        for site in block.sites:
          out.write(f"- `{site.path}:{site.start}-{site.end}`\n")
        out.write("\n```python\n")
        out.write(block.snippet)
        out.write("\n```\n\n")
    else:
      out.write("_No textual duplicates at this threshold._\n\n")

  if include_struct:
    kept = report.structural_duplicates
    out.write(
      f"## Structural duplicates ({len(kept)} after filters, {report.structural_suppressed_count} suppressed)\n\n"
    )
    if kept:
      out.write("| Struct | Comp | A | B |\n")
      out.write("|---|---|---|---|\n")
      for pair in kept:
        a = f"`{pair.a_path}:{pair.a_lines}` `{pair.a_name}`"
        b = f"`{pair.b_path}:{pair.b_lines}` `{pair.b_name}`"
        out.write(f"| {pair.structural:.0f} | {pair.composite:.0f} | {a} | {b} |\n")
      out.write("\n")
    else:
      out.write("_No structural duplicates survived filtering._\n\n")

  return out.getvalue()


def _render_json(report: Report) -> str:
  """Render the report as a single JSON object."""

  def as_dict(obj: object) -> object:
    if hasattr(obj, "__slots__"):
      return {slot: as_dict(getattr(obj, slot)) for slot in obj.__slots__}  # type: ignore[attr-defined]
    if isinstance(obj, list):
      return [as_dict(x) for x in obj]
    return obj

  payload = {
    "target": report.target,
    "scanned_at": report.scanned_at,
    "dead_code": [as_dict(h) for h in report.dead_code],
    "dead_code_suppressed": [as_dict(h) for h in report.dead_code_suppressed],
    "textual_duplicates": [as_dict(b) for b in report.textual_duplicates],
    "structural_duplicates": [as_dict(p) for p in report.structural_duplicates],
    "structural_suppressed_count": report.structural_suppressed_count,
  }
  return json.dumps(payload, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Find dead and duplicate Python code; emit one filtered report.",
  )
  parser.add_argument("target", type=Path, help="Directory to scan (e.g. src/portfolio)")
  parser.add_argument("--format", choices=["md", "json"], default="md")
  parser.add_argument("--output", type=Path, default=None, help="Write to file instead of stdout")
  parser.add_argument("--skip-dead", action="store_true")
  parser.add_argument("--skip-dup-text", action="store_true")
  parser.add_argument("--skip-dup-struct", action="store_true")
  parser.add_argument("--min-confidence", type=int, default=60)
  parser.add_argument("--min-similarity-lines", type=int, default=6)
  parser.add_argument("--deepcsim-threshold", type=int, default=80)
  parser.add_argument("--min-struct", type=float, default=85.0)
  parser.add_argument("--min-composite", type=float, default=85.0)
  parser.add_argument("--min-func-lines", type=int, default=8)
  parser.add_argument(
    "--skip-globs",
    default="tests/**,**/ui/**",
    help="Comma-separated globs (relative to target's parent) to suppress dead-code hits in.",
  )
  return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
  args = _parse_args(argv if argv is not None else sys.argv[1:])
  target: Path = args.target
  if not target.exists():
    print(f"target does not exist: {target}", file=sys.stderr)
    return 2

  skip_globs = [g.strip() for g in args.skip_globs.split(",") if g.strip()]
  report = Report(
    target=str(target),
    scanned_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
  )

  if not args.skip_dead:
    raw = _run_vulture(target, args.min_confidence)
    kept, suppressed = _filter_dead_code(raw, target, skip_globs)
    report.dead_code = kept
    report.dead_code_suppressed = suppressed

  if not args.skip_dup_text:
    report.textual_duplicates = _run_pylint_similarities(target, args.min_similarity_lines)

  if not args.skip_dup_struct:
    raw_pairs = _run_deepcsim(target, args.deepcsim_threshold)
    kept_pairs, suppressed_count = _filter_structural(
      raw_pairs,
      report.textual_duplicates,
      target,
      args.min_struct,
      args.min_composite,
      args.min_func_lines,
    )
    report.structural_duplicates = kept_pairs
    report.structural_suppressed_count = suppressed_count

  if args.format == "json":
    rendered = _render_json(report)
  else:
    rendered = _render_markdown(
      report,
      include_dead=not args.skip_dead,
      include_text=not args.skip_dup_text,
      include_struct=not args.skip_dup_struct,
    )

  if args.output is not None:
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output}", file=sys.stderr)
  else:
    sys.stdout.write(rendered)
    if not rendered.endswith("\n"):
      sys.stdout.write("\n")
  return 0


if __name__ == "__main__":
  sys.exit(main())
