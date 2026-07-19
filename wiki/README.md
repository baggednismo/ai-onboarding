# Obsidian Wiki

This directory is the repository's Obsidian vault root. It stays intentionally small, but new canonical wiki content now lives as linked Obsidian notes.

## Structure

- `templates/` defines the supported note shapes.
- `raw/` stores durable source inputs for later ingest. Existing raw files are not edited by wiki automation.
- `notes/` holds canonical notes.
- `notes/topics/` holds synthesized durable knowledge.
- `notes/sources/` holds provenance notes for ingested sources.
- `notes/projects/` holds durable project context when needed.
- `bases/` holds generated Obsidian Bases definitions.
- `canvases/` holds generated JSON Canvas maps.

## Required notes

- `notes/overview.md`
- `notes/index.md`
- `notes/log.md`

## Supported note types

- `entry`
- `topic`
- `source`
- `project`

## Workflow

1. Place or identify durable source material in `raw/`.
2. Run `wiki-ingest` for one source at a time, passing `--project` and `--project-number` for project-related documents when known.
3. Run `wiki-normalize` to repair metadata, wikilinks, and generated sections.
4. Run `wiki-audit` to validate vault health.
5. Run `wiki-generate-bases` and `wiki-generate-canvas`.
6. Run `wiki-audit` again before treating the update as complete.

The old lightweight wiki notes can remain as reference material while the Obsidian flow is solidified. Fresh ingest from `raw/` should produce the new canonical note shape.
