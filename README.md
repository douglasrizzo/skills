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

### Claude Code (global, one-time)

```bash
# Symlink the rules file as your global CLAUDE.md
ln -sf ~/code/personal/skills/CLAUDE.md ~/.claude/CLAUDE.md

# Symlink each skill as a global custom command
mkdir -p ~/.claude/commands
for dir in ~/code/personal/skills/skills/*/; do
  name=$(basename "$dir")
  ln -sf "$dir/SKILL.md" ~/.claude/commands/"$name".md
done
```

The engineering standards are injected into every session automatically. Skills become slash commands available everywhere: `/implement-feature`, `/review-code`, `/debug-code`, etc.

### Cursor (per-project)

Cursor reads rules from `.cursor/rules/` inside each project. Add this alias to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
alias install-skills='
  mkdir -p .cursor/rules
  ln -sf ~/code/personal/skills/CLAUDE.md .cursor/rules/python-engineering-standards.mdc
  for dir in ~/code/personal/skills/skills/*/; do
    name=$(basename "$dir")
    ln -sf "$dir/SKILL.md" .cursor/rules/"$name".mdc
  done
'
```

Run `install-skills` from the root of any new project. Cursor picks up `alwaysApply: true` rules automatically and injects skills as context when the task matches their description.

> `CLAUDE.md` is symlinked with a `.mdc` extension so Cursor recognises it as a rule file. The frontmatter (`alwaysApply: true`) works regardless of where the file originates.

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

Skills are injected automatically based on what you are asking. You can also mention a skill by name in your prompt (e.g. "follow the implement-feature skill") to trigger it explicitly.

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
