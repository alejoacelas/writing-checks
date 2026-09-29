"""Run from the repository root: uv run --with markdown-it-py==4.0.0 --with 'pyyaml>=6,<7' --with beautifulsoup4 --with markdownify python -m unittest discover -s scripts -v"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from check import RULES, evaluate, main


def failures(text, **kwargs):
    return {f["rule"] for f in evaluate(text, **kwargs)}


class WritingChecks(unittest.TestCase):
    def test_every_rule_detects_its_failure(self):
        examples = {
            1: " ".join(["word"] * 41) + ".",
            2: "Use the API through the CLI.",
            4: "# Which tool?\n\n- Alpha\n- Beta\n- Gamma\n",
            5: "Call advice, no entry behind it: test the result.",
            6: "Alejo recommends testing the result.",
            7: " ".join(["word"] * 81),
            8: "- " + " ".join(["word"] * 51),
            9: "---\ntitle: " + " ".join(["word"] * 15) + "\n---\nAnswer.",
            11: "Read it; then edit it; then check it.",
            12: "Read it — slowly — before editing.",
            13: "Read it (" + " ".join(["word"] * 11) + ").",
            16: "*Last updated 2026-09-19 · Confidence: documented.*\n\nAnswer.",
            17: "The habit I teach: save the file.",
            18: "See [Word skill — SKILL.md](https://example.org/file).",
            19: "Files: copy them. Conversations: start again. Billing: keep the plan.",
            20: "Read — then edit.",
            21: "Use this (with four extra words) — then proceed.",
            22: "Choose files, not chats. Use commands, not screenshots.",
            23: "Use a task-specific, per-user, read-only setting.",
        }
        self.assertEqual(set(examples), set(RULES))
        for rule, text in examples.items():
            with self.subTest(rule=rule):
                self.assertIn(rule, failures(text, options=rule == 4))

    def test_thresholds_and_exemptions(self):
        cases = [
            (1, " ".join(["word"] * 40) + ". Next sentence."),
            (2, "The application programming interface (API) connects tools."),
            (2, "Use the API (application programming interface)."),
            (2, "The command-line interface (CLI) runs commands."),
            (4, "# A vs B\n\nStart with A.\n\n- A\n- B\n- C"),
            (4, "# A vs B\n\nUse A for drafts.\n\n- A\n- B\n- C"),
            (7, " ".join(["word"] * 80)),
            (8, "- " + " ".join(["word"] * 50)),
            (9, "# " + " ".join(["word"] * 14)),
            (11, 'The source says “read; then edit.” Use `read; edit`.'),
            (12, "Read it — slowly. Then — edit it."),
            (13, "Read it (" + " ".join(["word"] * 10) + ")."),
            (13, "Read it ([" + " ".join(["word"] * 11) + "](url))."),
            (16, "Answer first.\n\nConfidence: documented."),
            (16, "*Last updated 2026-09-19*\n\nAnswer."),
            (17, "Save the file."),
            (18, "Open [AGENTS.md](AGENTS.md)."),
            (18, "See [Agent instructions](AGENTS.md)."),
        ]
        for rule, text in cases:
            with self.subTest(rule=rule, text=text):
                self.assertNotIn(rule, failures(text))

    def test_markdown_structure_and_line_numbers(self):
        text = "---\ntitle: Short\ncalls: ['Alejo recommends; private']\n---\n\n"
        text += "<!-- Alejo recommends; hidden -->\n\n```python\nAPI; Alejo recommends\n```\n\n"
        text += "> API; Alejo recommends\n\nKeep it short.\n\nThis fails; here; twice.\n"
        findings = evaluate(text)
        self.assertEqual([f["rule"] for f in findings], [11])
        self.assertEqual(findings[0]["line"], 16)
        self.assertEqual(findings[0]["excerpt"], "This fails; here; twice.")
        self.assertEqual(failures("Read [API](https://example.org/a_(b)) with CLI."), {2})
        self.assertIn(18, failures("Read more in [SKILL.md][s].\n\n[s]: /skill"))
        self.assertNotIn(11, failures("Words &amp; words &#59;".replace("&#59;", "&gt;")))
        self.assertIn(11, failures("Words &#59; words &#59; words"))

    def test_multiline_items_and_section_scopes(self):
        text = "- " + "word " * 30 + "\n\n  " + "word " * 21 + "\n"
        self.assertIn(8, failures(text))
        self.assertNotIn(7, failures(text))
        self.assertNotIn(4, failures("# A vs B\n\nText.\n\n## Sources\n\n- A\n- B\n- C"))
        self.assertIn(4, failures("# A vs B\n\nText.\n\n- A\n- B\n- C\n\nUse A."))
        self.assertIn(4, failures("# A vs B\n\nNetwork disabled by default.\n\n- A\n- B\n- C"))
        self.assertNotIn(2, failures("API and CLI", audience="technical"))
        self.assertIn(2, failures("API and CLI first. The application programming interface comes later."))
        self.assertNotIn(11, failures("## Sources\n\nCitation; detail.\n\n### More\n\nCitation; detail."))
        self.assertIn(11, failures("## Sources\n\nCitation; detail.\n\n## Advice\n\nRead; edit; check."))
        self.assertIn(13, failures("An aside (" + "word " * 11 + "(nested))."))
        self.assertIn(16, failures("> Historical reference: not reverified.\n\nAnswer."))

    def test_cli_json_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guide.md"
            path.write_text("# Simple guide\n\nKeep it short.")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main([str(path), "--format", "json"]), 0)
            report = json.loads(out.getvalue())
            self.assertEqual(len(report["documents"][0]["checks"]), len(RULES))
            path.write_text("Read; edit; check.")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(path)]), 1)
                self.assertEqual(main([str(path), "--checks", "1"]), 0)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([directory + "/missing"]), 2)
                self.assertEqual(main([str(path), "--checks", "24"]), 2)
                self.assertEqual(main([str(path), "--checks", "14"]), 2)
                path.write_text("---\ntitle: [not text]\n---\nBody")
                self.assertEqual(main([str(path)]), 2)

    def test_body_sentences_density_and_evidence_labels(self):
        long = " ".join(["word"] * 41) + "."
        self.assertIn(1, failures("Short opening.\n\n" + long))
        for excluded in ["> " + long, "```\n" + long + "\n```",
                         "## Sources\n\n" + long, "Last updated 2026-09-19 " + long]:
            self.assertNotIn(1, failures(excluded))
        paragraph = " ".join(["word"] * 23) + ". " + " ".join(["word"] * 23) + "."
        dense = "\n\n".join([paragraph] * 3)
        self.assertIn(7, failures(dense))
        self.assertNotIn(1, failures(dense))
        self.assertNotIn(7, failures("\n\n".join([paragraph] * 2)))
        self.assertNotIn(7, failures("\n\n".join(["- " + paragraph] * 3)))
        self.assertIn(5, failures("This may work (inferred — test it)."))
        self.assertNotIn(5, failures("This may work; the documentation does not specify it."))
        self.assertNotIn(5, failures("## Sources\n\nExample (reported)."))

    def test_calibrated_semicolons_and_acronyms(self):
        self.assertNotIn(11, failures("Write fixtures by hand; use JSON or YAML."))
        # Two semicolons exactly meet the allowance in 400 body words.
        paragraph = "Read; edit; " + " ".join(["word"] * 398)
        self.assertNotIn(11, failures(paragraph))
        self.assertIn(11, failures(paragraph.rsplit(" ", 1)[0]))
        self.assertNotIn(11, failures('The source says “read; edit; check”. Use `x; y; z`.'))
        self.assertNotIn(11, failures("Confidence: documented; tested; checked.\n\nAnswer."))
        self.assertNotIn(2, failures("Use the API."))
        self.assertNotIn(2, failures("Use the API via the command-line interface (CLI)."))

    def test_parallel_labels_and_comparison_applicability(self):
        self.assertIn(19, failures("New document: create a file. Formatting only: paste it."))
        for text in ["Files: copy them.\n\nBilling: keep it.",
                     "- Files: copy them.\n- Billing: keep it.",
                     "See https://example.org and https://example.net.",
                     "The standard interpretation guideline: use labels. The ceiling is real: check results.",
                     "`Files: copy them. Billing: keep it.`",
                     "> Files: copy them. Billing: keep it."]:
            self.assertNotIn(19, failures(text))
        self.assertNotIn(4, failures("# Create subscriptions\n\n- Open it\n- Edit it\n- Save it\n\n## Advanced options"))
        self.assertIn(4, failures("# Create subscriptions\n\n- A\n- B\n- C", options=True))
        self.assertNotIn(18, failures("## Sources\n\n[Word skill — SKILL.md](url)"))

    def test_retired_limits_do_not_affect_score(self):
        self.assertFalse({3, 10, 14, 15} & set(RULES))
        self.assertFalse(failures("## Never use National Insurance numbers to verify a user's identity\n\n"
                                  "| A | B |\n|---|---|\n" + "| X | Y |\n" * 10 +
                                  "\nRead [A](a), [B](b), [C](c), [D](d).\n\n"
                                  "## Further reading\n\n" + "- [Read](a)\n" * 8))

    def test_promoted_signals_boundaries_and_exclusions(self):
        self.assertNotIn(20, failures("word " * 100 + "—"))
        self.assertIn(20, failures("word " * 99 + "—"))
        self.assertNotIn(21, failures("Use this (three extra words) — then proceed."))
        self.assertIn(21, failures("Use this (with four extra words) and that (with four other words)."))
        self.assertNotIn(22, failures("Choose files, not chats."))
        self.assertNotIn(23, failures("Use a per-user, read-only setting."))
        noisy = "Choose files, not chats — (with four extra words). Use task-specific, per-user, read-only settings, not defaults."
        for excluded in ["> " + noisy, "```\n" + noisy + "\n```",
                         'The author says “' + noisy + '”', "## Sources\n\n" + noisy,
                         "## Further reading\n\n" + noisy, "Confidence: documented. " + noisy,
                         "Read this (reported — " + noisy + ")",
                         "Read ([" + noisy + "](url))."]:
            self.assertFalse({20, 21, 22, 23} & failures(excluded), excluded)
        findings = [f for f in evaluate("# Title\n\n" + noisy) if f["rule"] >= 20]
        self.assertEqual({f["rule"] for f in findings}, {20, 21, 22, 23})
        self.assertTrue(all(f["line"] == 3 and f["excerpt"] and f["reason"] for f in findings))


if __name__ == "__main__":
    unittest.main()
