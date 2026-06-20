# Architecture Principles

Use these defaults when the user has not already chosen a stack. Prefer existing repository patterns over these defaults.

## MVP Defaults

- One primary user role.
- One deployable application.
- One relational database unless the product clearly needs another store.
- Server-side validation at every mutation boundary.
- Manual admin operations before admin dashboards.
- Hardcoded constants before configuration systems.
- Synchronous request flow unless work is slow, unreliable, or long-running.
- Managed services before custom infrastructure.

## Stack Selection

For a product web app:

- Use the current stable Next.js App Router, React, and TypeScript when the repo is already JavaScript/TypeScript or the user has no preference.
- Use Tailwind plus a proven component library when speed matters.
- Use PostgreSQL for relational product data.
- Use object storage for user uploads, generated files, and large artifacts.
- Use a hosted auth provider when auth is required and custom identity is not the product.

Recommended default for a new AI-assisted SaaS or product web app:

- App: Next.js App Router + TypeScript.
- UI: Tailwind CSS + shadcn/ui or the repo's existing component system.
- Database: PostgreSQL through a managed provider such as Supabase, Neon, or the deployment platform's managed Postgres.
- Auth: Clerk, Supabase Auth, or the platform's managed auth. Pick one; do not build custom auth for v1.
- Files/artifacts: managed object storage such as S3-compatible storage, Vercel Blob, or Supabase Storage.
- AI SDK layer: use a provider-agnostic SDK or thin service module so prompts, schemas, retries, and provider choice are isolated.
- Background jobs: Trigger.dev, Inngest, platform queues, or a simple cron/job runner only when work is slow, retry-heavy, or cost-sensitive.
- Email: Resend or a similar managed transactional email provider.
- Payments: Stripe only after the product has a clear paid action or plan boundary.
- Observability: Sentry or platform logging for errors; product analytics only after the core workflow exists.

For an API service:

- Use the repo's existing backend stack first.
- If starting fresh, choose a simple monolith in TypeScript or Python.
- Keep validation schemas close to request boundaries.
- Add background jobs only for long-running or retry-heavy work.

Recommended default for a new API:

- TypeScript service when sharing types with a web frontend matters.
- Python service when the product is data/ML-heavy and the repo already leans Python.
- PostgreSQL first; add Redis only for queues, rate limits, sessions, or hot cache needs.
- OpenAPI or generated client contracts when external consumers will integrate.

For a CLI or local developer tool:

- Prefer Python with a small dependency surface or Node.js when the ecosystem demands it.
- Keep configuration file-based.
- Make dry-run and explicit overwrite behavior available for file writes.

Recommended default for a new developer CLI:

- Python if file automation, text processing, or portability matters most.
- Node.js/TypeScript if the tool works mainly inside JavaScript/TypeScript projects.
- Keep file writes explicit and reversible: dry run, clear diff, and no silent overwrites.

For mobile:

- Use Expo/React Native unless native-only capabilities drive a different choice.
- Avoid building separate native apps for v1 unless required.

Recommended default for a new mobile MVP:

- Expo + React Native when mobile is required on day one.
- Responsive web app first when the core value can be proven in a browser.

## How To Recommend In The Interview

Every recommendation should include:

- A default choice.
- Why it is the best default for v1.
- When to choose a different option.
- What can be delayed.

Example:

```text
Recommended: Next.js + TypeScript on Vercel with managed Postgres.
Why: it gives you one deployable app, server routes, UI, and fast deployment without custom infrastructure.
Choose FastAPI instead if the product is primarily a backend/data API or the team is Python-first.
Delay: queues, analytics dashboards, multi-tenant billing, and admin panels until the core workflow works.
```

Do not present a menu of trendy tools. Recommend one path unless the user's answer materially changes the decision. Verify exact package names, versions, and provider APIs from current official docs before implementation.

## Data Decisions

- Model real product concepts, not UI screens.
- Store relationships and ownership in the database.
- Store large blobs and generated artifacts outside the database.
- Keep audit-critical events explicit.
- Avoid analytics schemas until the user has real events to measure.

## AI Feature Decisions

- Keep prompts, schemas, and tool contracts versionable.
- Validate model output before mutating application state.
- Record runs when users need status, retry, history, or support.
- Use durable jobs for slow AI work.
- Design failure states before adding streaming polish.

## Security Decisions

- Treat auth, authorization, file access, payment callbacks, webhooks, and AI tool calls as trust boundaries.
- Validate all external input.
- Check ownership before mutation.
- Keep secrets out of client code and context files.
- Add rate limits when endpoints can trigger cost, email, AI calls, or writes.

## Deployment Decisions

- Choose the simplest host that supports the selected framework.
- Keep local development commands explicit.
- Document required environment variables by name, without values.
- Avoid Kubernetes, service meshes, and microservices for v1 unless the product is infrastructure software.

## Pushback Triggers

Push back when the user asks for:

- Multi-tenant enterprise architecture before a single-user flow exists.
- Billing before value has been proven.
- Analytics dashboards before events exist.
- Custom auth before auth is a differentiator.
- Queues before there is slow or unreliable work.
- Admin panels before manual operations are painful.
- A rewrite without evidence the current stack blocks the MVP.
