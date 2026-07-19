#!/usr/bin/env bash

# Local adapter for the globally installed AgentMemory package.
# AgentMemory itself is intentionally not vendored in this repository.
set -u

script_name="${1:-}"
case "$script_name" in
  session-start.mjs|prompt-submit.mjs|pre-tool-use.mjs|post-tool-use.mjs|pre-compact.mjs|stop.mjs) ;;
  *) exit 0 ;;
esac

node_bin=""
if [ -n "${AGENTMEMORY_NODE:-}" ] && [ -x "$AGENTMEMORY_NODE" ]; then
  node_bin="$AGENTMEMORY_NODE"
elif command -v node >/dev/null 2>&1; then
  node_bin="$(command -v node)"
elif [ -x "/opt/homebrew/bin/node" ]; then
  node_bin="/opt/homebrew/bin/node"
elif [ -x "/Applications/Codex.app/Contents/Resources/cua_node/bin/node" ]; then
  node_bin="/Applications/Codex.app/Contents/Resources/cua_node/bin/node"
fi

[ -n "$node_bin" ] || exit 0

package_root="${AGENTMEMORY_PACKAGE_ROOT:-/opt/homebrew/lib/node_modules/@agentmemory/agentmemory}"
script_path="$package_root/plugin/scripts/$script_name"
[ -f "$script_path" ] || exit 0

exec "$node_bin" "$script_path"
