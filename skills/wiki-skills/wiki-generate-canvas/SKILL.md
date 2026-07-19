---
name: wiki-generate-canvas
description: Generate JSON Canvas relationship maps from canonical wiki notes
---

Argument hint: [optional wiki root]

# Generate Wiki Canvas

Use this skill to refresh generated JSON Canvas relationship maps from canonical note metadata and Obsidian wikilinks.

## Contract

- Read canonical notes under `wiki/notes/`.
- Write generated Canvas files under `wiki/canvases/`.
- Treat generated Canvas files as derived artifacts.
- Overwrite prior generated output on refresh.
- Do not preserve arbitrary manual Canvas edits as source of truth.

## Command

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki generate-canvas
```

Run `wiki-audit` after generation.
