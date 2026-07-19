#!/usr/bin/env python3
"""Small, dependency-free source compaction tools for Codex research."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return " ".join(self.parts)


def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    if "<" in value and ">" in value:
        parser = _TextExtractor()
        parser.feed(value)
        value = parser.text()
    return re.sub(r"\s+", " ", value).strip()


def canonical_url(value: str) -> str:
    parts = urlsplit((value or "").strip())
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.query, ""))


def read_json(path: str) -> list[dict]:
    payload = json.load(sys.stdin if path == "-" else Path(path).open())
    if isinstance(payload, dict):
        payload = payload.get("sources", [])
    if not isinstance(payload, list):
        raise ValueError("input must be a JSON list or an object with a sources list")
    return [item for item in payload if isinstance(item, dict)]


def write_json(path: str, payload: object) -> None:
    output = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path == "-":
        sys.stdout.write(output)
    else:
        Path(path).write_text(output)


def normalize(sources: list[dict]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for source in sources:
        url = canonical_url(str(source.get("url") or source.get("href") or ""))
        text = clean_text(str(source.get("text") or source.get("body") or source.get("content") or ""))
        if not url or not text:
            continue
        key = url or hashlib.sha256(text.encode()).hexdigest()
        item = {"url": url, "title": clean_text(str(source.get("title") or url)), "text": text}
        previous = by_key.get(key)
        if previous is None or len(item["text"]) > len(previous["text"]):
            by_key[key] = item
    return list(by_key.values())


def context(sources: list[dict], max_chars: int, per_source: int) -> str:
    parts = ["# Research Context", ""]
    remaining = max_chars
    for index, source in enumerate(sources, 1):
        if remaining <= 0:
            break
        text = source["text"][: min(per_source, remaining)]
        parts.extend((f"## [{index}] {source['title']}", source["url"], "", text, ""))
        remaining -= len(text)
    return "\n".join(parts).rstrip() + "\n"


def citations(sources: list[dict]) -> str:
    return "\n".join(f"[{index}] {source['title']}. {source['url']}" for index, source in enumerate(sources, 1)) + "\n"


def self_check() -> None:
    sample = normalize([{"url": "HTTPS://Example.com/a#one", "title": " A ", "body": "<p>Hello   world</p>"}, {"url": "https://example.com/a", "body": "Hello world and more"}])
    assert len(sample) == 1 and sample[0]["text"] == "Hello world and more"
    assert "[1]" in citations(sample)
    assert len(context(sample, 1000, 100)) < 1000


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("clean", "context", "citations"):
        command = sub.add_parser(name)
        command.add_argument("--input", required=True)
        command.add_argument("--output", default="-")
        if name == "context":
            command.add_argument("--max-chars", type=int, default=24000)
            command.add_argument("--per-source", type=int, default=4000)
    sub.add_parser("self-check")
    args = parser.parse_args()
    if args.command == "self-check":
        self_check()
        return
    sources = normalize(read_json(args.input))
    if args.command == "clean":
        write_json(args.output, sources)
    elif args.command == "context":
        output = context(sources, args.max_chars, args.per_source)
        Path(args.output).write_text(output) if args.output != "-" else sys.stdout.write(output)
    else:
        output = citations(sources)
        Path(args.output).write_text(output) if args.output != "-" else sys.stdout.write(output)


if __name__ == "__main__":
    main()
