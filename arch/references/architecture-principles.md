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

For an API service:

- Use the repo's existing backend stack first.
- If starting fresh, choose a simple monolith in TypeScript or Python.
- Keep validation schemas close to request boundaries.
- Add background jobs only for long-running or retry-heavy work.

For a CLI or local developer tool:

- Prefer Python with a small dependency surface or Node.js when the ecosystem demands it.
- Keep configuration file-based.
- Make dry-run and explicit overwrite behavior available for file writes.

For mobile:

- Use Expo/React Native unless native-only capabilities drive a different choice.
- Avoid building separate native apps for v1 unless required.

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
