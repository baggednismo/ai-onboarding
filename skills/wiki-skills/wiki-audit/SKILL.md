---
name: wiki-audit
description: Audit the Obsidian wiki for metadata, link, relationship, and generated artifact health
---

Argument hint: [optional wiki root]

# Audit the Obsidian Wiki

Use this skill before or after ingest, normalization, Bases generation, or Canvas generation to validate externally visible vault behavior.

## Contract

- Target the fresh Obsidian model under `wiki/notes/`, `wiki/bases/`, and `wiki/canvases/`.
- Treat `wiki/raw/` as source input only.
- Report failures loudly with actionable file context.
- Do not auto-fix during audit.

## Command

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki audit
```

## Audit surface

The audit checks:

- required vault paths
- required frontmatter fields
- supported note types
- broken frontmatter wikilinks
- broken body wikilinks
- missing generated relationship sections
- stale topic, source, and project Bases files
- stale generated Canvas file

Generated artifact freshness is checked after the Bases and Canvas generators run.
