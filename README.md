# Writing checks

Find passages worth editing in Markdown: long sentences, dense paragraphs,
unexplained acronyms, and repeated style patterns. Run 19 deterministic checks
with source lines and excerpts, or browse the findings in a local HTML explorer.

For example, the bundled sentence “Files: copy them. Versions: keep them.
Recovery: test it.” produces this finding:

```text
L6 [19] Two or more short sentence-initial labels; separate these into items: Files: copy them. Versions: keep them. Recovery: test it.
```

These are opinionated editing prompts. A passing score does not establish accuracy,
clarity, or usefulness. Some rules reflect the author's preferences: check 6 detects
third-person references to Alejo, and check 17 detects coaching-call framing.
See the [full rubric](RUBRIC.md) before using scores to judge writing.

## Try the examples

You need Git, Python 3.10 or later, and [uv](https://docs.astral.sh/uv/getting-started/installation/).
No accounts, API keys, model subscriptions, or hosted services are needed. There
are no service charges; computation and storage use your own machine. First use
needs internet access to download Python dependencies.

Run these commands in a terminal:

```sh
git clone https://github.com/alejoacelas/writing-checks.git
cd writing-checks
uv run scripts/check.py
```

`uv run` installs the dependencies declared in the script. The clear example
passes all checks; the review example fails rules 11, 19, and 22. The final line is:

```text
2 documents; 3 failed document/check pairs.
```

**Exit code 1 is expected here:** the examples include deliberate failures. Each
rule counts once per document, even if it reports several passages. Checker exit
codes are **0** for no findings, **1** for writing findings, and **2** for invalid
inputs. Do not chain the next command with `&&` after this example run.

Open the explorer:

```sh
uv run scripts/explore.py --open
```

It reports `2 documents` and writes `scripts/explorer.local.html`. If a browser
doesn't open automatically, open that file yourself. Select a document to see its
findings, then choose **Read in context** to read the surrounding text. The page
works offline without a server.

## Check your writing

Run from the cloned repository, replacing the example paths with your Markdown
file or directory. Quote paths containing spaces. Input files are never edited.

```sh
uv run scripts/check.py /path/to/writing
uv run scripts/check.py /path/to/guide.md --format json
uv run scripts/explore.py /path/to/writing --open
```

Both commands accept multiple files or directories. Directory scans include `*.md`
files recursively, skipping hidden paths, `node_modules`, `__pycache__`,
`AGENTS.md`, `DECISIONS.md`, `PLAN.md`, and `feedback-log.md`. Explicit file
arguments override those exclusions. With no paths, both tools read only the
bundled `examples/` directory.

To focus the checker on your own preferences, select rule IDs from the rubric:

```sh
uv run scripts/check.py /path/to/writing --checks 1,7,8,19
uv run scripts/check.py /path/to/writing --audience technical
uv run scripts/check.py /path/to/guide.md --options-guide
```

`--audience technical` skips the beginner acronym check. `--options-guide` applies
the recommendation-first check regardless of the title. These options belong to
the checker; the explorer always uses all 19 checks with the beginner audience.

If you see “No Markdown documents found”, check the directory's file extensions
and exclusions above, or pass a file explicitly. For other errors, give your
coding assistant the command and error output, or inspect `--help` for either script.

## Browse and save results

The explorer is a snapshot: rerun its command after editing your writing. Each
run replaces `scripts/explorer.local.html`. To keep separate snapshots, supply
`--output`, using an existing directory:

```sh
uv run scripts/explore.py /path/to/writing --output review.local.html --open
```

Generated pages embed document prose, titles, findings, and local file paths.
Keep them private unless those contents are suitable to share. Names ending in
`.local.html` are ignored by Git; other output names are not. Frontmatter and
review comments are omitted from reading text, but selected title and source
metadata are retained. This is not a tool for removing sensitive information.
JSON checker output also contains paths and excerpts.

Use the document-type, length, and search filters to narrow the corpus. Click a
rule to show failures, or double-click to show passes. Pass-rate comparisons use
the type, length, and search selection before applying score or rule filters.

- **Up/down** or **j/k:** browse documents.
- **Left/right:** move between occupied scores.
- **[ / ]:** browse findings; **v:** switch to reading context.
- **/** searches; **Esc** resets filters; **?** opens shortcut help.

Optional YAML frontmatter `kind: article` or `kind: primer` groups your documents.
Other files appear as Notes or Indexes. Existing attributed snapshots can use
`reference_provider: Stripe`, `Django`, `GOV.UK`, or `Chrome`, plus `source_url`.
No third-party documentation snapshots are bundled or fetched. Opening an
**Original page** link visits the specified website.

## Development and verification

Run the tests and rebuild the example explorer:

```sh
uv run --with markdown-it-py==4.0.0 --with 'pyyaml>=6,<7' python -m unittest discover -s scripts -v
uv run scripts/explore.py
```

The 14 automated tests, example checker output, and HTML generation were verified
on macOS on 2026-09-29. Browser interactions and setup on Windows or Linux were
not verified in that review.

## Reuse and provenance

**No reuse license is included yet.** The owner needs to choose a license before
peers can rely on explicit permission to reuse or redistribute this code.

The checker, explorer, and tests were extracted from a private writing-evaluation
project. This repository starts with fresh history and synthetic examples;
private writing, calibration reports, and model experiments remain there.
