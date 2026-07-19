# AI Toolkit

Personal source of truth for reusable AI assistant assets and working guidance.

## Contents

- `AGENTS.md` - this project's operating rules
- `AGENTS_SOURCE.md` - shared instructions linked into user roots
- `governance/` - engineering baseline and assistant behavior
- `skills/` - reusable skills
- `skills/ponytail/` - Ponytail's six skills
- `hooks/ponytail/` - Ponytail's hooks and harness-specific hook configuration
- `hooks/agentmemory-node.sh` - adapter for the global AgentMemory install
- `launchd/` - repository-owned macOS startup configuration for AgentMemory
- `agents/` - reusable agent prompts
- `artifacts/` - generated specs, research, domain docs, and local tickets
- `wiki/` - lightweight durable notes and templates
- `mcp-config.json` - local MCP configuration

## Use

Keep shared assets here. Edit them in place rather than maintaining copies in tool-specific directories. Generated output belongs under `artifacts/`.

Link the toolkit into the user roots with `scripts/makesymlinks.sh`. This
replaces the Codex user-root shared directories with links to this project.
Ponytail hooks prefer Node.js on the user-root PATH. The Codex projection also
falls back to the installed Codex app's bundled Node and quietly skips
lifecycle activation when no Node runtime is available; the skills remain
usable.

Upstream skills retain Matt Pocock's buckets under `skills/engineering/`, `skills/productivity/`, `skills/misc/`, `skills/personal/`, and `skills/in-progress/`. Local-only skills remain at the top level.

The wiki is the first place to look for durable project context. Keep it small and update it when shared rules or structure change.

## Vendor quickstarts

Ponytail — set the coding mode before work and change it only when needed:

```text
/ponytail full
...work...
/ponytail off
```

Impeccable — load project context, then run the smallest relevant UI command:

```bash
node .codex/skills/impeccable/scripts/context.mjs
$impeccable audit
```

GPT Researcher — use the skill for integration guidance or run its MCP server:

```text
$gpt-researcher
uvx gpt-researcher
```

AgentMemory — project the hooks, confirm the service, and approve changed hooks:

```bash
scripts/makesymlinks.sh
agentmemory status
curl -fsS http://localhost:3111/agentmemory/health
```

## AgentMemory setup

AgentMemory is an optional global memory service. It is deliberately not
vendored into this repository. The canonical hook aggregate records AgentMemory
events, while the npm package and its runtime data remain in the user account.

### What you need to download

Install these prerequisites before running the setup:

- [Node.js 20 or newer](https://nodejs.org/en/download/). AgentMemory requires
  Node.js `>=20`; verify with `node --version`.
- [Homebrew](https://brew.sh/) is recommended on macOS. The checked-in
  LaunchAgent targets the Apple Silicon Homebrew path
  `/opt/homebrew/bin/agentmemory`; Intel Macs or non-Homebrew installs must
  update the canonical plist before running the link script.
- [AgentMemory](https://github.com/rohitg00/agentmemory), installed globally
  with npm:

  ```bash
  npm install -g @agentmemory/agentmemory
  ```

  If npm cannot find Node or reports a permissions error, fix the Node/npm
  installation first. Avoid installing a second copy into this repository.
- [Codex CLI/Desktop](https://openai.com/codex/get-started/), if Codex is not
  already installed on the machine.

The upstream installation notes are available in the
[AgentMemory installation runbook](https://raw.githubusercontent.com/rohitg00/agentmemory/main/INSTALL_FOR_AGENTS.md).
The first AgentMemory start may also install its `iii-engine` runtime under
`~/.agentmemory/bin`; see the [iii documentation](https://iii.dev/docs) for
that runtime.

### Install this toolkit and enable AgentMemory

From the cloned repository, run:

```bash
cd /path/to/ai-onboarding
scripts/makesymlinks.sh
```

On macOS, this does all of the following:

1. Projects the canonical hooks to `~/.codex/hooks.json` and
   `~/.codex/hooks/`.
2. Links the repository-owned
   `launchd/com.agentmemory.agentmemory.plist` to
   `~/Library/LaunchAgents/com.agentmemory.agentmemory.plist`.
3. Loads or restarts the LaunchAgent when
   `/opt/homebrew/bin/agentmemory` exists.

The LaunchAgent starts AgentMemory when you log in and restarts it if it
crashes. It runs from `~/.agentmemory`, so service data is not written into a
repository. The current configuration uses these local endpoints:

| Endpoint | Purpose |
| --- | --- |
| `http://localhost:3111` | REST API and hook service |
| `http://localhost:3111/agentmemory/health` | Health check |
| `http://localhost:3113` | Live memory viewer |
| `ws://localhost:3112` | Event streams |
| `ws://localhost:49134` | iii engine bridge |

Verify the installation with:

```bash
node --version
npm --version
agentmemory --version
curl -fsS http://localhost:3111/agentmemory/health
open http://localhost:3113
```

The default install works without an API key using BM25 and on-device
embeddings. To enable LLM compression and summaries, create
`~/.agentmemory/.env` and add one supported provider key, for example:

```dotenv
ANTHROPIC_API_KEY=your-key-here
```

Restart AgentMemory after changing `.env`. Keep secrets in `~/.agentmemory`;
never commit them to this repository. The optional
`AGENTMEMORY_INJECT_CONTEXT=true` setting is intentionally disabled by this
harness because it injects memory into prompts.

### Approve the Codex hooks

After the first install or any hook change:

1. Open Codex CLI and run `/hooks`.
2. Review and trust the changed hook definition.
3. Start a new thread. Restart Codex Desktop if it has not reloaded the
   projected configuration.

The hooks fail open when AgentMemory is unavailable, so Codex remains usable
while the service is stopped. You can inspect the service with:

```bash
agentmemory status
agentmemory doctor
launchctl print "gui/$(id -u)/com.agentmemory.agentmemory"
```

Stop or start the service manually when needed:

```bash
agentmemory stop --force
scripts/makesymlinks.sh
```

### Using AgentMemory in a new repository

No AgentMemory files need to be copied into a new repository. The projected
global Codex hooks apply to every project, and AgentMemory associates events
with the current repository based on Codex's working directory. The new
repository only needs to be trusted by Codex and opened after the global hooks
have been installed.

This setup intentionally does not run `agentmemory connect codex`. That command
can edit the existing `~/.codex/config.toml` and add AgentMemory's native MCP
server, which would bypass this repository's canonical configuration. In the
current setup, lifecycle capture and recall hooks are enabled; native
AgentMemory MCP tools are not. If those tools are required later, merge the
AgentMemory MCP entry into the existing Codex configuration manually without
replacing other MCP servers, then document the change in `CODEX-RULES.md`.

For machine-specific paths, set `AGENTMEMORY_NODE` or
`AGENTMEMORY_PACKAGE_ROOT` for the hook adapter, or update the canonical
LaunchAgent plist before running `scripts/makesymlinks.sh`.
