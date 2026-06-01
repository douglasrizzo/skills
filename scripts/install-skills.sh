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
  opencode
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
    opencode)
      install_opencode "$repo_root"
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

# ── Shared: install skills to ~/.agents/skills/ (read by both OpenCode and Cursor) ───

install_skills() {
  local repo_root=$1
  local target_base="${2:-$HOME/.agents/skills}"

  mkdir -p "$target_base"

  # Clean up stale skill symlinks at legacy per-tool paths
  for legacy in "$HOME/.cursor/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.config/opencode/skills"; do
    if [ -d "$legacy" ]; then
      for link in "$legacy"/*/; do
        [ -L "${link%/}" ] && rm -f "${link%/}"
      done
      # Remove empty legacy dir
      rmdir "$legacy" 2>/dev/null || true
    fi
  done

  local dir name target
  for dir in "$repo_root"/skills/*/; do
    [ -d "$dir" ] && [ -f "$dir/SKILL.md" ] || continue
    name=$(basename "$dir")
    target="$target_base/$name"
    if [ -L "$target" ]; then
      rm -f "$target"
    elif [ -d "$target" ]; then
      rm -rf "$target"
    fi
    ln -sfn "${dir%/}" "$target"
  done

  echo "  Skills: ~/.agents/skills/<skill> × $(ls -d "$repo_root"/skills/*/ | wc -l | tr -d ' ')"
}

# ── OpenCode ────────────────────────────────────────────────────────────────────────

install_opencode() {
  local repo_root=$1

  # AGENTS.md → ~/.config/opencode/AGENTS.md
  mkdir -p "$HOME/.config/opencode"
  ln -sf "$repo_root/dist/AGENTS.md" "$HOME/.config/opencode/AGENTS.md"

  # Agents → ~/.config/opencode/agents/
  mkdir -p "$HOME/.config/opencode/agents"
  local agent_dir agent_name agent_target
  for agent_dir in "$repo_root"/agents/*.md; do
    [ -f "$agent_dir" ] || continue
    agent_name=$(basename "$agent_dir")
    agent_target="$HOME/.config/opencode/agents/$agent_name"
    if [ -L "$agent_target" ]; then
      rm -f "$agent_target"
    elif [ -f "$agent_target" ]; then
      rm -f "$agent_target"
    fi
    ln -sf "$agent_dir" "$agent_target"
  done

  # Skills → ~/.agents/skills/ (shared with Cursor)
  install_skills "$repo_root" "$HOME/.agents/skills"

  echo "Installed for OpenCode:"
  echo "  ~/.config/opencode/AGENTS.md → dist/AGENTS.md"
  echo "  ~/.config/opencode/agents/ → $(ls "$repo_root"/agents/*.md 2>/dev/null | wc -l | tr -d ' ') agent(s)"
  echo "  ~/.agents/skills/<skill> × $(ls -d "$repo_root"/skills/*/ | wc -l | tr -d ' ')"
}

# ── Cursor ──────────────────────────────────────────────────────────────────────────

install_cursor() {
  local repo_root=$1

  mkdir -p "$HOME/.cursor/rules"

  # Engineering standards → ~/.cursor/rules/engineering-standards.mdc
  ln -sf "$repo_root/dist/engineering-standards.mdc" \
         "$HOME/.cursor/rules/engineering-standards.mdc"

  # Context7 rule → ~/.cursor/rules/context7.mdc
  ln -sf "$repo_root/dist/context7.mdc" \
         "$HOME/.cursor/rules/context7.mdc"

  # Remove stale rule files from previous installs
  local stale
  for stale in \
    "$HOME/.cursor/rules/python-engineering-standards.mdc" \
    "$HOME/.cursor/rules/python-examples.mdc"; do
    if [ -L "$stale" ] || [ -f "$stale" ]; then
      rm -f "$stale"
      echo "  Removed stale: $(basename "$stale")"
    fi
  done

  # Skills → ~/.agents/skills/ (shared with OpenCode)
  install_skills "$repo_root" "$HOME/.agents/skills"

  echo "Installed for Cursor:"
  echo "  ~/.cursor/rules/engineering-standards.mdc → dist/engineering-standards.mdc"
  echo "  ~/.cursor/rules/context7.mdc → dist/context7.mdc"
  echo "  ~/.agents/skills/<skill> × $(ls -d "$repo_root"/skills/*/ | wc -l | tr -d ' ')"
}

main "$@"
