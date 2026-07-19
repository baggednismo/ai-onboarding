import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "obsidian_wiki.py"


def run_cli(*args, cwd=ROOT, check=True):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result


class ObsidianWikiCliTests(unittest.TestCase):
    def test_contract_scaffolds_expected_vault_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            result = run_cli("--wiki-root", str(wiki), "contract")
            payload = json.loads(result.stdout)

            self.assertEqual(payload["notes"], "notes")
            for rel in [
                "raw",
                "notes/topics",
                "notes/sources",
                "notes/projects",
                "bases",
                "canvases",
                "templates",
            ]:
                self.assertTrue((wiki / rel).is_dir(), rel)

    def test_ingest_creates_source_and_topic_without_mutating_raw(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            raw = wiki / "raw"
            raw.mkdir(parents=True)
            source = raw / "Policy Manager.md"
            source.write_text("Policy manager durable fact\nSecond fact\n", encoding="utf-8")
            before = source.read_text(encoding="utf-8")

            run_cli("--wiki-root", str(wiki), "ingest", str(source), "--topic", "Policy Manager")

            self.assertEqual(source.read_text(encoding="utf-8"), before)
            source_note = wiki / "notes/sources/policy-manager.md"
            topic_note = wiki / "notes/topics/policy-manager.md"
            self.assertIn("type: source", source_note.read_text(encoding="utf-8"))
            self.assertIn("[[policy-manager]]", source_note.read_text(encoding="utf-8"))
            self.assertIn("type: topic", topic_note.read_text(encoding="utf-8"))
            self.assertIn("[[policy-manager]]", topic_note.read_text(encoding="utf-8"))

    def test_ingest_links_source_topic_and_project(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            raw = wiki / "raw"
            raw.mkdir(parents=True)
            source = raw / "Policy Manager Phase 2.md"
            source.write_text("Policy manager durable fact\n", encoding="utf-8")
            before = source.read_text(encoding="utf-8")

            result = run_cli(
                "--wiki-root",
                str(wiki),
                "ingest",
                str(source),
                "--topic",
                "Policy Manager",
                "--project",
                "Policy Manager",
                "--project-number",
                "PM-2048",
            )
            payload = json.loads(result.stdout)

            self.assertEqual(source.read_text(encoding="utf-8"), before)
            self.assertEqual(payload["project_note"], str(wiki / "notes/projects/project-pm-2048.md"))

            source_text = (wiki / "notes/sources/policy-manager-phase-2.md").read_text(encoding="utf-8")
            topic_text = (wiki / "notes/topics/policy-manager.md").read_text(encoding="utf-8")
            project_text = (wiki / "notes/projects/project-pm-2048.md").read_text(encoding="utf-8")

            self.assertIn("projects:", source_text)
            self.assertIn("[[project-pm-2048]]", source_text)
            self.assertIn("sources:", topic_text)
            self.assertIn("[[policy-manager-phase-2]]", topic_text)
            self.assertIn("type: project", project_text)
            self.assertIn("title: Policy Manager", project_text)
            self.assertIn("project_number: PM-2048", project_text)
            self.assertIn("[[policy-manager]]", project_text)
            self.assertIn("[[policy-manager-phase-2]]", project_text)

    def test_ingest_updates_index_and_log_entry_points(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            notes = wiki / "notes"
            notes.mkdir(parents=True)
            (notes / "index.md").write_text(
                "---\nid: index\ntype: entry\ntitle: Index\nstatus: active\nrelated:\n"
                "  - [[overview]]\ncreated: 2026-05-13\nupdated: 2026-05-13\n---\n\n"
                "# Index\n\n## Purpose\n\nEntry point.\n",
                encoding="utf-8",
            )
            (notes / "log.md").write_text(
                "---\nid: log\ntype: entry\ntitle: Log\nstatus: active\nrelated:\n"
                "  - [[overview]]\ncreated: 2026-05-13\nupdated: 2026-05-13\n---\n\n"
                "# Log\n\n## Purpose\n\nEntry point.\n",
                encoding="utf-8",
            )
            raw = wiki / "raw"
            raw.mkdir(parents=True)
            source = raw / "Policy Manager Phase 2.md"
            source.write_text("Policy manager durable fact\n", encoding="utf-8")

            run_cli(
                "--wiki-root",
                str(wiki),
                "ingest",
                str(source),
                "--topic",
                "Policy Manager",
                "--project",
                "Policy Manager",
            )

            index_text = (notes / "index.md").read_text(encoding="utf-8")
            log_text = (notes / "log.md").read_text(encoding="utf-8")

            self.assertIn("[[policy-manager]]", index_text)
            self.assertIn("[[policy-manager-phase-2]]", log_text)
            self.assertIn("<!-- WIKI:GENERATED:RELATIONSHIPS:START -->", index_text)
            self.assertIn("<!-- WIKI:GENERATED:RELATIONSHIPS:START -->", log_text)

    def test_normalize_preserves_manual_content_and_rewrites_links(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            note_dir = wiki / "notes/topics"
            note_dir.mkdir(parents=True)
            (note_dir / "linked.md").write_text("# Linked\n", encoding="utf-8")
            note = note_dir / "demo.md"
            note.write_text("# Demo\n\nManual paragraph with [Linked](linked.md).\n", encoding="utf-8")

            run_cli("--wiki-root", str(wiki), "normalize")

            text = note.read_text(encoding="utf-8")
            self.assertIn("Manual paragraph", text)
            self.assertIn("[[linked]]", text)
            self.assertIn("<!-- WIKI:GENERATED:RELATIONSHIPS:START -->", text)

    def test_audit_fails_on_broken_wikilink_and_passes_after_target_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            note_dir = wiki / "notes/topics"
            note_dir.mkdir(parents=True)
            (note_dir / "demo.md").write_text(
                "---\nid: demo\ntype: topic\ntitle: Demo\nstatus: active\n---\n\n# Demo\n\n[[missing]]\n"
                "<!-- WIKI:GENERATED:RELATIONSHIPS:START -->\n## Related\n\nNo related notes recorded.\n"
                "<!-- WIKI:GENERATED:RELATIONSHIPS:END -->\n",
                encoding="utf-8",
            )

            failed = run_cli("--wiki-root", str(wiki), "audit", check=False)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("broken body link", failed.stdout)

            (note_dir / "missing.md").write_text("# Missing\n", encoding="utf-8")
            run_cli("--wiki-root", str(wiki), "normalize")
            run_cli("--wiki-root", str(wiki), "generate-bases")
            run_cli("--wiki-root", str(wiki), "generate-canvas")
            passed = run_cli("--wiki-root", str(wiki), "audit")
            self.assertIn("healthy", passed.stdout)

    def test_generators_are_deterministic_and_overwrite_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            raw = wiki / "raw"
            raw.mkdir(parents=True)
            source = raw / "Source.md"
            source.write_text("Fact\n", encoding="utf-8")
            run_cli("--wiki-root", str(wiki), "ingest", str(source), "--topic", "Demo Topic")

            run_cli("--wiki-root", str(wiki), "generate-bases")
            run_cli("--wiki-root", str(wiki), "generate-canvas")
            bases_first = (wiki / "bases/topics.base").read_text(encoding="utf-8")
            self.assertTrue((wiki / "bases/projects.base").is_file())
            canvas_path = wiki / "canvases/knowledge-map.canvas"
            canvas_first = canvas_path.read_text(encoding="utf-8")
            canvas_path.write_text("manual drift", encoding="utf-8")

            run_cli("--wiki-root", str(wiki), "generate-bases")
            run_cli("--wiki-root", str(wiki), "generate-canvas")

            self.assertEqual((wiki / "bases/topics.base").read_text(encoding="utf-8"), bases_first)
            self.assertEqual(canvas_path.read_text(encoding="utf-8"), canvas_first)
            canvas = json.loads(canvas_first)
            self.assertIn("nodes", canvas)
            self.assertIn("edges", canvas)

    def test_audit_reports_stale_generated_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            wiki = Path(temp) / "wiki"
            raw = wiki / "raw"
            raw.mkdir(parents=True)
            source = raw / "Source.md"
            source.write_text("Fact\n", encoding="utf-8")
            run_cli("--wiki-root", str(wiki), "ingest", str(source), "--topic", "Demo Topic")
            run_cli("--wiki-root", str(wiki), "generate-bases")
            run_cli("--wiki-root", str(wiki), "generate-canvas")

            (wiki / "bases/topics.base").write_text("drift", encoding="utf-8")
            failed = run_cli("--wiki-root", str(wiki), "audit", check=False)

            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("stale generated Bases file", failed.stdout)


if __name__ == "__main__":
    unittest.main()
