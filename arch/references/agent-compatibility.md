# Agent Compatibility

ARCH writes a `context/` folder because every coding assistant can read files. Keep the folder assistant-neutral, then add assistant-specific rules only when useful.

## Universal Rules

- Use stable file names.
- Keep implementation order in `progress-tracker.md`.
- Put exact commands in feature specs.
- Keep architecture decisions in one place.
- Update context immediately when implementation changes scope or behavior.
- Avoid contradictory instructions across README, context files, and assistant rule files.

## Codex

- Prefer `AGENTS.md` for repository-wide execution rules.
- Keep `context/ai-workflow-rules.md` focused on product-specific implementation rules.
- When Codex will implement next, include verification commands and exact files to inspect.

## Claude Code

- Prefer `CLAUDE.md` for assistant behavior and repository conventions.
- Keep long product specs in `context/` and reference them from `CLAUDE.md`.
- Avoid burying critical requirements in chat-only history.

## Cursor

- Prefer `.cursor/rules` for always-on coding rules.
- Keep product architecture in `context/` and reference it from Cursor rules.
- Use feature specs for discrete implementation prompts.

## Handoff Prompt Pattern

Use a short prompt that points the assistant to context before implementation:

```text
Read the context folder first. Implement the next item in context/progress-tracker.md.
Follow context/ai-workflow-rules.md and update progress when verified.
```

For a specific feature:

```text
Read context/project-overview.md, context/architecture-context.md, and
context/feature-specs/NN-feature-name.md. Implement only that feature and run
the listed checks.
```
