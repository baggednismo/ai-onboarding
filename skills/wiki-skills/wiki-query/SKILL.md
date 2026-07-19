---
name: wiki-query
description: Query the Obsidian wiki with index-first retrieval and evidence-bounded answers
---

Argument hint: [question or topic]

# Query the Obsidian Wiki

Answer questions from canonical Obsidian notes by reading `wiki/notes/index.md` first, then drilling into the smallest relevant set of topic, source, project, or entry notes. In consuming environments, treat `wiki/` as the primary surface and fall back to `~/.copilot/wiki` when the workspace does not expose it.

## Variables

- `CANONICAL_ROOT = {resolved wiki root}/notes`
- `INDEX_FILE = CANONICAL_ROOT/index.md`
- `OVERVIEW_FILE = CANONICAL_ROOT/overview.md`
- `LOG_FILE = CANONICAL_ROOT/log.md`

## Workflow

1. Resolve the wiki root from `./wiki` first and `~/.copilot/wiki` second.
2. Read `wiki/AGENTS.md`, `INDEX_FILE`, and `OVERVIEW_FILE`.
3. Retrieve only the canonical notes needed to answer the question.
4. For project-specific questions, search `notes/projects/` by title, ID, and `project_number` before broadening to linked topics or sources.
5. Prefer `notes/projects/`, `notes/topics/`, and `notes/sources/` over `raw/`.
6. If raw material seems relevant but no canonical note exists, report it as an ingest opportunity unless the user explicitly asks to inspect raw sources.
7. Cite exact canonical note paths for every substantive claim.

## Guardrails

- Start from `notes/index.md`.
- Keep answers evidence-bounded.
- Do not silently create or modify wiki notes during query mode.
- Do not treat test-era content under `wiki/wiki/` as the primary retrieval surface for the new Obsidian model.
