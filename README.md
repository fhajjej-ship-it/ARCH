<p align="center">
  <img src="arch/assets/logo.svg" alt="ARCH" width="420">
</p>

# ARCH

ARCH is an agent skill for turning a vague software idea into a `context/` folder that Codex, Claude Code, Cursor, and other coding assistants can execute against.

It is not a SaaS or a project generator. It is a pre-build architecture pass: interview the developer, reduce scope to the smallest useful MVP, choose a practical architecture, and write durable context files before implementation starts.

## What It Creates

ARCH creates or updates:

- `context/project-overview.md`
- `context/architecture-context.md`
- `context/ui-context.md`
- `context/code-standards.md`
- `context/ai-workflow-rules.md`
- `context/progress-tracker.md`
- `context/feature-specs/*.md`

The output is designed to keep coding agents from improvising product scope, stack decisions, file boundaries, and verification steps.

## Install For Codex

Clone this repo, then copy the skill folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills/arch
cp -R arch/. ~/.codex/skills/arch/
```

Restart Codex so the skill is discovered.

## Use

In the project you want to architect:

```text
Use $arch to interview me about this project and create the context folder.
```

For an existing project:

```text
Use $arch to inspect this repo, update the context folder, and define the next buildable feature specs.
```

## Why This Exists

AI coding assistants execute better when the project has:

- a clear MVP
- explicit architecture boundaries
- concrete data and auth rules
- feature specs small enough to finish
- verification steps for each unit
- a progress ledger that survives chat history loss

ARCH creates that structure before code generation starts.

## Example

See `examples/ghost-ai-context/context/` for an example context folder from a collaborative architecture workspace project.

## License

MIT
