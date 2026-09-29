# Writing checks

Find passages worth editing across a folder of Markdown guides. The checker runs
19 deterministic style checks and reports source lines and excerpts; the local HTML
explorer lets you filter documents by score and rule, then read findings in context.
For example, find guides with dense paragraphs, review the flagged passages, edit
the source Markdown, and rerun the checks to see what changed.

These are opinionated editing prompts. A passing score does not establish accuracy,
clarity, or usefulness. Some rules reflect the author's preferences: check 6 detects
third-person references to Alejo, and check 17 detects coaching-call framing.
The [full rubric](RUBRIC.md) explains each rule and its limitations. You can select
which checks to run in the command-line checker.

## Try the examples

You need Git, Python 3.10 or later, and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Run these commands in a terminal:

```sh
git clone https://github.com/alejoacelas/writing-checks.git
cd writing-checks
uv run scripts/check.py
```

The first run installs the script's declared dependencies, requiring internet
access if they are not cached. Checking and browsing run locally without a model,
API key, account, or server. Input files are never edited.

You should see two documents and this final line:

```text
2 documents; 3 failed document/check pairs.
```

[Save a draft](examples/clear-guide.md) passes all 19 checks.
[Choose a backup method](examples/review-guide.md) deliberately fails rules 11, 19,
and 22. A finding such as `L6 [19]` points to source line 6 and rule 19. Multiple
findings for one rule count as one failed document/check pair. The example command
exits with code **1** because it found writing to review; setup has succeeded.

Build the explorer and open it in your browser:

```sh
uv run scripts/explore.py --open
```

This writes `scripts/explorer.local.html` and reports `2 documents`. If your browser
does not open automatically, open that file yourself. The examples score 19/19 and
16/19: scores count rules passed, rather than individual findings.

## Check your writing

Replace the example paths below with your Markdown file or directory. Quote paths
that contain spaces. Directory scans recurse through files ending in `.md`.

```sh
uv run scripts/check.py /path/to/writing
uv run scripts/explore.py /path/to/writing --open
```

Edit your Markdown in your usual editor, then rerun the commands. The explorer is
a snapshot: rebuild it and refresh the browser to see edits. Each build replaces
the default output file.

The checker supports these optional choices:

| To… | Use… |
| --- | --- |
| Run only selected rules | `uv run scripts/check.py /path/to/writing --checks 1,7,8,19` |
| Skip the beginner acronym check | `uv run scripts/check.py /path/to/writing --audience technical` |
| Apply the recommendation-first check regardless of title | `uv run scripts/check.py /path/to/guide.md --options-guide` |
| Get structured results with findings and source lines | `uv run scripts/check.py /path/to/guide.md --format json` |

Checker exit codes are **0** for no findings, **1** for writing findings, and **2**
for invalid inputs. An empty directory is an invalid input. If you get “No Markdown
documents found”, check the path and exclusions below. JSON output uses the same
exit codes. Run either script with `--help` for its options.

Directory scans skip hidden paths, `node_modules`, `__pycache__`, `AGENTS.md`,
`DECISIONS.md`, `PLAN.md`, and `feedback-log.md`. Explicit file arguments override
those exclusions. With no input path, both scripts read only `examples/`.

The explorer always uses the complete beginner rubric; it does not accept the
checker's rule-selection, audience, or options-guide flags.

## Browse and keep results

The generated `scripts/explorer.local.html` works offline and is ignored by Git.
It embeds document prose and local file paths; share it only when those contents
are suitable to publish. Frontmatter and review comments are omitted from reading
text, but the title and source metadata are used in the interface.

To keep a separate snapshot, use `--output review.local.html` when building the
explorer. Choose an existing output directory. The `*.local.html` suffix keeps the
file ignored inside this repository; other output names are not automatically
ignored.

Use the document-type, length, and search filters to narrow the corpus. Click a rule
to show failures, or double-click to show passes. Pass-rate comparisons use the type,
length, and search selection before applying score or rule filters.

- **Up/down** or **j/k:** browse documents.
- **Left/right:** move between occupied scores.
- **[ / ]:** browse findings; **v:** switch to reading context.
- **/** searches; **Esc** resets filters; **?** opens shortcut help.

Optional YAML frontmatter `kind: article` or `kind: primer` groups your documents.
Other files appear as Notes, except `README.md` and `index.md`, which appear as
Indexes. Existing attributed snapshots can use `reference_provider: Stripe`,
`Django`, `GOV.UK`, or `Chrome`, plus `source_url`. These are metadata for files you
supply; the explorer does not download them. No third-party documentation snapshots
are bundled.

## Development

Run from the repository root:

```sh
uv run --with markdown-it-py==4.0.0 --with 'pyyaml>=6,<7' python -m unittest discover -s scripts -v
uv run scripts/explore.py
```

The tests cover rule behavior, source lines, command-line results, and explorer
data generation. See [agent instructions](AGENTS.md) before changing rules and
[publication decisions](DECISIONS.md) for the repository's scope.

The checker, explorer, and tests were extracted from a private writing-evaluation
project. This repository starts with fresh history and synthetic examples;
private writing, calibration reports, and model experiments remain there.

## Reuse

No reuse license has been selected. Ask the owner for permission before
redistributing or incorporating the code into another project.
