# Context File Guide

Use this guide when creating or updating `context/` for a project.

## Output Rules

- Write for the coding assistant that will implement the product next.
- Make every decision traceable to user goals, existing code, or explicit assumptions.
- Use "Open Questions" only when the answer changes implementation.
- Do not leave bracket placeholders in final files.
- Keep feature specs independently buildable and verifiable.

## `project-overview.md`

Include:

- Product name and one-sentence description.
- Target user and core job-to-be-done.
- MVP scope in concrete user-facing terms.
- Main happy path.
- Out-of-scope items for v1.
- Success criteria that can be manually or automatically verified.

Good success criteria:

- "A signed-in user can create a project and reopen it."
- "The generated Markdown file downloads with the current canvas content."

Weak success criteria:

- "The app is scalable."
- "The UI is modern."

## `architecture-context.md`

Include:

- Stack table by layer.
- System boundaries and ownership.
- Data model and storage decisions.
- Auth and authorization boundaries.
- External integrations and failure behavior.
- Background jobs or async work, only when needed.
- Deployment/runtime assumptions.
- Invariants that implementation must not violate.

Architecture invariants should be short and enforceable:

- "Every mutation checks authenticated user ownership before writing."
- "Large generated artifacts live in object storage, not relational rows."
- "Long-running AI generation runs outside request handlers."

## `ui-context.md`

Include:

- Product UX principles.
- Primary navigation and screen list.
- Empty, loading, success, and error states.
- Mobile and responsive behavior.
- Accessibility requirements.
- Design system or styling constraints.

Avoid marketing copy unless the project is a marketing site.

## `code-standards.md`

Include:

- Language and framework rules.
- Validation and error-handling rules.
- API and data access patterns.
- Testing expectations.
- Dependency policy.
- File organization.
- Security-sensitive handling.

Keep rules local to the project. Do not paste generic style guides unless the rule affects implementation.

## `ai-workflow-rules.md`

Include:

- How to choose the next task.
- How to split work.
- When to update context.
- What not to modify.
- Verification requirements.
- Rules for handling ambiguous requirements.

This file should control future coding agents.

## `progress-tracker.md`

Include:

- Current phase.
- Current goal.
- Completed work.
- In progress.
- Next up.
- Open questions.
- Architecture decisions.

Keep it factual. It is the handoff ledger between sessions.

## `feature-specs/*.md`

Each feature spec should include:

- Goal.
- User value.
- Requirements.
- Data/state changes.
- UX states.
- Implementation notes.
- Out of scope.
- Checks when done.

Feature specs should be small. If a spec touches UI, database, background jobs, and third-party integrations at once, split it.
