# Codex Rules

This file is the project-local reference for Codex lifecycle hooks and the
Ponytail hook integration. It records both intended behavior and operational
constraints discovered during review.

Vendor additions must update this document with their hook events, discovered
configuration locations, executable/runtime requirements, trust steps, and
symlinked roots. The `vendor-skills` skill owns that onboarding workflow.

## Hook discovery and registration

- Codex discovers hooks from `~/.codex/hooks.json`, inline `[[hooks.EVENT]]`
  tables in `~/.codex/config.toml`, project-local `.codex/hooks.json` or
  `.codex/config.toml`, and enabled plugin hook manifests or
  `hooks/hooks.json` files.
- Files nested under `~/.codex/hooks/` are not discovered merely because they
  exist. The canonical Ponytail definition at
  `hooks/ponytail/claude-codex-hooks.json` must be copied or merged into an
  actually discovered Codex hook source.
- This harness keeps that discovered source at `hooks/hooks.json`; the
  symlink script exposes it as `~/.codex/hooks.json`. Add future vendor hook
  groups to this aggregate using the vendor merge rules below.
- Keep one hook representation per config layer. If a layer contains both
  `hooks.json` and inline `[hooks]`, Codex merges them and warns.
- Hooks are enabled by default. If disabling or explicitly enabling them,
  use `[features].hooks`; `codex_hooks` is only a deprecated alias.
- Non-managed hooks must be reviewed and trusted before execution. Use `/hooks`
  in CLI, or the equivalent hook management UI in Desktop, after installing or
  changing a hook. Trust is tied to the hook definition hash, so changes
  require review again.

## Ponytail Codex behavior

The Codex hook definition should register these handlers:

- `SessionStart` for `startup`, `resume`, `clear`, and `compact`, running
  `ponytail-activate.js`.
- `SubagentStart`, running `ponytail-subagent.js` so spawned agents receive
  the active ruleset.
- `UserPromptSubmit`, running `ponytail-mode-tracker.js` so `/ponytail`,
  `/ponytail lite`, `/ponytail full`, `/ponytail ultra`, `/ponytail off`,
  `stop ponytail`, and `normal mode` update the active mode.

The scripts use `PONYTAIL_CODEX=1` and write the live mode to
`$CODEX_HOME/.ponytail-active` (defaulting to `~/.codex/.ponytail-active`).
The default mode is resolved in this order:

1. `PONYTAIL_DEFAULT_MODE`
2. `XDG_CONFIG_HOME/ponytail/config.json`, or the platform fallback config
3. `full`

`off`, `lite`, `full`, and `ultra` are runtime modes. `review` is a
session-only mode and must not be used as a persisted default.

### Vendored Ponytail surface

- Vendor skills live under `skills/ponytail/`; the MIT license and harness
  adapters live under `hooks/ponytail/`.
- The vendor hook contract is `SessionStart`, `SubagentStart`, and
  `UserPromptSubmit`, with the original definition retained at
  `hooks/ponytail/claude-codex-hooks.json`.
- This repository's symlink install exposes the canonical aggregate
  `hooks/hooks.json` as `~/.codex/hooks.json`; that is the discovered Codex
  registration point. It preserves the vendor's three event groups while
  resolving scripts from the linked `$CODEX_HOME/hooks/ponytail` directory.
- The aggregate invokes `ponytail-node.sh`. It preserves the vendor's
  Node-based behavior, preferring `PONYTAIL_NODE`, then `node` on PATH, then
  the installed Codex app's bundled Node. If no Node runtime exists, it exits
  quietly so the six Ponytail skills remain available without lifecycle
  activation, matching the vendor's documented fallback behavior.
- After a hook definition or script changes, Codex must review and trust the
  current hook hash through `/hooks`, then start a new thread. Desktop must be
  restarted when its Codex runtime needs to reload the projected config.

## Impeccable Codex behavior

Impeccable is vendored from `pbakaus/impeccable` at commit
`e4ab5e24bdf5321b72163d2fbcbe6fa985c848ba` (release `3.9.1`, Apache-2.0).
Its generated Codex payload is canonical at `skills/impeccable/` and includes
the `SKILL.md`, 32 reference files, 69 support scripts, OpenAI metadata, and
two nested Codex subagents. Codex discovers those subagents from the skill's
own `agents/` directory; they must not be duplicated under the top-level
`agents/` root.

The vendor's upstream project-local hook is retained at
`hooks/impeccable/upstream-codex-hooks.json` for provenance. This harness
merges its `PostToolUse` handler into the discovered canonical aggregate at
`hooks/hooks.json`. The aggregate invokes
`hooks/impeccable/impeccable-node.sh`, which resolves Node from
`IMPECCABLE_NODE`, PATH, or the Codex Desktop bundled runtime, then runs the
linked `~/.codex/skills/impeccable/scripts/hook.mjs`.

The Impeccable hook listens to `PostToolUse` for `Edit`, `Write`, and
`apply_patch`, reads event JSON from stdin, runs the UI anti-pattern detector
against the touched file, emits findings through
`hookSpecificOutput.additionalContext`, and always exits successfully so a
detector failure cannot break the agent turn. It has a five-second timeout and
may write an audit log when configured.

Impeccable's generated skill instructions use `.agents/skills/impeccable` in
the upstream Codex repo-install form. This repository adapts those command
paths to the canonical `.codex/skills/impeccable` projection, so the skill
works after `scripts/makesymlinks.sh` for this user's Codex CLI and Desktop
installations. Do not copy the upstream `.codex` directory into the user root
or edit the projected links directly.

After installing or changing Impeccable, review and trust the aggregate hook
again through `/hooks`; trust is hash-based. Verify both the hook wrapper and
the linked script with representative PostToolUse stdin, and start a fresh
thread after trust/config changes. If Desktop has a reduced PATH, the bundled
Node fallback or an explicit `IMPECCABLE_NODE` path is required.

## GPT Researcher Codex behavior

GPT Researcher is remastered as a Codex-native pack under
`skills/gpt-researcher/`, with custom agents under `agents/gpt-researcher/`.
`scripts/makesymlinks.sh` projects those TOML files directly into the Codex
agents root for discovery. The agents use the parent Codex session's available
web/internet tools and write research artifacts under `artifacts/`. The bundled
`research_tools.py` script only cleans, deduplicates, bounds, and formats text;
it never calls an LLM.

The canonical `mcp-config.json` deliberately contains no GPT Researcher
server. Do not add provider API keys or enable the upstream `.mcp.json` for
this workflow. If native web access is unavailable in a Codex surface, report
that limitation rather than silently switching to an external retriever.

## AgentMemory external integration

AgentMemory is installed globally, not vendored into this repository. The
current install is `@agentmemory/agentmemory` `0.9.28`, with package root
`/opt/homebrew/lib/node_modules/@agentmemory/agentmemory` and runtime data under
`~/.agentmemory`.

The canonical `hooks/hooks.json` manually merges AgentMemory's six Codex hook
events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`,
`PreCompact`, and `Stop`. They invoke the local adapter
`hooks/agentmemory-node.sh`, which executes the corresponding scripts from the
global package without copying AgentMemory into this repository. The adapter
supports `AGENTMEMORY_NODE` and `AGENTMEMORY_PACKAGE_ROOT` overrides, then
falls back to PATH, Homebrew Node, or Codex Desktop's bundled Node.

Do not run `agentmemory connect codex` for this harness: it may edit the Codex
configuration and bypass the repository's canonical aggregate. Run
`scripts/makesymlinks.sh` after hook changes so `~/.codex/hooks.json` remains a
projection of this file. The AgentMemory server must be running at its
documented default `http://localhost:3111` for capture and recall hooks to
reach the full service; its hooks fail open when the server is unavailable.
Optional context injection remains controlled by AgentMemory's documented
`AGENTMEMORY_INJECT_CONTEXT` setting and is not enabled by this repository.

On macOS, `launchd/com.agentmemory.agentmemory.plist` is the canonical user
LaunchAgent. `scripts/makesymlinks.sh` links it to
`~/Library/LaunchAgents/com.agentmemory.agentmemory.plist`; it runs AgentMemory
from `~/.agentmemory`, starts it at login, and keeps it alive after a crash.
This avoids creating service data in a repository working directory. The
LaunchAgent uses the Homebrew executable at `/opt/homebrew/bin/agentmemory`;
if Node or Homebrew is installed elsewhere, update the canonical plist or set
up the machine's equivalent installation before running the link script.
Installing the global npm package alone does not create this startup item.

The global hooks apply to every Codex project through the projected
`~/.codex/hooks.json`; a new repository does not need a local AgentMemory
install. Run this repository's `scripts/makesymlinks.sh` on a new machine,
keep the AgentMemory service running, and review/trust the changed hooks in
Codex. AgentMemory derives the active project from the session working
directory, so a new repository is captured automatically once Codex can run
its hooks. The optional native AgentMemory MCP tools are a separate concern:
this harness deliberately has not run `agentmemory connect codex`, so they are
not added to the existing Codex `config.toml` automatically.

## Command and runtime requirements

- Hook commands receive one JSON object on stdin. Hook scripts must consume
  stdin without blocking and exit successfully when there is no applicable
  work.
- `SessionStart` and `SubagentStart` match thread/subagent startup scope;
  `UserPromptSubmit` runs at turn scope. Codex currently ignores matchers on
  `UserPromptSubmit`.
- Codex accepts JSON hook output using `systemMessage` and
  `hookSpecificOutput.additionalContext`. `SubagentStart` uses the same
  hook-specific context shape.
- Model-visible hook context is limited to roughly 2,500 tokens per entry.
  Keep injected rules concise and do not emit secrets.
- Hook commands run with the session working directory. Resolve shared
  scripts from stable absolute paths rather than assuming the current
  directory.
- Vendor hooks may require Node. This harness's Ponytail aggregate uses
  `hooks/ponytail/ponytail-node.sh`, which resolves `PONYTAIL_NODE`, then
  `node` on PATH, then the installed Codex app's bundled Node, and otherwise
  exits quietly so skills still work without lifecycle activation. This
  machine now provides Node at `/opt/homebrew/bin/node`; the bundled-app
  fallback remains for Desktop environments with a reduced PATH.
- Validate hook JSON, JavaScript syntax, executable paths, and representative
  stdin/output cases after every hook change.

## Scope boundaries

- `hooks/ponytail/claude-codex-hooks.json` is Codex-specific. The neighboring
  `copilot-hooks.json` and `qoder-hooks.json` are reference configurations for
  other harnesses and are not Codex registrations.
- TOML files under `hooks/ponytail/commands/` are Ponytail command definitions;
  their presence under the hooks directory does not automatically register
  them as Codex slash commands.
- The repository is canonical. Change hook sources here, then run
  `scripts/makesymlinks.sh` when shared-root mappings change. Do not edit the
  `~/.codex/hooks` symlink or linked files directly.

## Vendor pack contract

- Place each vendor under the immediate child of every applicable canonical
  root: `skills/<vendor>/`, `hooks/<vendor>/`, `agents/<vendor>/`, and
  `governance/<vendor>-agents.md`.
- Preserve vendor intent and licenses while excluding upstream history,
  installers, benchmarks, tests, build output, and unrelated files.
- Dedupe identical files and merge conflicting structured configuration by
  key. Preserve local changes and never silently overwrite a conflict.
- Keep Codex hook registration in a location Codex discovers; a file nested
  under `~/.codex/hooks/` is not registration by itself.
- Update `scripts/makesymlinks.sh` for new shared roots or user-root mappings,
  expose `CODEX-RULES.md`, and test the script twice against isolated targets
  to verify links, backups, and idempotence.
- Record each vendor's hook surface, runtime executable requirements,
  configuration files, trust/review steps, and verification results here.

## Verification checklist

Before reporting Codex hook support as working:

- Confirm a discovered root/config/plugin hook source exists.
- Confirm `/hooks` lists the expected handlers and trust each current hash.
- Confirm the configured Node command resolves in both CLI and Desktop.
- Start a new session and verify Ponytail activation output.
- Submit `/ponytail ultra`, then verify the mode file and prompt output.
- Spawn a subagent and verify it receives Ponytail context.
- Repeat the smoke test in both Codex CLI and Desktop when cross-surface
  behavior matters.
