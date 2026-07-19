#!/usr/bin/env python3
"""Obsidian wiki maintenance commands for the repository wiki."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


GENERATED_START = "<!-- WIKI:GENERATED:RELATIONSHIPS:START -->"
GENERATED_END = "<!-- WIKI:GENERATED:RELATIONSHIPS:END -->"
DOC_TYPES = {"entry", "topic", "source", "project"}
NOTE_DIRS = {
    "topic": Path("notes/topics"),
    "source": Path("notes/sources"),
    "project": Path("notes/projects"),
}


@dataclass
class Note:
    path: Path
    meta: dict[str, object]
    body: str

    @property
    def identifier(self) -> str:
        return str(self.meta.get("id") or self.path.stem)

    @property
    def note_type(self) -> str:
        return str(self.meta.get("type") or infer_type(self.path))

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or title_from_slug(self.path.stem))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled"


def title_from_slug(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("_", "-").split("-") if part) or "Untitled"


def wiki_link(identifier: str, title: str | None = None) -> str:
    clean_id = identifier.strip("[]")
    if title and title_from_slug(clean_id) != title:
        return f"[[{clean_id}|{title}]]"
    return f"[[{clean_id}]]"


def parse_link_id(value: object) -> str:
    text = str(value)
    match = re.match(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", text)
    return match.group(1) if match else text


def append_link(meta: dict[str, object], field: str, identifier: str) -> None:
    values = meta.get(field)
    values = values if isinstance(values, list) else []
    link = wiki_link(identifier)
    if link not in values:
        values.append(link)
    meta[field] = values


def project_id_for(project: str | None, project_number: str | None) -> str | None:
    if project_number:
        return f"project-{slugify(project_number)}"
    if project:
        return slugify(project)
    return None


def ensure_vault(root: Path) -> None:
    for rel in [
        "raw",
        "notes/topics",
        "notes/sources",
        "notes/projects",
        "bases",
        "canvases",
        "templates",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def infer_type(path: Path) -> str:
    parts = set(path.parts)
    if "topics" in parts:
        return "topic"
    if "sources" in parts:
        return "source"
    if "projects" in parts:
        return "project"
    return "entry"


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].splitlines()
    body = text[end + 5 :]
    meta: dict[str, object] = {}
    current: str | None = None
    for line in raw:
        if not line.strip():
            continue
        if line.startswith("  - ") and current:
            meta.setdefault(current, [])
            if isinstance(meta[current], list):
                meta[current].append(line[4:].strip().strip('"'))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            current = key
            if not value:
                meta[key] = []
            elif value in {"[]", "null"}:
                meta[key] = [] if value == "[]" else ""
            else:
                meta[key] = value.strip('"')
    return meta, body


def dump_frontmatter(meta: dict[str, object]) -> str:
    order = [
        "id",
        "type",
        "title",
        "status",
        "project_number",
        "source_path",
        "topics",
        "sources",
        "projects",
        "related",
        "created",
        "updated",
    ]
    keys = [key for key in order if key in meta] + sorted(key for key in meta if key not in order)
    lines = ["---"]
    for key in keys:
        value = meta[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def read_note(path: Path) -> Note:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    return Note(path=path, meta=meta, body=body)


def write_note(note: Note) -> None:
    note.path.parent.mkdir(parents=True, exist_ok=True)
    note.path.write_text(dump_frontmatter(note.meta) + note.body.lstrip(), encoding="utf-8")


def entry_body(title: str) -> str:
    purposes = {
        "Index": "Lightweight index of canonical wiki notes, starting with project and topic notes created through source ingest.",
        "Log": "Operational log entry point for durable wiki updates and source ingests.",
        "Overview": "Top-level entry point for the durable Obsidian wiki and its canonical notes.",
    }
    return f"# {title}\n\n## Purpose\n\n{purposes.get(title, 'Canonical wiki entry point.')}\n"


def append_entry_link(root: Path, identifier: str, title: str, target_id: str) -> None:
    path = root / "notes" / f"{identifier}.md"
    today = date.today().isoformat()
    if path.exists():
        note = read_note(path)
    else:
        note = Note(
            path=path,
            meta={
                "id": identifier,
                "type": "entry",
                "title": title,
                "status": "active",
                "related": [],
                "created": today,
                "updated": today,
            },
            body=entry_body(title),
        )
    append_link(note.meta, "related", target_id)
    write_note(normalize_note(note))


def update_ingest_entry_points(root: Path, source_id: str, topic_id: str, project_id: str | None) -> None:
    append_entry_link(root, "index", "Index", project_id or topic_id)
    append_entry_link(root, "log", "Log", source_id)


def notes(root: Path) -> list[Note]:
    note_root = root / "notes"
    if not note_root.exists():
        return []
    return [read_note(path) for path in sorted(note_root.rglob("*.md"))]


def note_index(root: Path) -> dict[str, Note]:
    return {note.identifier: note for note in notes(root)}


def generated_relationship_section(note: Note) -> str:
    structured_fields = ["topics", "sources", "projects"]
    related_values = note.meta.get("related")
    lines = [GENERATED_START, "## Related"]
    if not any(isinstance(note.meta.get(field), list) and note.meta.get(field) for field in structured_fields):
        if isinstance(related_values, list) and related_values:
            lines.append("")
            for value in related_values:
                link_id = parse_link_id(value)
                lines.append(f"- {wiki_link(link_id)}")
            lines.append(GENERATED_END)
            return "\n".join(lines) + "\n"

    fields = structured_fields + ["related"]
    found = False
    for field in fields:
        values = note.meta.get(field)
        if isinstance(values, list) and values:
            found = True
            lines.append("")
            lines.append(f"### {field.capitalize()}")
            for value in values:
                link_id = parse_link_id(value)
                lines.append(f"- {wiki_link(link_id)}")
    if not found:
        lines.append("")
        lines.append("No related notes recorded.")
    lines.append(GENERATED_END)
    return "\n".join(lines) + "\n"


def refresh_generated_section(body: str, section: str) -> str:
    pattern = re.compile(
        re.escape(GENERATED_START) + r".*?" + re.escape(GENERATED_END) + r"\n?",
        re.DOTALL,
    )
    if pattern.search(body):
        return pattern.sub(section, body)
    stripped = body.rstrip()
    return (stripped + "\n\n" if stripped else "") + section


def normalize_markdown_links(body: str) -> str:
    pattern = re.compile(r"\[([^\]]+)\]\((?:\.\./)*(?:notes/)?(?:topics/|sources/|projects/)?([^)\/]+)\.md\)")

    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        identifier = Path(match.group(2)).stem
        return wiki_link(identifier, label)

    return pattern.sub(replace, body)


def normalize_note(note: Note) -> Note:
    today = date.today().isoformat()
    identifier = slugify(str(note.meta.get("id") or note.path.stem))
    note_type = str(note.meta.get("type") or infer_type(note.path))
    if note_type not in DOC_TYPES:
        note_type = infer_type(note.path)
    title_match = re.search(r"^#\s+(.+)$", note.body, re.MULTILINE)
    title = str(note.meta.get("title") or (title_match.group(1).strip() if title_match else title_from_slug(identifier)))
    note.meta.update(
        {
            "id": identifier,
            "type": note_type,
            "title": title,
            "status": str(note.meta.get("status") or "active"),
            "updated": today,
        }
    )
    note.meta.setdefault("created", today)
    for field in ["topics", "sources", "projects", "related"]:
        value = note.meta.get(field)
        if value is None:
            continue
        if not isinstance(value, list):
            value = [str(value)]
        note.meta[field] = [wiki_link(parse_link_id(item)) for item in value if str(item).strip()]
    if not re.search(r"^#\s+", note.body, re.MULTILINE):
        note.body = f"# {title}\n\n" + note.body.lstrip()
    note.body = normalize_markdown_links(note.body)
    note.body = refresh_generated_section(note.body, generated_relationship_section(note))
    return note


def readable_excerpt(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except UnicodeDecodeError:
        return []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[:5]


def command_contract(args: argparse.Namespace) -> int:
    root = Path(args.wiki_root)
    ensure_vault(root)
    print(json.dumps({"vault_root": str(root), "notes": "notes", "raw": "raw", "bases": "bases", "canvases": "canvases"}))
    return 0


def command_ingest(args: argparse.Namespace) -> int:
    root = Path(args.wiki_root)
    ensure_vault(root)
    source = Path(args.source)
    if not source.exists():
        print(f"source does not exist: {source}", file=sys.stderr)
        return 2
    raw_root = (root / "raw").resolve()
    before = source.read_bytes()
    source_id = slugify(args.id or source.stem)
    source_title = args.title or title_from_slug(source_id)
    topic_id = slugify(args.topic or source_id)
    topic_title = args.topic_title or title_from_slug(topic_id)
    project_id = project_id_for(args.project, args.project_number)
    project_title = args.project or topic_title
    rel_source = source.resolve().relative_to(root.resolve()) if source.resolve().is_relative_to(root.resolve()) else source.resolve()
    excerpt = readable_excerpt(source)

    source_meta = {
        "id": source_id,
        "type": "source",
        "title": source_title,
        "status": "active",
        "source_path": rel_source,
        "topics": [wiki_link(topic_id)],
        "created": date.today().isoformat(),
        "updated": date.today().isoformat(),
    }
    if project_id:
        source_meta["projects"] = [wiki_link(project_id)]
    source_note = Note(
        path=root / "notes/sources" / f"{source_id}.md",
        meta=source_meta,
        body=(
            f"# {source_title}\n\n"
            "## What it is\n\n"
            f"Durable source ingested from `{rel_source}`.\n\n"
            "## Key facts\n\n"
            + ("\n".join(f"- {line}" for line in excerpt) if excerpt else "- Source requires manual extraction.")
            + "\n"
        ),
    )
    write_note(normalize_note(source_note))

    topic_path = root / "notes/topics" / f"{topic_id}.md"
    if topic_path.exists():
        topic_note = read_note(topic_path)
        append_link(topic_note.meta, "sources", source_id)
    else:
        topic_note = Note(
            path=topic_path,
            meta={
                "id": topic_id,
                "type": "topic",
                "title": topic_title,
                "status": "active",
                "sources": [wiki_link(source_id)],
                "created": date.today().isoformat(),
                "updated": date.today().isoformat(),
            },
            body=(
                f"# {topic_title}\n\n"
                "## Summary\n\n"
                f"- Source-derived topic created from {wiki_link(source_id)}.\n"
            ),
        )
    write_note(normalize_note(topic_note))

    project_path: Path | None = None
    if project_id:
        project_path = root / "notes/projects" / f"{project_id}.md"
        if project_path.exists():
            project_note = read_note(project_path)
            project_note.meta.setdefault("title", project_title)
            if args.project_number and not project_note.meta.get("project_number"):
                project_note.meta["project_number"] = args.project_number
            append_link(project_note.meta, "topics", topic_id)
            append_link(project_note.meta, "sources", source_id)
        else:
            project_meta = {
                "id": project_id,
                "type": "project",
                "title": project_title,
                "status": "active",
                "topics": [wiki_link(topic_id)],
                "sources": [wiki_link(source_id)],
                "created": date.today().isoformat(),
                "updated": date.today().isoformat(),
            }
            if args.project_number:
                project_meta["project_number"] = args.project_number
            project_note = Note(
                path=project_path,
                meta=project_meta,
                body=(
                    f"# {project_title}\n\n"
                    "## Summary\n\n"
                    f"Project context linked from {wiki_link(source_id)}.\n"
                ),
            )
        write_note(normalize_note(project_note))

    if source.resolve().is_relative_to(raw_root) and source.read_bytes() != before:
        print(f"raw source was modified: {source}", file=sys.stderr)
        return 3
    update_ingest_entry_points(root, source_id, topic_id, project_id)
    payload = {"source_note": str(source_note.path), "topic_note": str(topic_path)}
    if project_path:
        payload["project_note"] = str(project_path)
    print(json.dumps(payload))
    return 0


def command_normalize(args: argparse.Namespace) -> int:
    root = Path(args.wiki_root)
    ensure_vault(root)
    changed: list[str] = []
    for note in notes(root):
        original = note.path.read_text(encoding="utf-8")
        normalized = normalize_note(note)
        rendered = dump_frontmatter(normalized.meta) + normalized.body.lstrip()
        if rendered != original:
            normalized.path.write_text(rendered, encoding="utf-8")
            changed.append(str(normalized.path))
    print(json.dumps({"changed": changed}))
    return 0


def relationships(root: Path) -> list[tuple[str, str, str]]:
    edges: list[tuple[str, str, str]] = []
    for note in notes(root):
        for field in ["topics", "sources", "projects", "related"]:
            values = note.meta.get(field)
            if isinstance(values, list):
                for value in values:
                    edges.append((note.identifier, parse_link_id(value), field))
    return sorted(set(edges))


def bases_content(root: Path, note_type: str) -> str:
    folders = {"topic": "topics", "source": "sources", "project": "projects"}
    folder = folders[note_type]
    return "\n".join(
        [
            "filters:",
            "  and:",
            f"    - file.inFolder(\"notes/{folder}\")",
            f"    - type == \"{note_type}\"",
            "views:",
            "  - type: table",
            f"    name: {title_from_slug(folder)}",
            "    order:",
            "      - title",
            "      - status",
            "      - updated",
            "",
        ]
    )


def command_generate_bases(args: argparse.Namespace) -> int:
    root = Path(args.wiki_root)
    ensure_vault(root)
    outputs = []
    for note_type, filename in [("topic", "topics.base"), ("source", "sources.base"), ("project", "projects.base")]:
        path = root / "bases" / filename
        path.write_text(bases_content(root, note_type), encoding="utf-8")
        outputs.append(str(path))
    print(json.dumps({"bases": outputs}))
    return 0


def canvas_content(root: Path) -> dict[str, object]:
    current_notes = sorted(notes(root), key=lambda item: item.identifier)
    nodes = []
    columns = {"entry": 0, "source": 1, "topic": 2, "project": 3}
    for index, note in enumerate(current_notes):
        nodes.append(
            {
                "id": note.identifier,
                "type": "file",
                "file": str(note.path.relative_to(root)),
                "x": columns.get(note.note_type, 4) * 360,
                "y": index * 140,
                "width": 300,
                "height": 100,
            }
        )
    known = {note.identifier for note in current_notes}
    edges = []
    for source_id, target_id, label in relationships(root):
        if source_id in known and target_id in known:
            edges.append(
                {
                    "id": f"{source_id}-{label}-{target_id}",
                    "fromNode": source_id,
                    "toNode": target_id,
                    "label": label,
                }
            )
    return {"nodes": nodes, "edges": edges}


def command_generate_canvas(args: argparse.Namespace) -> int:
    root = Path(args.wiki_root)
    ensure_vault(root)
    path = root / "canvases" / "knowledge-map.canvas"
    path.write_text(json.dumps(canvas_content(root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"canvas": str(path)}))
    return 0


def audit_findings(root: Path) -> list[str]:
    findings: list[str] = []
    for rel in ["raw", "notes/topics", "notes/sources", "notes/projects", "bases", "canvases"]:
        if not (root / rel).exists():
            findings.append(f"missing required path: {rel}")
    current = notes(root)
    index = {note.identifier: note for note in current}
    for note in current:
        for key in ["id", "type", "title", "status"]:
            if not note.meta.get(key):
                findings.append(f"{note.path}: missing {key}")
        if note.note_type not in DOC_TYPES:
            findings.append(f"{note.path}: invalid type {note.note_type}")
        for field in ["topics", "sources", "projects", "related"]:
            values = note.meta.get(field)
            if isinstance(values, list):
                for value in values:
                    target = parse_link_id(value)
                    if target not in index:
                        findings.append(f"{note.path}: broken {field} link {value}")
        for target in re.findall(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", note.body):
            if target not in index:
                findings.append(f"{note.path}: broken body link [[{target}]]")
        if GENERATED_START not in note.body or GENERATED_END not in note.body:
            findings.append(f"{note.path}: missing generated relationship section")
    expected_bases = {
        root / "bases/topics.base": bases_content(root, "topic"),
        root / "bases/sources.base": bases_content(root, "source"),
        root / "bases/projects.base": bases_content(root, "project"),
    }
    for path, expected in expected_bases.items():
        if not path.exists():
            findings.append(f"{path}: missing generated Bases file")
        elif path.read_text(encoding="utf-8") != expected:
            findings.append(f"{path}: stale generated Bases file")
    canvas_path = root / "canvases/knowledge-map.canvas"
    expected_canvas = json.dumps(canvas_content(root), indent=2, sort_keys=True) + "\n"
    if not canvas_path.exists():
        findings.append(f"{canvas_path}: missing generated Canvas file")
    elif canvas_path.read_text(encoding="utf-8") != expected_canvas:
        findings.append(f"{canvas_path}: stale generated Canvas file")
    return findings


def command_audit(args: argparse.Namespace) -> int:
    root = Path(args.wiki_root)
    findings = audit_findings(root)
    if findings:
        print(json.dumps({"status": "failed", "findings": findings}, indent=2))
        return 1
    print(json.dumps({"status": "healthy", "findings": []}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki-root", default="wiki", help="Path to the Obsidian wiki vault root")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("contract").set_defaults(func=command_contract)
    ingest = sub.add_parser("ingest")
    ingest.add_argument("source")
    ingest.add_argument("--id")
    ingest.add_argument("--title")
    ingest.add_argument("--topic")
    ingest.add_argument("--topic-title")
    ingest.add_argument("--project")
    ingest.add_argument("--project-number")
    ingest.set_defaults(func=command_ingest)
    sub.add_parser("normalize").set_defaults(func=command_normalize)
    sub.add_parser("audit").set_defaults(func=command_audit)
    sub.add_parser("generate-bases").set_defaults(func=command_generate_bases)
    sub.add_parser("generate-canvas").set_defaults(func=command_generate_canvas)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
