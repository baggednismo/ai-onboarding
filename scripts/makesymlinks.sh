#!/usr/bin/env bash

set -euo pipefail

SOURCE="${SOURCE:-$HOME/ai-onboarding}"
TARGET="${TARGET:-$HOME/.copilot}"
CODEX_TARGET="${CODEX_TARGET:-${CODEX_HOME:-$HOME/.codex}}"

SOURCE="$(cd "$SOURCE" && pwd -P)"
mkdir -p "$TARGET"

link_file() {
  local source_path="$1"
  local target_path="$2"

  if [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
    echo "refusing to replace non-symlink target: $target_path" >&2
    exit 1
  fi
  rm -f "$target_path"
  ln -s "$source_path" "$target_path"
}

link_file "$SOURCE/AGENTS_SOURCE.md" "$TARGET/AGENTS.md"
link_file "$SOURCE/mcp-config.json" "$TARGET/mcp-config.json"
link_file "$SOURCE/CODEX-RULES.md" "$TARGET/CODEX-RULES.md"
link_file "$SOURCE/governance" "$TARGET/governance"
link_file "$SOURCE/wiki" "$TARGET/wiki"

# Replace the Codex user root with links to this repository's canonical roots.
# Real existing paths are moved aside instead of being silently deleted.
CODEX_BACKUP="$CODEX_TARGET/.ai-onboarding-backups/$(date +%Y%m%d%H%M%S)-$$"

replace_codex_path() {
  local source_path="$1"
  local target_path="$2"

  if [ -e "$target_path" ] || [ -L "$target_path" ]; then
    if [ -L "$target_path" ]; then
      rm -f "$target_path"
    else
      mkdir -p "$CODEX_BACKUP"
      mv "$target_path" "$CODEX_BACKUP/$(basename "$target_path")"
    fi
  fi
  mkdir -p "$(dirname "$target_path")"
  ln -s "$source_path" "$target_path"
}

replace_codex_path "$SOURCE/AGENTS_SOURCE.md" "$CODEX_TARGET/AGENTS.md"
replace_codex_path "$SOURCE/governance" "$CODEX_TARGET/governance"
replace_codex_path "$SOURCE/skills" "$CODEX_TARGET/skills"
replace_codex_path "$SOURCE/hooks" "$CODEX_TARGET/hooks"
replace_codex_path "$SOURCE/hooks/hooks.json" "$CODEX_TARGET/hooks.json"
replace_codex_path "$SOURCE/wiki" "$CODEX_TARGET/wiki"
replace_codex_path "$SOURCE/mcp-config.json" "$CODEX_TARGET/mcp-config.json"
replace_codex_path "$SOURCE/CODEX-RULES.md" "$CODEX_TARGET/CODEX-RULES.md"

# Codex discovers standalone agent TOMLs directly under ~/.codex/agents.
# Keep vendor agents grouped in the canonical repository, then project their
# files at the discovered root without duplicating their contents here.
CODEX_AGENTS_TARGET="$CODEX_TARGET/agents"
CODEX_AGENTS_MARKER="$CODEX_AGENTS_TARGET/.ai-onboarding-managed"
if [ -L "$CODEX_AGENTS_TARGET" ]; then
  rm -f "$CODEX_AGENTS_TARGET"
elif [ -e "$CODEX_AGENTS_TARGET" ] && [ ! -f "$CODEX_AGENTS_MARKER" ]; then
  mkdir -p "$CODEX_BACKUP"
  mv "$CODEX_AGENTS_TARGET" "$CODEX_BACKUP/agents"
fi
mkdir -p "$CODEX_AGENTS_TARGET"
touch "$CODEX_AGENTS_MARKER"

# Remove stale generated links from an earlier projection shape. The marker
# means this directory was created by this script, not supplied by the user.
find "$CODEX_AGENTS_TARGET" -mindepth 1 -maxdepth 1 -type l -exec rm -f {} +

while IFS= read -r -d '' agent_file; do
  link_file "$agent_file" "$CODEX_AGENTS_TARGET/$(basename "$agent_file")"
done < <(find "$SOURCE/agents" -mindepth 2 -maxdepth 2 -type f -name '*.toml' -print0)

# AgentMemory is installed globally and is intentionally not vendored. On
# macOS, expose the repository-owned LaunchAgent so it starts at login and
# remains recoverable from this canonical source.
if [ "$(uname -s)" = "Darwin" ] && [ -f "$SOURCE/launchd/com.agentmemory.agentmemory.plist" ]; then
  LAUNCH_AGENTS_TARGET="${LAUNCH_AGENTS_TARGET:-$HOME/Library/LaunchAgents}"
  mkdir -p "$LAUNCH_AGENTS_TARGET"
  LAUNCH_AGENT_PATH="$LAUNCH_AGENTS_TARGET/com.agentmemory.agentmemory.plist"
  link_file "$SOURCE/launchd/com.agentmemory.agentmemory.plist" "$LAUNCH_AGENT_PATH"

  # Load it now when the explicitly supported global install is present. A
  # later login loads the same plist automatically through launchd.
  if [ -x "/opt/homebrew/bin/agentmemory" ] && command -v launchctl >/dev/null 2>&1; then
    LAUNCH_AGENT_DOMAIN="gui/$(id -u)"
    if launchctl print "$LAUNCH_AGENT_DOMAIN/com.agentmemory.agentmemory" >/dev/null 2>&1; then
      launchctl kickstart -k "$LAUNCH_AGENT_DOMAIN/com.agentmemory.agentmemory"
    else
      launchctl bootstrap "$LAUNCH_AGENT_DOMAIN" "$LAUNCH_AGENT_PATH"
    fi
  fi
fi

# Keep the user-root skill directory usable while preserving its bucketed
# organization in this repository. Each exposed skill points to its source.
if [ -L "$TARGET/skills" ]; then
  rm "$TARGET/skills"
fi
mkdir -p "$TARGET/skills"

while IFS= read -r -d '' skill_md; do
  source_dir="$(dirname "$skill_md")"
  name="$(basename "$source_dir")"
  target_path="$TARGET/skills/$name"

  if [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
    echo "refusing to replace non-symlink skill: $target_path" >&2
    exit 1
  fi
  rm -f "$target_path"
  ln -s "$source_dir" "$target_path"
done < <(find "$SOURCE/skills" -name SKILL.md -not -path '*/node_modules/*' -print0)
