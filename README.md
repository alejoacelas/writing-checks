# Writing checks

Find passages to review in Markdown: long sentences, dense paragraphs, unexplained
acronyms, repeated contrast phrases, and other style patterns. The checker reports
19 deterministic checks with source lines and excerpts. The HTML explorer lets you
filter documents by score and rule, then read findings in context.

These are opinionated editing prompts. A passing score does not establish accuracy,
clarity, or usefulness. Some rules reflect the author's preferences: check 6 detects
third-person references to Alejo, and check 17 detects coaching-call framing.
See the [full rubric](RUBRIC.md) for definitions and limitations.

## Run

Requires Python 3.10 or later and [uv](https://docs.astral.sh/uv/).
`uv run` installs the declared Python dependencies on first use. Scoring and browsing
then run locally without a model, API key, or server. Input files are never edited.

```sh
# Try the bundled synthetic examples.
uv run scripts/check.py
uv run scripts/explore.py --open

# Check your own files or directories.
uv run scripts/check.py /path/to/writing
uv run scripts/check.py /path/to/guide.md --format json
uv run scripts/check.py /path/to/writing --checks 1,7,8,19
uv run scripts/check.py /path/to/writing --audience technical
uv run scripts/explore.py /path/to/writing --open
```

The default examples include deliberate failures. Checker exit codes are **0** for
no findings, **1** for writing findings, and **2** for invalid inputs. Use
`--options-guide` to apply the recommendation-first check regardless of the title.
`--audience technical` skips the beginner acronym check. The explorer uses the
complete beginner rubric.

Directory scans include Markdown files, skipping hidden paths, `node_modules`,
`__pycache__`, `AGENTS.md`, `DECISIONS.md`, `PLAN.md`, and `feedback-log.md`.
Explicit file arguments override those exclusions.

## Explorer

The generated `scripts/explorer.local.html` works offline and is ignored by Git.
It embeds document prose and local file paths; share it only when those contents
are suitable to publish. Frontmatter and review comments are omitted from reading
text, but the title and source metadata are used in the interface.

Use the document-type, length, and search filters to narrow the corpus. Click a rule
to show failures, or double-click to show passes. Pass-rate comparisons use the type,
length, and search selection before applying score or rule filters.

- **Up/down** or **j/k:** browse documents.
- **Left/right:** move between occupied scores.
- **[ / ]:** browse findings; **v:** switch to reading context.
- **/** searches; **Esc** resets filters; **?** opens shortcut help.

Optional YAML frontmatter `kind: article` or `kind: primer` groups your documents.
Other files appear as Notes or Indexes. Existing attributed snapshots can use
`reference_provider: Stripe`, `Django`, `GOV.UK`, or `Chrome`, plus `source_url`.
No third-party documentation snapshots are bundled.

## Development

```sh
uv run --with markdown-it-py==4.0.0 --with 'pyyaml>=6,<7' python -m unittest discover -s scripts -v
uv run scripts/explore.py
```

The checker, explorer, and tests were extracted from a private writing-evaluation
project. This repository starts with fresh history and synthetic examples;
private writing, calibration reports, and model experiments remain there.
