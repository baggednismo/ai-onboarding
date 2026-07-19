---
name: wiki-lint
description: Legacy alias for auditing the Obsidian wiki
---

# Wiki Lint

`wiki-lint` is retained as a compatibility entry point. For the Obsidian wiki model, prefer `wiki-audit`.

Run:

```bash
python3 scripts/obsidian_wiki.py --wiki-root wiki audit
```

The audit targets `wiki/notes/`, `wiki/bases/`, and `wiki/canvases/`. It does not mutate `wiki/raw/` and does not require migration of test-era content under `wiki/wiki/`.
