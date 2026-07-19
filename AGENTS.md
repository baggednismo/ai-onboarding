# AI Onboarding Project

This repository is a portable LLM harness. Pull it onto a machine, run
`scripts/makesymlinks.sh`, and receive a complete user-root toolkit.

`AGENTS.md` governs this repository only. Any rule or behavior intended for
linked harnesses MUST be added to `AGENTS_SOURCE.md`, not this file.

Codex hook behavior and the CLI/Desktop verification contract are documented
in [CODEX-RULES.md](CODEX-RULES.md); read it when reviewing or changing hooks.

## MUST

- Read `AGENTS_SOURCE.md` when changing shared assets or user-root behavior.
- Keep vendor assets grouped under `governance/`, `skills/`, `hooks/`, or `agents/`.
- Put generated text and files under `artifacts/`.
- Run `scripts/makesymlinks.sh` after changing shared roots or harness mappings.
- Preserve vendor intent while adapting paths to this project's harness roots.

## Vendor Integration

- MUST group each vendor under the immediate child of every applicable harness root: `skills/<vendor>/`, `hooks/<vendor>/`, `agents/<vendor>/`, and `governance/<vendor>-agents.md`.
- MUST rename vendor root `AGENTS.md` files to `governance/<vendor>-agents.md`; reference them from `AGENTS_SOURCE.md` file, never replace this file.
- MUST read `governance/ponytail-agents.md` when changing or using Ponytail assets.
- MUST use this project's harness directories and hook/MCP configuration; adapt vendor paths without changing intended behavior.
- MUST make `scripts/makesymlinks.sh` expose the complete canonical roots at the harness user root.
- MUST keep generated vendor output under `artifacts/`.
- DO NOT install vendor plugins, installers, repository history, benchmarks, tests, or unrelated files unless explicitly required.
- DO NOT flatten, mix, copy, or edit vendor assets in user-root directories.

## DO NOT

- Replace this file or `AGENTS_SOURCE.md` with a vendor `AGENTS.md`.
- Flatten or mix vendor assets.
- Vendor repository history, installers, or unrelated upstream files.
- Edit user-root links directly; change the canonical source here.
