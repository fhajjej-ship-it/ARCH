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
2. Run a guided decision interview.
   - Ask exactly one question at a time.
   - Include a recommended default answer and the tradeoff behind it.
   - Wait for the developer's answer before asking the next question.
   - Skip a question only when the repository or earlier answers already settle it.
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

## Guided Decision Interview

Never ask the full intake as a numbered list. ARCH should feel like a senior architect interviewing the developer, one decision at a time.

Use this loop:

1. State what was learned from the repo inspection in one short sentence.
2. Ask one question.
3. Give a recommended answer labeled `Recommended`.
4. Give 1-2 alternatives only when they are genuinely plausible.
5. Explain the tradeoff in plain language.
6. Give a short answer format.
7. Stop and wait.

Question format:

```text
Question 1/N: [single decision]

Recommended: [best default for this project stage].
Why: [short tradeoff].
Choose this instead if: [1-2 alternatives, only if useful].

Answer with: [specific short format].
```

Recommended question sequence:

1. Product and target user.
   - Recommend narrowing to one target user and one painful job.
   - Push back if the product serves multiple audiences in v1.
2. Value proof.
   - Recommend one user action that proves the product works.
   - Prefer a measurable workflow completion over vague engagement.
3. Interface.
   - Recommend the smallest interface that proves the job: usually web app for collaborative/product workflows, CLI for local developer tools, API only for integration-first products.
4. Stack and deployment.
   - Recommend the simplest proven stack compatible with the repo and team.
   - Read `references/architecture-principles.md` before recommending concrete stack choices.
5. Data and persistence.
   - Recommend the smallest real data model and identify what can be mocked, hardcoded, or manually operated.
6. Auth, security, integrations, and AI.
   - Recommend managed auth and validated server-side boundaries when user data exists.
   - Recommend delaying payments, dashboards, and heavy integrations unless they prove v1 value.
7. Coding-agent handoff.
   - Recommend Codex-friendly `context/` plus assistant-specific rule files only when needed.
   - Read `references/agent-compatibility.md` when the user names Codex, Claude Code, Cursor, or another assistant.

After each answer, briefly confirm the decision and ask the next single question. When enough decisions exist, summarize the architecture assumptions before writing files.

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
