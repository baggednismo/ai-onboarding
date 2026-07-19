# GPT Researcher Vendor Guidelines

GPT Researcher is vendored from `assafelovic/gpt-researcher` at commit
`5d84d2f5553e70a2765a8ff3a0d2672d60437ce8` (2026-07-14), under Apache-2.0.
The canonical pack is `skills/gpt-researcher/`: its skill coordinates native
Codex research and its Python script performs deterministic context reduction.

Codex-native agents are authored once under `agents/gpt-researcher/`. The
`scripts/makesymlinks.sh` projection exposes them directly under the Codex
agents root because Codex discovers standalone agent TOML files there. They
use the parent Codex session's available research tools and write intermediate
files under `artifacts/`; they do not call an LLM directly.

The upstream `.mcp.json` is intentionally not enabled. The package currently
does not expose a `uvx gpt-researcher` executable, and this harness uses the
signed-in Codex session rather than an external GPT Researcher MCP server.

The upstream application source, tests, benchmarks, build output, installers,
examples, and repository history are excluded from this pack.
