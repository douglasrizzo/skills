#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/install-skills.sh <agent>

Install this repo's skills globally for the selected agent using symlinks.

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

  if [ ! -f "$repo_root/CLAUDE.md" ]; then
    echo >&2 "Error: could not find CLAUDE.md from repo root."
    exit 1
  fi

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

  mkdir -p "$HOME/.claude/commands"
  ln -sf "$repo_root/CLAUDE.md" "$HOME/.claude/CLAUDE.md"

  local dir name
  for dir in "$repo_root"/skills/*/; do
    [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
    name=$(basename "$dir")
    ln -sf "$dir/SKILL.md" "$HOME/.claude/commands/$name.md"
  done
}

install_codex() {
  local repo_root=$1

  mkdir -p "$HOME/.codex/skills"

  local dir name
  for dir in "$repo_root"/skills/*/; do
    [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
    name=$(basename "$dir")
    mkdir -p "$HOME/.codex/skills/$name"
    ln -sf "$dir/SKILL.md" "$HOME/.codex/skills/$name/SKILL.md"
  done
}

install_cursor() {
  local repo_root=$1

  mkdir -p "$HOME/.cursor/rules" "$HOME/.cursor/skills"
  ln -sf "$repo_root/CLAUDE.md" "$HOME/.cursor/rules/python-engineering-standards.mdc"

  local dir name
  for dir in "$repo_root"/skills/*/; do
    [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
    name=$(basename "$dir")
    mkdir -p "$HOME/.cursor/skills/$name"
    ln -sf "$dir/SKILL.md" "$HOME/.cursor/skills/$name/SKILL.md"
  done
}

main "$@"
