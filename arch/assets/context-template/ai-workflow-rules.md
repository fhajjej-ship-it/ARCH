# AI Workflow Rules

## How To Work

- Read `context/project-overview.md` and `context/architecture-context.md` before implementing.
- Use `context/progress-tracker.md` to choose the next task unless the user says otherwise.
- Implement one feature spec at a time.
- Keep edits scoped to the active feature.
- Update context when architecture, scope, or progress changes.

## Scoping Rules

- Split work that touches unrelated system boundaries.
- Do not combine a UI rewrite, data model change, and background job unless the feature spec requires it.
- Prefer the smallest change that proves the feature works.
- Ask a targeted question only when a missing decision blocks implementation.

## Quality Rules

- Handle happy path, empty state, loading state, and error state at the simplest useful level.
- Keep validation server-side for trusted writes.
- Do not hide failures with broad catch blocks.
- Do not add dependencies without a clear reason.
- Do not refactor unrelated code.

## Verification

- Run the narrowest relevant check first.
- Run broader checks when touching shared behavior.
- If automated checks do not exist, perform and document a manual verification path.
- Do not mark progress complete until verification has evidence.

## Progress Updates

When a feature is done:

1. Move it to Completed in `context/progress-tracker.md`.
2. Record the verification command or manual path.
3. Update architecture or standards files if implementation changed a decision.
