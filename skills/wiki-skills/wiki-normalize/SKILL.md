---
name: wiki-normalize
description: Normalize Obsidian wiki note metadata, wikilinks, and generated sections
---

Argument hint: [optional wiki root]

# Normalize the Obsidian Wiki

Use this skill after ingest or manual note edits to repair the canonical Obsidian note shape.

## Contract

- Target canonical notes under `wiki/notes/`.
- Do not target test-era content under `wiki/wiki/`.
- Do not edit files under `wiki/raw/`.
- Automation may update frontmatter and marked generated regions.
- Manual body content outside generated regions must be preserved.

## Command

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki normalize
```

## Checks

Normalization should:

- add missing required frontmatter
- infer note type from the note path when needed
- use filename stems as canonical IDs
- rewrite markdown note links into Obsidian wikilinks
- refresh generated relationship sections
- preserve manual prose outside frontmatter and generated regions

Run `wiki-audit` after normalization.
