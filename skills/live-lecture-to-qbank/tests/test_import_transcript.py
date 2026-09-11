import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "import_transcript.py"

class ImportTranscriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name); self.out = self.root / "out"
    def tearDown(self): self.temp.cleanup()
    def run_import(self, name, content, suffix, identity="entry-1", source_kind="live"):
        source = self.root / (name + suffix); source.write_text(content, encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--course", "OST520", "--unit", "UE2", "--lecture-title", "Live", "--source-identity", identity, "--recording-date", "2026-09-10", "--source-kind", source_kind, "--output-root", str(self.out)], text=True, capture_output=True)
    def index(self): return json.loads((self.out / "OST520" / "UE2" / "index.json").read_text())
    def test_vtt_multiline_and_repeat_is_unchanged(self):
        content = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nalpha\nbeta\n\nchapter-two\n00:00:02.000 --> 00:00:04.000\ngamma\n\nNOTE editor note\nignored\n\nSTYLE\n::cue { color: white; }\n"
        first = self.run_import("a", content, ".vtt"); self.assertEqual(first.returncode, 0)
        again = self.run_import("b", content, ".vtt"); self.assertEqual(json.loads(again.stdout)["status"], "unchanged")
        body = next((self.out / "OST520" / "UE2").rglob("normalized.txt")).read_text(); self.assertIn("[00:00:01.000] alpha beta", body)
    def test_revision_and_unrelated_recording_are_isolated(self):
        self.assertEqual(self.run_import("one", "first", ".txt").returncode, 0); self.assertEqual(self.run_import("two", "changed", ".txt").returncode, 0)
        self.assertEqual(self.run_import("three", "other", ".txt", "entry-2").returncode, 0); entries = self.index()["entries"]
        self.assertEqual(len(entries["entry-1"]["content_versions"]), 2); self.assertEqual(len(entries["entry-2"]["content_versions"]), 1)
        reverted = self.run_import("four", "first", ".txt"); self.assertEqual(json.loads(reverted.stdout)["status"], "revised")
        self.assertEqual(len(self.index()["entries"]["entry-1"]["content_versions"]), 3)
    def test_raw_variant_skips_question_work_and_safe_names_do_not_collide(self):
        self.assertEqual(self.run_import("base", "same", ".txt", "a/b").returncode, 0)
        variant = self.run_import("variant", "same\n", ".txt", "a/b"); self.assertEqual(json.loads(variant.stdout)["downstream"], "skip_unchanged_normalized")
        self.assertEqual(self.run_import("other", "different", ".txt", "a b").returncode, 0)
        paths = [v["normalized_path"] for e in self.index()["entries"].values() for v in e["content_versions"]]
        self.assertEqual(len(paths), len(set(paths)))
    def test_same_byte_identity_metadata_conflict_is_rejected(self):
        self.assertEqual(self.run_import("one", "first", ".txt").returncode, 0)
        conflict = self.run_import("two", "first", ".txt", source_kind="prerecorded")
        self.assertNotEqual(conflict.returncode, 0); self.assertEqual(len(self.index()["entries"]["entry-1"]["content_versions"]), 1)
    def test_srt_and_plain_text_locators(self):
        self.assertEqual(self.run_import("s", "1\n00:00:01,000 --> 00:00:02,000\nfirst\nsecond\n", ".srt").returncode, 0)
        self.assertEqual(self.run_import("p", "paragraph one\n\nparagraph two", ".txt", "plain").returncode, 0); entries = self.index()["entries"]
        self.assertEqual(entries["plain"]["content_versions"][0]["locator_type"], "paragraph")
    def test_timestamped_text_export_keeps_caption_locators(self):
        inline = "# MediaSpace visible transcript\n# Captions: 2\n\n[00:00] DENNIS: Hello\n[00:03] This continues\n"
        self.assertEqual(self.run_import("timestamped", inline, ".txt", "caption-text", "prerecorded").returncode, 0)
        version = self.index()["entries"]["caption-text"]["content_versions"][0]
        self.assertEqual(version["locator_type"], "timestamp"); self.assertIn("[00:00]", (self.out / "OST520" / "UE2" / version["normalized_path"]).read_text())
    def test_historical_media_space_fixture_when_available(self):
        fixture = Path("/Users/austin_cheng/Desktop/MSUCOM/26 Fall/OST 520/_outputs/transcripts/timestamped/026__OST520 (035) L Bacterial structure - Arvidson.timestamped.txt")
        if not fixture.exists(): self.skipTest("historical MediaSpace archive is unavailable on this host")
        source = self.root / fixture.name; shutil.copyfile(fixture, source)
        result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--course", "OST520", "--unit", "UE2", "--lecture-title", "Bacterial structure", "--source-identity", "historical-026", "--recording-date", "2026-08-27", "--source-kind", "prerecorded", "--output-root", str(self.out)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr); version = self.index()["entries"]["historical-026"]["content_versions"][0]
        self.assertEqual(version["locator_type"], "timestamp"); self.assertIn("[00:00]", (self.out / "OST520" / "UE2" / version["normalized_path"]).read_text())
    def test_empty_and_bad_captions_do_not_create_index(self):
        self.assertNotEqual(self.run_import("empty", "", ".txt").returncode, 0); self.assertFalse((self.out / "OST520" / "UE2" / "index.json").exists())
        self.assertNotEqual(self.run_import("bad", "00:61:00 --> 00:62:00\nnope", ".vtt").returncode, 0); self.assertFalse((self.out / "OST520" / "UE2" / "index.json").exists())

if __name__ == "__main__": unittest.main()
