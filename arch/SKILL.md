---
name: arch
description: Architecture planning and context-folder generation for AI-assisted software projects. Use when starting, reshaping, or rescuing a project before implementation; when a user asks to architect an app, define an MVP, choose a tech stack, write feature specs, create or update a context folder, or prepare Codex, Claude Code, Cursor, or another coding assistant to execute reliably.
---

# ARCH

## Overview

ARCH turns a loose product idea into a concrete `context/` folder that a coding assistant can execute against. It is for pre-build architecture, MVP scoping, feature sequencing, and keeping implementation agents aligned.

## Core Workflow

1. Inspect the repository first.
   - Read existing README, package files, framework config, database schema, docs, and any current `context/` folder.
   - Preserve useful existing decisions. Do not overwrite user-written context without reading it.
2. Interview only for information that materially changes the architecture.
   - If the request is vague, ask a concise intake before writing files.
   - If enough information exists, state assumptions and continue.
3. Push back on scope.
   - Identify the smallest useful MVP.
   - Cut admin panels, billing, dashboards, multi-tenancy, queues, plugins, or microservices unless the MVP truly needs them.
4. Create or update `context/`.
   - Use `scripts/bootstrap_context.py` to create missing files from `assets/context-template/`.
   - Then edit the files so they are project-specific and executable. Do not leave template placeholders.
5. Split the work into feature specs.
   - Each feature spec should be independently buildable and verifiable.
   - Keep feature specs small enough for a coding assistant to finish in one focused pass.
6. Verify the result.
   - Check that required files exist.
   - Search for stale placeholders.
   - Report assumptions, open questions, and the next implementation unit.

## Intake Questions

Ask at most seven questions in one pass. Prefer these, adapted to the project:

1. What are we building, and who is the first target user?
2. What single user action proves version 1 is valuable?
3. What interface is required for v1: web app, API, CLI, mobile app, browser extension, or something else?
4. What stack, hosting, database, auth, or budget constraints already exist?
5. What data must exist on day one, and what can be mocked or hardcoded?
6. What integrations, payments, AI features, or security requirements are truly required for v1?
7. Which coding assistant will execute this, and are there existing rules files such as `AGENTS.md`, `CLAUDE.md`, or `.cursor/rules`?

If a user asks to build immediately, still do this architecture pass first unless the change is a small fix.

## Context Folder Contract

Create or update these files:

- `context/project-overview.md` - product goal, target user, MVP, scope cuts, flows, and success criteria.
- `context/architecture-context.md` - stack, system boundaries, data/storage model, auth, integrations, deployment, and invariants.
- `context/ui-context.md` - UX principles, navigation, screens, states, responsiveness, accessibility, and visual constraints.
- `context/code-standards.md` - implementation rules, validation, testing, dependency policy, and file organization.
- `context/ai-workflow-rules.md` - how coding assistants should scope, implement, verify, and update context.
- `context/progress-tracker.md` - current phase, completed work, next up, open questions, and decisions.
- `context/feature-specs/*.md` - one file per buildable implementation unit.

Read `references/context-file-guide.md` when writing the context files. Read `references/architecture-principles.md` when selecting or challenging a stack. Read `references/agent-compatibility.md` when the user cares about Codex, Claude Code, Cursor, or other assistant-specific execution.

## Bootstrap Command

When `context/` is missing or incomplete, run:

```bash
python arch/scripts/bootstrap_context.py .
```

If this skill is installed outside the repository, run the script from the installed skill path and pass the project path:

```bash
python /path/to/arch/scripts/bootstrap_context.py /path/to/project
```

The script creates only missing files by default. After bootstrapping, edit the generated files with the actual architecture, product decisions, and feature plan.

## Quality Bar

- Use concrete nouns, file paths, commands, models, routes, and data shapes.
- Put unresolved decisions in `progress-tracker.md` under Open Questions.
- Do not hide uncertainty inside confident architecture claims.
- Prefer boring, proven architecture over novelty.
- Prefer the repository's existing stack over a rewrite.
- Do not recommend exact package versions unless they are already in the repo or have been verified.
- Make implementation order obvious to the next coding assistant.
- Keep all context files consistent with each other.

## Verification

Before finishing, run the narrowest useful checks:

```bash
test -d context
find context -maxdepth 2 -type f | sort
rg -n "TODO|TBD|PLACEHOLDER|\\[[A-Za-z0-9 _/-]+\\]" context
```

The `rg` command should return no template placeholders. Intentional open questions are allowed only in `context/progress-tracker.md`.
