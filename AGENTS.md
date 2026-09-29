# Writing checks

This public repository contains the deterministic checker, local HTML explorer,
and synthetic examples. Keep private corpora, reports, model runs, credentials,
and generated explorer snapshots out of Git. Import selected reviewed files only;
never merge history from the private writing-evals repository.

Preserve rule IDs and change thresholds for writing reasons. Run the tests and
rebuild the explorer using the commands in README.md after code changes.

The checker is in `scripts/check.py`; the explorer generator and HTML template
are in `scripts/explore.py` and `scripts/explorer.html`. Keep command examples in
`README.md` and rule descriptions in `RUBRIC.md` consistent with the code. Default
commands must continue to read only the bundled synthetic `examples/`.
