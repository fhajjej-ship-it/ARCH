# Architect Question Packs

Use this reference after repo inspection to choose the next unresolved architecture decision. Ask one question at a time and adapt the wording to the actual repo, product idea, and confirmed decisions.

Do not read every pack into the chat output. Select the relevant project mode and ask the next decision gate from that pack.

## Shared Question Rules

Every architect-level question should decide at least one of:

- system boundary: which app, route, command, worker, or service owns the workflow
- source of truth: which data is durable, mocked, derived, or manually operated
- trust boundary: who can read or mutate data and which inputs require validation
- failure boundary: what can fail, retry, be reviewed, or be safely ignored in v1
- vertical slice: which end-to-end feature proves the product without optional surfaces

Avoid preference surveys. Replace "Which stack do you want?" with "Which runtime boundary should own the first value-producing workflow?" Replace "Do you need auth?" with "Who owns this object, and what mutation must be rejected server-side?"

## New Web App

Use for a fresh browser-based product.

- Workflow boundary: recommend one signed-in or link-based user flow that starts and finishes in the web app.
- Source of truth: recommend a relational data model for shared product state; mock only content that is not part of the value proof.
- Auth boundary: recommend managed auth when users own private data; use magic-link or invite-token access only when collaboration needs low-friction entry.
- Runtime boundary: recommend one deployable app with server routes before queues, microservices, or separate admin apps.
- First slice: recommend one route set that creates, mutates, reloads, and verifies the core object.

Example first question: "Which user-owned object should be the source of truth for v1, and what mutation proves the workflow works?"

## Mobile App

Use when mobile is required or the user names iOS, Android, Expo, React Native, or native device capabilities.

- Interface boundary: recommend responsive web unless native capabilities are part of the value proof.
- Native capability boundary: ask whether push notifications, camera, location, contacts, widgets, or offline mode are required on day one.
- State boundary: decide what must work offline, what syncs later, and what conflicts are impossible in v1.
- Release boundary: decide whether Expo/manual device testing is enough before app store distribution.
- First slice: recommend one mobile loop with permission failure, empty state, and retry behavior.

Example first question: "Which native capability is required for the value proof, and what is the fallback if permission is denied?"

## AI Product

Use when v1 includes LLMs, agents, generated content, embeddings, document parsing, or model-driven decisions.

- AI boundary: recommend one model-assisted task with human review before the output mutates trusted product state.
- Schema boundary: decide the structured input, output schema, validation rule, and what happens when validation fails.
- Persistence boundary: decide which prompts, inputs, outputs, model versions, and review states must be stored for support or retry.
- Cost boundary: decide whether calls run synchronously, in a job, or behind explicit user action.
- Safety boundary: decide what the AI must never claim, decide, send, charge, delete, or execute.

Example first question: "Which AI output is trusted enough to store, and what validation or human review must pass before it changes product state?"

## CLI Or Developer Tool

Use for local tools, repo automation, code generation, or command-line workflows.

- Write boundary: recommend dry-run first for file mutations; require explicit overwrite or patch preview for destructive changes.
- Config boundary: decide whether inputs come from flags, config files, repo inspection, or interactive prompts.
- Safety boundary: decide which paths can be read or written and how symlinks, ignored files, and generated output are handled.
- Distribution boundary: decide whether v1 installs as a local script, package, or repo template.
- First slice: recommend one command that inspects a real repo, prints deterministic output, and has a manual verification path.

Example first question: "Which file operation should v1 perform, and what dry-run or rollback boundary prevents unsafe writes?"

## Existing Repo Rescue

Use when the repository already has code, dependencies, schema, routes, or partial context.

- Preservation boundary: identify what decisions must be preserved unless proven to block the MVP.
- Completion boundary: choose one incomplete workflow to finish before refactoring or adding new surfaces.
- Data boundary: map existing tables, APIs, routes, and ownership checks before creating new ones.
- Risk boundary: decide whether the first task is context creation, failing-test repair, build repair, or a vertical feature.
- First slice: recommend a spec that names existing files and verification commands.

Example first question: "Which existing workflow should be completed first, and which current stack or data decisions must Codex preserve while doing it?"

## Internal Ops Tool

Use for dashboards, back-office workflows, spreadsheet replacement, CRM-like tools, or support/admin operations.

- Decision boundary: ask which repeated operational decision the tool makes faster or safer.
- Data freshness boundary: decide whether v1 reads live data, imports a CSV, syncs on a schedule, or uses manual entry.
- Permission boundary: recommend one internal role first; delay complex RBAC until one workflow works.
- Audit boundary: decide which edits need actor, timestamp, previous value, or reason.
- First slice: recommend one dense table or task queue flow with filter, update, empty state, and error state.

Example first question: "Which operational record can users change in v1, and what audit trail is required for that mutation?"

## Regulated Or Security-Sensitive App

Use when the project touches healthcare, finance, children, legal advice, employment decisions, identity, payments, private files, secrets, or high-impact AI.

- Scope boundary: recommend a safer adjacent workflow when direct advice, automated decisions, or regulated actions are too risky for v1.
- Data classification boundary: decide which data is sensitive, how long it is retained, and how deletion/export works.
- Review boundary: decide where human review, disclaimers, clinician/professional approval, or manual operations are mandatory.
- Security boundary: decide auth, authorization, encryption/storage, audit events, rate limits, and abuse prevention before feature polish.
- First slice: recommend one low-risk workflow that can be verified without making high-stakes claims.

Example first question: "What safer adjacent workflow can v1 support, and what user action must remain outside automated decision-making?"
