# Publication decisions

## Core decisions

### Publish reusable tools

- [Keep the public repository separate from private evaluation material](#keep-the-public-repository-separate-from-private-evaluation-material).
- [Use bundled synthetic examples by default](#use-bundled-synthetic-examples-by-default).

## Details

### Keep the public repository separate from private evaluation material

Publish reviewed checker and explorer code, tests, and documentation with fresh
Git history. The original evaluation repository contains private writing and
comparisons. Transfer future changes selectively; never merge its history.
Generated explorer pages embed input prose and local paths and remain Git-ignored.
The initial extraction is commit `80ecae0`.

### Use bundled synthetic examples by default

Default commands read only `examples/`. Users supply explicit paths for their own
writing. This makes a fresh checkout usable and prevents default commands from
scanning neighboring repositories. The rubric retains its original rule IDs and
personal preferences, documented in the README and rubric.

## Decision log

- 2026-09-29: Publish the reusable checker and explorer in a separate public
  repository with synthetic examples and fresh history; preserve the original
  evaluation repository's privacy.
