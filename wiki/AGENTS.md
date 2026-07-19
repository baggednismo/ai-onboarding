# Wiki AGENTS

## Purpose

This directory is the Obsidian vault root for durable AI wiki content. Keep it small, source-first, template-driven, and usable both by Obsidian and by LLM retrieval workflows.

## Directory roles

- `templates/` - source templates for supported note types
- `raw/` - durable input material for ingest; existing raw files are read-only
- `notes/` - canonical Obsidian-facing notes
- `notes/topics/` - synthesized durable knowledge
- `notes/sources/` - provenance notes for ingested raw sources
- `notes/projects/` - durable project context when needed
- `bases/` - generated Obsidian Bases definitions
- `canvases/` - generated JSON Canvas relationship maps
- `wiki/` - test-era lightweight wiki content; not part of required migration for the Obsidian flow

## Wiki rules

- `wiki/` is the vault root.
- Canonical notes for new work live under `notes/`.
- The wiki is for durable project and shared context, not scratch notes.
- Search canonical notes first for project-related context across this repo, linked environment projects, project documentation, and durable reports.
- Prefer a small required note set over a broad knowledge base.
- Avoid duplicate notes that describe the same concept.
- Update existing canonical notes in place when the truth changes.
- Keep entries concise and high-signal.
- Fall back to raw material, repo scans, or external project locations only when canonical notes lack the needed answer or the user explicitly asks for those sources.

## Note contract

- Every canonical note must have frontmatter.
- Required fields are `id`, `type`, `title`, and `status`.
- `id` is the filename stem and the canonical Obsidian link target.
- Supported `type` values are `entry`, `topic`, `source`, and `project`.
- Project notes may include `project_number` when a durable external project identifier exists.
- Relationships use Obsidian wikilinks in frontmatter and note bodies, such as `[[policy-manager]]`.
- Automation may edit frontmatter and marked generated regions only.
- The generated relationship region is bounded by `<!-- WIKI:GENERATED:RELATIONSHIPS:START -->` and `<!-- WIKI:GENERATED:RELATIONSHIPS:END -->`.

## When to update the wiki

Update the relevant canonical note or generated artifact when a change affects:

- shared structure, project structure, or durable asset locations
- root operating rules or governance expectations
- platform guidance that changes how teams should build
- wiki templates or supported note types
- shared skills, prompts, agents, or their maintenance model
- wiki-first search behavior or the scope of projects and artifacts the wiki is expected to cover

## How to update the wiki

1. Pick the note type that matches the change.
2. Start from the matching template in `templates/`.
3. Update canonical notes in `notes/`, not `raw/`.
4. Replace outdated guidance in the same change that introduces the new truth.
5. Run normalize and audit before treating broad wiki updates as complete.

For project-related ingest, pass `--project` and `--project-number` when known so source notes, topic notes, and project notes are linked during ingest.

Use `chat-source.tempalate.md` for Teams or similar chat-log ingest when the canonical record should preserve a factual narrative rather than transcript-shaped notes.

## Guardrails

- Do not turn the wiki into a large documentation dump.
- Do not preserve stale statements just for history.
- Do not create ad hoc note shapes when a template should govern the content.
- Do not edit existing files under `raw/`; raw files are source inputs.
- Do not hand-edit generated Bases or Canvas output as source of truth.
