---
name: vendor-skills
description: Vendor a complete external AI skill pack into this repository's canonical harness, preserving vendor intent while deduplicating existing skills, agents, governance, hooks, configuration, and symlink mappings. Use when importing, onboarding, mirroring, or updating a vendor skill pack similar to Ponytail or Matt Pocock's skills, especially when hooks or Codex/Desktop/CLI configuration is included.
---

# Vendor Skill Pack

Vendor packs into the repository's canonical roots. Treat the repository as
the source of truth; user-root directories are projections created by
`scripts/makesymlinks.sh`.

## Required context

Before inspecting or editing vendor files, read:

1. `CODEX-RULES.md`
2. `AGENTS.md`
3. `governance/ponytail-agents.md` when Ponytail assets are involved
4. The relevant `wiki/` notes and existing vendor directories

`CODEX-RULES.md` is authoritative for hook discovery, Codex input/output,
trust, Node resolution, and verification. Update it whenever the imported
pack introduces or changes hooks, agents, commands, plugins, or symlinked
roots.

## Workflow

### 1. Inventory the pack

Identify the source, vendor name, version or commit, license, and every asset
category. Inspect before copying. Include only the pack's reusable assets:

- skills and their `SKILL.md` files
- agents and UI metadata
- hooks and lifecycle configuration
- vendor governance or root instructions
- commands, references, scripts, and required support files

Exclude repository history, installers, benchmarks, tests, build output,
examples, and unrelated upstream files unless the user explicitly requests
them. Record the source and version in the vendor governance note or the
durable artifact requested by the repository.

### 2. Map into canonical roots

Use the immediate vendor child required by this harness:

```text
skills/<vendor>/
hooks/<vendor>/
agents/<vendor>/
governance/<vendor>-agents.md
```

Keep the vendor's internal structure beneath that boundary. Rename an
upstream root `AGENTS.md` to `governance/<vendor>-agents.md`; reference it
from `AGENTS_SOURCE.md` instead of replacing this repository's instructions.
Place generated reports or manifests under `artifacts/`.

### 3. Dedupe, then merge

Compare the proposed tree with all existing canonical roots before writing.

- Identical files: retain one canonical copy and do not duplicate it.
- Same behavior under different names: reuse the existing asset when the
  vendor license and intent permit it; otherwise retain the vendor file and
  document the relationship.
- Same path with different content: inspect both versions and merge the
  smallest complete result. Preserve existing local changes, vendor intent,
  license notices, and user-authored rules. Never silently overwrite a
  conflict.
- Structured files: parse and merge objects/tables by key. For hook maps,
  merge event groups and deduplicate handlers by event, matcher, type, and
  command. Preserve distinct handlers even when they share an event.
- Markdown instructions: co-locate related rules, remove exact duplicates,
  and keep one authoritative statement. Reference shared rules instead of
  copying them.
- Symlinks: compare resolved targets and link intent before replacing them.
  Preserve real files by moving them to the script's backup area; never
  delete an unresolved or unrelated user file.

If a conflict cannot be safely merged without choosing between incompatible
behaviors, stop with the exact paths and ask for direction.

### 4. Wire Codex and other surfaces

For Codex hooks, ensure the configuration is in a discovered location from
`CODEX-RULES.md`. A JSON file buried under `~/.codex/hooks/` is not enough.
Use a canonical root hook registration or an enabled plugin hook manifest;
do not rely on a vendor file merely existing in the hooks directory.

Check every command for:

- stable absolute or repository-root-resolved paths
- a Node/Python/shell executable available to both CLI and Desktop
- stdin consumption and bounded execution
- valid Codex event names, matchers, and JSON output
- hook trust/review requirements
- output size and secret handling

Keep Claude, Copilot, Qoder, and Codex configurations separate unless the
vendor explicitly defines a compatible shared contract. Do not make a
foreign harness configuration look like a Codex registration.

### 5. Update the symlink projection

When the pack adds or changes a shared root, hook registration, agent source,
governance file, or Codex rules file, update `scripts/makesymlinks.sh` rather
than editing user-root files directly. The script must:

- expose the complete canonical roots at the configured Codex target
- expose `CODEX-RULES.md` when Codex needs the shared rules document
- preserve existing real files through its backup path
- refuse to replace non-symlink skill targets silently
- avoid flattening vendors or mixing vendor files into other vendors
- make repeated runs idempotent

Prefer a small general mapping change over a vendor-specific workaround. If
hook registration requires a generated aggregate, make its source and merge
rule explicit and keep the generated result under the repository's canonical
configuration surface.

### 6. Verify before handoff

Run the smallest complete check set:

1. Validate every changed JSON, TOML, YAML, and `SKILL.md`.
2. Run `skills/.system/skill-creator/scripts/quick_validate.py` on this skill.
3. Run `scripts/makesymlinks.sh` against an isolated temporary target for both
   Copilot and Codex projections; inspect links and backups.
4. Run it a second time and confirm no new changes are produced.
5. Confirm the projected `AGENTS.md`, `CODEX-RULES.md`, skills, agents,
   governance, hooks, and MCP mappings resolve to the canonical source.
6. For hooks, run representative stdin/output smoke tests and confirm the
   configured executable resolves in CLI and Desktop environments.
7. Report source/version, files added or merged, symlink changes, tests,
   unresolved conflicts, and anything requiring `/hooks` trust.

Completion means every imported asset has a canonical destination, every
conflict is resolved or explicitly reported, the symlink script passes the
isolated idempotence test, and `CODEX-RULES.md` describes the new vendor
surface.
