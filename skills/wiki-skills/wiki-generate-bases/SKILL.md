---
name: wiki-generate-bases
description: Generate Obsidian Bases definitions from canonical wiki note metadata
---

Argument hint: [optional wiki root]

# Generate Obsidian Bases

Use this skill to refresh generated Bases definitions from canonical note metadata. The generated files are committed artifacts, but note metadata remains the source of truth.

## Contract

- Read canonical notes under `wiki/notes/`.
- Write generated Bases under `wiki/bases/`.
- Generate topic, source, and project views.
- Make output deterministic and reviewable.
- Do not hand-edit generated Bases as canonical source.

## Command

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki generate-bases
```

Run `wiki-audit` after generation.
