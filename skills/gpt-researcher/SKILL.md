---
name: gpt-researcher
description: Run citation-first research with Codex agents and native web access. Use for planning investigations, gathering sources, fact-checking drafts, and publishing documented reports with local Python token-saving tools and no external LLM or MCP server.
---

# GPT Researcher

Use this skill when the user asks to plan, research, investigate, fact-check,
review, synthesize, or publish a documented report. Codex performs the
reasoning and web research; the bundled Python tool only transforms text.

## Task routing

Classify the request before acting:

- `plan`: create an investigation plan and stop before source gathering.
- `research`: execute the plan and collect citation-bearing source records.
- `review`: audit a draft or claim set against its sources.
- `publish`: synthesize approved evidence into the final report and references.
- `full`: if the user says “research this” without a narrower mode, run
  `plan → research → review → publish`.

If the request names multiple modes, run them in that order. MUST preserve the
same artifact directory across modes.

## Artifact contract

Create `artifacts/research/<slug>/` before any work. MUST write documentation
for every completed mode:

```text
request.md                         # question, audience, constraints, date
plan.md                            # scope, sections, claims, source strategy
sections/<n>-<slug>/raw.json       # raw source records from one section
sections/<n>-<slug>/sources.json   # cleaned and deduplicated records
sections/<n>-<slug>/context.md     # bounded context passed to synthesis
review.md                          # claim-level findings and corrections
report.md                          # final report
references.md                      # deduplicated source list
```

DO keep intermediate files beside the final report so another agent can
resume without reconstructing context. DO use compact records with only
`url`, `title`, and `text`. DO record the current date and research scope in
`request.md`.

DO NOT paste full source documents or drafts into chat when a file can hold
them. DO NOT report a mode complete until its required file exists. DO NOT
overwrite an existing report without reading it and preserving its sources.

## Plan mode

MUST write `request.md` and `plan.md`. The plan MUST define the report
question, exclusions, audience, section list, key claims per section, source
types, freshness requirements, and a stop condition.

DO delegate planning to `gpt-researcher-planner` when available. DO split work
into independent sections. DO choose primary sources before secondary
commentary. DO stop after planning when the user asked only for a plan.

DO NOT research every possible angle. DO NOT create sections that do not
answer the question. DO NOT hide uncertainty or missing source requirements.

## Research mode

MUST read `plan.md` first. MUST research only the assigned section and save
raw records to its `raw.json`. MUST preserve the source URL for every material
claim. MUST use native Codex web/internet access; start a terminal session with
`codex --search` when live search is not already enabled.

DO delegate independent sections to `gpt-researcher-researcher` in parallel.
DO prefer primary, recent, and directly relevant sources. DO use the local
tool after gathering sources:

```bash
python skills/gpt-researcher/scripts/research_tools.py clean \
  --input sections/<n>-<slug>/raw.json \
  --output sections/<n>-<slug>/sources.json
python skills/gpt-researcher/scripts/research_tools.py context \
  --input sections/<n>-<slug>/sources.json \
  --output sections/<n>-<slug>/context.md \
  --max-chars 24000
```

DO use `context.md` for synthesis instead of repeatedly sending raw pages.
DO note failed searches, inaccessible sources, and unresolved claims in the
section documentation.

DO NOT call an LLM from Python. DO NOT add API keys. DO NOT start the upstream
GPT Researcher MCP server. DO NOT treat a search snippet as verified evidence.

## Review mode

MUST read the draft, `sources.json`, and `plan.md` before reviewing. MUST write
`review.md` with one finding per material claim: claim, source, verdict,
confidence, and required correction.

DO delegate to `gpt-researcher-fact-checker`. DO check citation coverage,
source quality, contradictions, stale facts, and claims that exceed the
evidence. DO distinguish “unsupported” from “false”. DO return the draft to
research when a claim lacks adequate evidence.

DO NOT silently rewrite unsupported claims. DO NOT add new facts during review.
DO NOT call a report publishable while high-impact findings remain unresolved.

## Publish mode

MUST read `plan.md`, every cleaned `context.md`, and `review.md` before writing.
MUST write `report.md` with a title, scope note, clear sections, conclusions,
and inline citations. MUST write `references.md` from the cleaned source set:

```bash
python skills/gpt-researcher/scripts/research_tools.py citations \
  --input sections/<n>-<slug>/sources.json \
  --output references.md
```

DO delegate synthesis to `gpt-researcher-editor`. DO preserve uncertainty,
separate evidence from inference, deduplicate references, and keep the report
within the requested audience and length. DO make the final response a short
summary plus the paths to `report.md`, `references.md`, and `review.md`.

DO NOT invent citations. DO NOT cite a source that was not read. DO NOT remove
material caveats merely to make the report sound decisive. DO NOT publish when
the plan, evidence, or review is missing.

## Global rules

MUST keep all generated research files under `artifacts/`. MUST preserve
existing user files and unrelated research runs. MUST report blocked native
web access instead of switching to an unapproved provider.
