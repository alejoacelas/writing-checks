# Writing checks

This repository contains the deterministic Markdown checker, local HTML explorer,
and synthetic examples. Read README.md for setup and RUBRIC.md for rule definitions.

Keep private corpora, reports, model runs, credentials, and generated explorer
snapshots out of Git. Explorer output embeds document prose and local paths;
use filenames ending in `.local.html` so the existing ignore rule applies.

Preserve rule IDs and change thresholds for writing reasons. Keep README.md,
RUBRIC.md, and the implementation consistent when changing behavior. After code
changes, run the tests and rebuild the example explorer with the Development and
verification commands in README.md. A default checker run exits 1 because the
bundled examples intentionally fail three document/check pairs.

No reuse license has been chosen. Leave that choice to the repository owner.

## Maintainer notes

Import selected reviewed files only from the original private evaluation project;
never merge its history. Keep private infrastructure and credential locations
outside this repository.
