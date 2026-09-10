# Contributing

## Daily updates

At the end of each day's active development session, update `docs/DAILY_UPDATES.md` with completed work, verification results and the next tasks, then commit and push the reviewed changes to the current working branch. The user has requested ongoing pushes as implementation progresses. Keep unfinished features clearly marked and exclude secrets and local artifacts. This is a development-session workflow, not an unattended scheduled job.

All application implementation is Python. Keep project-specific code under `projects/<name>/src`, tests under `projects/<name>/tests`, and planning under that project's `docs` directory. Do not add a JavaScript or TypeScript application to this repository.

Before implementation, select a task from the active phase, check its dependencies and write down the behavior its acceptance criteria require. Use branches such as `phase-1/P1-03-candidate-profile` and include the task ID in commits and pull requests.

During implementation, keep the change small enough to review. Add behavior-focused tests for scoring, authorization, data isolation and failure handling when those features are implemented. Never replace a real sandbox with Python `exec`, `eval` or subprocess execution of candidate code in the API service.

Before closing a task, run its applicable checks, record the results in the pull request, update the phase checklist and document any changed API or configuration. Before closing a phase, demonstrate its complete exit scenario and record remaining defects. A folder, stub or mock alone does not satisfy a product acceptance criterion.

Dependency choices must be resolved and locked when implemented. Provider calls must have explicit timeouts, budget controls, retries where safe, and offline test doubles. New model or prompt versions must pass the relevant evaluation baseline before release.
