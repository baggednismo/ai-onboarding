#!/usr/bin/env bash

# Resolve Node for the symlinked Codex harness without changing Ponytail's
# behavior. Missing Node is intentionally a quiet no-op: the skills remain
# available, while lifecycle activation is skipped as in the vendor install.
set -u

script_name="${1:-}"
if [ -z "$script_name" ]; then
  exit 0
fi
shift

node_bin=""
if [ -n "${PONYTAIL_NODE:-}" ] && [ -x "$PONYTAIL_NODE" ]; then
  node_bin="$PONYTAIL_NODE"
elif command -v node >/dev/null 2>&1; then
  node_bin="$(command -v node)"
elif [ -x "/Applications/Codex.app/Contents/Resources/cua_node/bin/node" ]; then
  node_bin="/Applications/Codex.app/Contents/Resources/cua_node/bin/node"
fi

[ -n "$node_bin" ] || exit 0

hook_root="${CODEX_HOME:-$HOME/.codex}/hooks/ponytail"
exec "$node_bin" "$hook_root/$script_name" "$@"
