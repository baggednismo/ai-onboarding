#!/usr/bin/env bash

# Resolve Node for the symlinked Codex harness without changing Impeccable's
# hook behavior. A missing runtime must not break the agent turn.
set -u

node_bin=""
if [ -n "${IMPECCABLE_NODE:-}" ] && [ -x "$IMPECCABLE_NODE" ]; then
  node_bin="$IMPECCABLE_NODE"
elif command -v node >/dev/null 2>&1; then
  node_bin="$(command -v node)"
elif [ -x "/Applications/Codex.app/Contents/Resources/cua_node/bin/node" ]; then
  node_bin="/Applications/Codex.app/Contents/Resources/cua_node/bin/node"
fi

[ -n "$node_bin" ] || exit 0

codex_root="${CODEX_HOME:-$HOME/.codex}"
exec "$node_bin" "$codex_root/skills/impeccable/scripts/hook.mjs"
