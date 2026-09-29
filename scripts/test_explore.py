import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from explore import build
from explore import document
from check import DEFAULT_PATHS, RULES


class ExplorerTest(unittest.TestCase):
    def test_snapshot_scores_and_safe_embedding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "guide.md"
            output = root / "explorer.html"
            source.write_text('---\ntitle: "</script><script>unsafe()</script>"\n'
                              'calls: ["PRIVATE_PROVENANCE"]\n---\n\n'
                              '<!-- PRIVATE_REVIEW -->\n\nRead; edit. Then; check.\n')
            data = build([source], output)
            doc = data["documents"][0]
            self.assertEqual(doc["failed"], [11])
            self.assertEqual(doc["score"], len(RULES) - 1)
            html = output.read_text()
            self.assertNotIn("PRIVATE_PROVENANCE", html)
            self.assertNotIn("PRIVATE_REVIEW", html)
            self.assertNotIn("</script><script>unsafe()", html)
            embedded = re.search(r'<script type="application/json" id="data">(.*?)</script>', html, re.S)[1]
            self.assertEqual(json.loads(embedded), json.loads(json.dumps(data)))
            self.assertEqual(doc["blocks"][0]["line"], 8)
            self.assertTrue(doc["uri"].startswith("file:///"))

    def test_default_paths_use_only_bundled_examples(self):
        from check import ROOT
        self.assertEqual(DEFAULT_PATHS, [ROOT / "examples"])

    def test_empty_input_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "explorer.html"
            with self.assertRaisesRegex(ValueError, "No Markdown"):
                build([directory], output)
            self.assertFalse(output.exists())

    def test_external_references_are_not_local_notes_or_indexes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evals"
            cases = [
                (root / "reference/stripe/example.md", "Stripe", True,
                 '---\nreference_provider: Stripe\nsource_url: https://docs.stripe.com/example\n---\n# Example\n\nRead it.'),
                (root / "notes/example.md", "Notes", False, "# Notes\n\nRead it."),
                (root / "guides/primer.md", "Primers", False, '---\nkind: primer\n---\n# Primer\n\nRead it.'),
            ]
            with patch("explore.ROOT", root):
                for path, group, reference, text in cases:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(text)
                    result = document(path)
                    self.assertEqual(result["group"], group)
                    self.assertEqual(result["reference"], reference)
                    if reference:
                        self.assertTrue(result["source_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
