#!/usr/bin/env bash
# Builds per-agent instruction files from fragments and installs them via symlinks.
# Run from anywhere — the script locates the repo root automatically.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/install-skills.sh <agent>

Build dist/ files from fragments and install this repo's skills globally
for the selected agent using symlinks.

Supported agents:
  claude
  codex
  cursor
EOF
}

main() {
  if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
  fi

  if [ "$#" -ne 1 ]; then
    usage >&2
    exit 1
  fi

  local repo_root
  repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)

  # Build dist/ files from fragments before installing
  bash "$repo_root/scripts/build.sh"

  case "$1" in
    claude)
      install_claude "$repo_root"
      ;;
    codex)
      install_codex "$repo_root"
      ;;
    cursor)
      install_cursor "$repo_root"
      ;;
    *)
      echo >&2 "Error: unsupported agent '$1'."
      usage >&2
      exit 1
      ;;
  esac
}

install_claude() {
  local repo_root=$1

  # Engineering standards (generated)
  mkdir -p "$HOME/.claude/commands" "$HOME/.claude/rules"
  ln -sf "$repo_root/dist/CLAUDE.md" "$HOME/.claude/CLAUDE.md"

  # Skills → slash commands
  local dir name
  for dir in "$repo_root"/skills/*/; do
    [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
    name=$(basename "$dir")
    ln -sf "$dir/SKILL.md" "$HOME/.claude/commands/$name.md"
  done

  # Rules: python examples reference + context7
  ln -sf "$repo_root/rules/python-examples.md" "$HOME/.claude/rules/python-examples.md"
  ln -sf "$repo_root/fragments/context7.md"    "$HOME/.claude/rules/context7.md"

  echo "Installed for Claude Code:"
  echo "  ~/.claude/CLAUDE.md → dist/CLAUDE.md"
  echo "  ~/.claude/commands/<skill>.md × $(ls "$repo_root"/skills/*/SKILL.md | wc -l | tr -d ' ')"
  echo "  ~/.claude/rules/python-examples.md"
  echo "  ~/.claude/rules/context7.md"
}

install_codex() {
  local repo_root=$1

  # Engineering standards (generated, fully self-contained)
  mkdir -p "$HOME/.codex/skills" "$HOME/.codex/rules"
  ln -sf "$repo_root/dist/AGENTS.md" "$HOME/.codex/AGENTS.md"

  # Skills
  local dir name
  for dir in "$repo_root"/skills/*/; do
    [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
    name=$(basename "$dir")
    mkdir -p "$HOME/.codex/skills/$name"
    ln -sf "$dir/SKILL.md" "$HOME/.codex/skills/$name/SKILL.md"
  done

  # Rules: python examples reference
  ln -sf "$repo_root/rules/python-examples.md" "$HOME/.codex/rules/python-examples.md"

  echo "Installed for Codex:"
  echo "  ~/.codex/AGENTS.md → dist/AGENTS.md"
  echo "  ~/.codex/skills/<skill>/SKILL.md × $(ls "$repo_root"/skills/*/SKILL.md | wc -l | tr -d ' ')"
  echo "  ~/.codex/rules/python-examples.md"
}

install_cursor() {
  local repo_root=$1

  mkdir -p "$HOME/.cursor/rules" "$HOME/.cursor/skills"

  # Engineering standards (generated)
  ln -sf "$repo_root/dist/engineering-standards.mdc" \
         "$HOME/.cursor/rules/engineering-standards.mdc"

  # Context7 rule (generated)
  ln -sf "$repo_root/dist/context7.mdc" \
         "$HOME/.cursor/rules/context7.mdc"

  # Remove stale rule file from previous install if present
  local stale="$HOME/.cursor/rules/python-engineering-standards.mdc"
  if [ -L "$stale" ] || [ -f "$stale" ]; then
    rm -f "$stale"
    echo "  Removed stale: python-engineering-standards.mdc"
  fi

  # Skills
  local dir name
  for dir in "$repo_root"/skills/*/; do
    [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
    name=$(basename "$dir")
    mkdir -p "$HOME/.cursor/skills/$name"
    ln -sf "$dir/SKILL.md" "$HOME/.cursor/skills/$name/SKILL.md"
  done

  # Rules: python examples reference
  ln -sf "$repo_root/rules/python-examples.md" \
         "$HOME/.cursor/rules/python-examples.mdc"

  echo "Installed for Cursor:"
  echo "  ~/.cursor/rules/engineering-standards.mdc → dist/engineering-standards.mdc"
  echo "  ~/.cursor/rules/context7.mdc → dist/context7.mdc"
  echo "  ~/.cursor/rules/python-examples.mdc"
  echo "  ~/.cursor/skills/<skill>/SKILL.md × $(ls "$repo_root"/skills/*/SKILL.md | wc -l | tr -d ' ')"
}

main "$@"
