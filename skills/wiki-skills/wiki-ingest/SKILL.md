---
name: wiki-ingest
description: Ingest one durable raw source into Obsidian wiki source and topic notes
---

Argument hint: [physical source file or natural-language ingest request] [optional --topic "Topic Name"] [optional --project "Project Name"] [optional --project-number "Project Number"]

# Ingest a Wiki Source

Use this skill when one durable source should become canonical Obsidian wiki notes. The workflow is source-first: raw material stays in `wiki/raw/`, source notes record provenance, and topic notes hold durable synthesized knowledge.

## Contract

- Resolve the wiki root from `./wiki` first and `~/.copilot/wiki` second.
- Treat `wiki/` as the Obsidian vault root.
- Treat `wiki/raw/` as read-only source material.
- Create or update canonical notes under `wiki/notes/`.
- Do not migrate or normalize test-era content under `wiki/wiki/`.
- Ingest one source at a time.

## Command

From the repository root or a workspace that exposes the shared wiki:

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki ingest "wiki/raw/path/to/source.md" --topic "Topic Name"
```

To associate the source with an active project, pass the project name and project number when known:

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki ingest "wiki/raw/path/to/source.md" --topic "Topic Name" --project "Project Name" --project-number "Project Number"
```

If the script is not available in a downstream tool home, run it from the source repository and point `--wiki-root` at the visible wiki root.

## Argument normalization

Before running the command, normalize the user request into explicit CLI arguments:

- Treat an existing file path as the ingest source.
- If no source path is provided, search `wiki/raw/` for files matching the project/topic words. Use the match only when there is exactly one clear candidate; otherwise ask which source file to ingest.
- Extract project numbers from phrases like `project #12345678ABC`, `project 12345678ABC`, `project-number 12345678ABC`, or `project number 12345678ABC`.
- Treat the words before `project` as the project name when no explicit `--project` is supplied.
- Default `--topic` to the project name when a project name is inferred and no explicit topic is supplied.
- Preserve explicit flags over inferred values.

Example:

```text
wiki ingest policy manager project #12345678ABC
```

Normalize to:

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki ingest "<resolved raw source>" --topic "Policy Manager" --project "Policy Manager" --project-number "12345678ABC"
```

## Process

1. Read `wiki/AGENTS.md`, `wiki/README.md`, and the targeted source file.
2. Confirm the target is a physical source when possible.
3. Prefer source files under `wiki/raw/`; fixture files outside `raw/` are only for tests or dry runs.
4. Run the ingest command.
5. Review the created or updated source note and topic note.
6. If `--project` or `--project-number` was supplied, review the created or updated project note.
7. Run `wiki-normalize`, `wiki-audit`, `wiki-generate-bases`, and `wiki-generate-canvas` as needed.

## Output

Report:

- source note created or updated
- topic note created or updated
- project note created or updated, when project metadata was supplied
- raw source used
- durable facts that still need manual synthesis
- any open questions

## Guardrails

- Never edit existing files under `wiki/raw/`.
- Do not preserve raw transcript or document dump shapes as canonical notes.
- Do not create broad note taxonomies before the source demands them.
- Keep generated regions clearly marked.
