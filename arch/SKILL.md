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
2. Run an architect-grade decision interview.
   - Ask exactly one question at a time.
   - Include a recommended default answer, the tradeoff behind it, and the architecture impact.
   - Wait for the developer's answer before asking the next question.
   - Treat "yes", "use recommended", "confirm", or an explicit answer as a confirmed architecture decision.
   - Skip a question only when the repository or earlier answers already settle it.
3. Push back on scope.
   - Identify the smallest useful MVP.
   - Cut admin panels, billing, dashboards, multi-tenancy, queues, plugins, or microservices unless the MVP truly needs them.
4. Create or update `context/`.
   - Use `scripts/bootstrap_context.py` to create missing files from `assets/context-template/`.
   - Convert confirmed decisions into project-specific context files. Do not leave confirmed decisions only in chat.
   - Update affected context files after each confirmed decision once the folder exists.
   - Do not leave template placeholders.
5. Split the work into feature specs.
   - Each feature spec should be independently buildable and verifiable.
   - Keep feature specs small enough for a coding assistant to finish in one focused pass.
6. Verify the result.
   - Check that required files exist.
   - Search for stale placeholders.
   - Run `scripts/validate_context.py` when available.
   - Report assumptions, open questions, and the next implementation unit.

## Guided Decision Interview

Never ask the full intake as a numbered list. ARCH should feel like a senior architect interviewing the developer, one decision at a time.

Classify the project mode after repo inspection: `new_web_app`, `mobile`, `ai_product`, `cli_tool`, `existing_repo`, `ops_tool`, or `regulated_risk`. Read `references/architect-question-packs.md` before asking the first question, then use only the relevant pack(s).

Use this loop:

1. State what was learned from the repo inspection in one short sentence.
2. Ask one architect-level question.
3. Give exactly three answer options.
4. Make option 1 the recommended default.
5. Make option 2 the strongest reasonable alternative.
6. Make option 3 `Other`, for a free-form answer.
7. Explain the tradeoff and architecture impact.
8. Stop and wait.

### Architect Question Contract

Every question must lock one architecture decision, not ask for a generic preference. Good questions decide a boundary, source of truth, invariant, failure mode, or first vertical slice. Before asking, know:

- Which implementation decision this answer will unlock.
- Which risk or tradeoff the recommendation resolves.
- When the recommended option is wrong.
- Which `context/` files will change after confirmation.

Do not ask shallow questions such as "What tech stack do you want?" or "Do you need auth?" Instead ask about the architecture consequence: where writes happen, what data must be durable, who can mutate it, what external output is trusted, what can fail, and what must be verified.

Use this compact question layout:

```text
**Question 1/N**
[single architecture decision]

**1. Recommended**
[best default for this project stage, including when it fits].

**2. Second option**
[strongest reasonable alternative, including when it fits].

**3. Other**
[free-form answer].

**Why I recommend 1**
[short tradeoff, including when option 1 is wrong].

**Architecture impact**
[what this locks and which `context/` files will change].

**Reply:** `1`, `2`, or `3`. If `3`, write your answer in one sentence.
```

Keep options easy to select. Put each option label on its own bold line, keep each option body to one short sentence, and leave one blank line between blocks. Do not use tables for question options because they wrap poorly in chat. Do not make the developer write a structured answer unless they choose `Other`.

Architecture decision ladder:

1. Product boundary and value proof.
   - Recommend one first user, one painful job, and one completed workflow that proves v1 works.
   - Push back if the product serves multiple audiences or has no measurable success action.
2. System boundary and interface.
   - Decide whether v1 is a web app, mobile app, CLI, API, or existing-app feature, and what code boundary owns the workflow.
3. Domain model and source of truth.
   - Decide the core entities, durable state, ownership model, and which data can be mocked or hardcoded.
4. Auth and permission boundaries.
   - Decide who can read or mutate each important object, and where server-side validation must happen.
5. Integrations, AI, and async work.
   - Decide which external outputs can be trusted, which need review, and whether slow or retry-heavy work needs a job boundary.
6. Stack and deployment.
   - Recommend the simplest proven stack compatible with the repo, runtime constraints, and team.
   - Read `references/architecture-principles.md` before recommending concrete stack choices.
7. First buildable vertical slice.
   - Decide the smallest end-to-end feature spec that crosses UI, state, validation, and verification without dragging in optional surfaces.
8. Coding-agent handoff and invariants.
   - Record the rules future agents must not violate, then recommend assistant-specific rule files only when needed.
   - Read `references/agent-compatibility.md` when the user names Codex, Claude Code, Cursor, or another assistant.

After each answer, briefly confirm the decision and ask the next single question. When enough decisions exist, summarize the architecture assumptions before writing files.

If a user asks to build immediately, still do this architecture pass first unless the change is a small fix.

## Confirmed Decisions To Context

ARCH exists to write durable project context, not just to advise in chat.

Use these rules:

1. Treat the developer's answer as the source of truth.
   - If they answer `1`, "yes", "use recommended", or "confirm", record option 1.
   - If they answer `2`, record option 2.
   - If they answer `3` with text, record the free-form decision.
   - If they answer only `3`, ask one short follow-up for the free-form answer.
   - If they override the options, record their decision and adjust later recommendations around it.
   - If their answer conflicts with an earlier decision, ask one clarifying question before writing contradictory context.
2. Create `context/` as soon as there is enough confirmed information for a useful draft.
   - For empty repos, this usually means product, target user, value proof, and interface are confirmed.
   - For existing repos, bootstrap missing files immediately after inspection, then update only files affected by confirmed decisions.
3. After each confirmed decision, update the relevant context file.
   - Product, target user, MVP, value proof, and scope cuts go in `project-overview.md`.
   - Stack, data, auth, integrations, deployment, and invariants go in `architecture-context.md`.
   - Screens, states, navigation, responsiveness, accessibility, and visual rules go in `ui-context.md`.
   - Implementation rules, validation, tests, dependency policy, and file organization go in `code-standards.md`.
   - Agent execution rules and context update rules go in `ai-workflow-rules.md`.
   - Phase, next task, open questions, and decisions go in `progress-tracker.md`.
   - Buildable units go in `feature-specs/*.md`.
4. After writing, briefly tell the developer which files changed and ask the next single question.
5. Do not wait for a perfect brief. Put unresolved but important decisions in `progress-tracker.md` under Open Questions.

## Context Folder Contract

Create or update these files:

- `context/project-overview.md` - product goal, target user, MVP, scope cuts, flows, and success criteria.
- `context/architecture-context.md` - stack, system boundaries, data/storage model, auth, integrations, deployment, and invariants.
- `context/ui-context.md` - UX principles, navigation, screens, states, responsiveness, accessibility, and visual constraints.
- `context/code-standards.md` - implementation rules, validation, testing, dependency policy, and file organization.
- `context/ai-workflow-rules.md` - how coding assistants should scope, implement, verify, and update context.
- `context/progress-tracker.md` - current phase, completed work, next up, open questions, and decisions.
- `context/feature-specs/*.md` - one file per buildable implementation unit.

Read `references/context-file-guide.md` when writing the context files. Read `references/architect-question-packs.md` when selecting interview questions. Read `references/architecture-principles.md` when selecting or challenging a stack. Read `references/agent-compatibility.md` when the user cares about Codex, Claude Code, Cursor, or other assistant-specific execution.

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
python /path/to/arch/scripts/validate_context.py .
```

The `rg` command should return no template placeholders. Intentional open questions are allowed only in `context/progress-tracker.md`.
The context validator should exit successfully before claiming the project is ready for a coding assistant.
