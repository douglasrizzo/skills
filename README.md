# skills

Personal rules and skills for AI coding agents (Claude Code and Cursor), focused on Python and machine learning projects.

`CLAUDE.md` encodes engineering standards that apply to every session. Skills are on-demand workflows — feature implementation, code review, testing, debugging, and pull request management — that the agent follows step by step when invoked.

## Structure

```
CLAUDE.md                            # always-on: tooling, design, naming, patterns
skills/
  bootstrap-python-project/          # scaffold a new Python repo
  debug-code/                        # diagnose errors, NaNs, shape mismatches, CUDA issues
  design-patterns-ml/                # when and how to apply patterns in ML codebases
  implement-feature/                 # plan, place, DRY-check, implement, validate
  implement-tests/                   # add or extend tests, with ML-specific guidance
  open-pr/                           # draft and open a pull request via gh
  review-code/                       # review existing code for quality and correctness
  review-pr/                         # fetch and review an open pull request via gh
```

## Installation

Clone this repo to a stable location. The instructions below use symlinks so any edit here is immediately reflected everywhere — no copying or syncing needed.

**Run each global install block from this repository’s root** (the directory that contains `CLAUDE.md`). Each block sets `REPO_ROOT=$(pwd -P)` and checks for `CLAUDE.md`, so you do not need to export a path manually.

### Claude Code (global, one-time)

```bash
REPO_ROOT=$(pwd -P)
[ -f "$REPO_ROOT/CLAUDE.md" ] || { echo >&2 "Error: run this from the skills repo root."; exit 1; }

# Symlink the rules file as your global CLAUDE.md
ln -sf "$REPO_ROOT/CLAUDE.md" ~/.claude/CLAUDE.md

# Symlink each skill as a global custom command
mkdir -p ~/.claude/commands
for dir in "$REPO_ROOT"/skills/*/; do
  name=$(basename "$dir")
  ln -sf "$dir/SKILL.md" ~/.claude/commands/"$name".md
done
```

The engineering standards are injected into every session automatically. Skills become slash commands available everywhere: `/implement-feature`, `/review-code`, `/debug-code`, etc.

### Cursor (global, one-time)

Cursor loads **rules** from `~/.cursor/rules/` (files named `*.mdc`) and **agent skills** from `~/.cursor/skills/<skill-name>/SKILL.md`. Symlink this repo so edits here apply everywhere. Do not use `~/.cursor/skills-cursor/` — that directory is reserved for Cursor’s built-in skills.

```bash
REPO_ROOT=$(pwd -P)
[ -f "$REPO_ROOT/CLAUDE.md" ] || { echo >&2 "Error: run this from the skills repo root."; exit 1; }

mkdir -p ~/.cursor/rules ~/.cursor/skills

# Always-on engineering standards (CLAUDE.md → rule file)
ln -sf "$REPO_ROOT/CLAUDE.md" ~/.cursor/rules/python-engineering-standards.mdc

# One directory per skill; each contains SKILL.md
for dir in "$REPO_ROOT"/skills/*/; do
  name=$(basename "$dir")
  mkdir -p ~/.cursor/skills/"$name"
  ln -sf "$dir/SKILL.md" ~/.cursor/skills/"$name"/SKILL.md
done
```

`CLAUDE.md` is stored as `python-engineering-standards.mdc` so Cursor treats it as a rule; the YAML frontmatter (`alwaysApply: true`, `description`, etc.) is unchanged.

### Cursor (per-project)

If you prefer project-local wiring (e.g. different machines or repo-specific overrides), symlink into **that project’s** `.cursor/` instead of your home directory.

Run the first lines **from this repository’s root** (where `CLAUDE.md` lives) so `SKILLS_ROOT` is set correctly; then `cd` to the project you are wiring (change the path in the `cd` line):

```bash
SKILLS_ROOT=$(pwd -P)
[ -f "$SKILLS_ROOT/CLAUDE.md" ] || { echo >&2 "Error: run the first two lines from the skills repo root."; exit 1; }

cd /path/to/your/project   # repository root of the project you are configuring

mkdir -p .cursor/rules .cursor/skills

ln -sf "$SKILLS_ROOT/CLAUDE.md" .cursor/rules/python-engineering-standards.mdc

for dir in "$SKILLS_ROOT"/skills/*/; do
  [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
  name=$(basename "$dir")
  mkdir -p .cursor/skills/"$name"
  ln -sf "$dir/SKILL.md" .cursor/skills/"$name"/SKILL.md
done
```

You can wrap this in a shell function: capture `SKILLS_ROOT` once from `$(cd /path/to/skills && pwd -P)` (or from `pwd -P` while standing in the skills repo), then `cd` to the target project and run the `mkdir` / `ln` / `for` loop.

### If you see a folder literally named `*`

That usually means the install script ran **from the wrong directory** (so the glob `skills/*/` matched nothing and Bash treated `*` literally), or the **`skills/`** tree was missing. **Remove the bad directory**, `cd` to this repository’s root (where `CLAUDE.md` is), and run the Cursor (global) block again:

```bash
# Removes only the directory whose name is literally "*", not other skills:
rm -rf -- ~/.cursor/skills/'*'

cd /path/to/this/repo   # skills repo root: must contain CLAUDE.md and skills/
# run the Cursor (global) block again
```

## Usage

### Claude Code

Invoke a skill with its slash command:

```
/implement-feature
/review-code
/debug-code
/implement-tests
/open-pr
/review-pr
/bootstrap-python-project
```

The agent will follow the skill's workflow: clarify, plan, wait for your confirmation, then implement.

### Cursor

With the symlinks above, the always-on rule applies every chat; workflows are available as **agent skills** under `~/.cursor/skills/` (or `.cursor/skills/` per project). The model selects them when your task matches their `description`, or you can name a skill in your prompt (e.g. “follow the implement-feature skill”).

## Defaults (bootstrap-python-project)

| Topic | Default |
|---|---|
| Python | Second-latest stable release |
| Package manager | uv |
| Layout | `src/<package>/` |
| Linter / formatter | Ruff |
| Type checker | ty |
| Docstrings | Google style |
| Tests | pytest |

## Design philosophy

- Rules encode what should always be true (tooling, naming, structure).
- Skills encode workflows that require judgment and user interaction.
- Design patterns are applied reactively to complexity, not preemptively to every file.
- The agent plans before implementing and waits for confirmation before making changes.

## License

MIT
