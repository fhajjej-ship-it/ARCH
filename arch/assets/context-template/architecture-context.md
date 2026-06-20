# Architecture Context

## Stack

| Layer | Technology | Role |
| --- | --- | --- |
| App/framework | [technology] | [role] |
| UI | [technology] | [role] |
| Data | [technology] | [role] |
| Auth | [technology or none] | [role] |
| Deployment | [technology] | [role] |

## System Boundaries

- `[path or module]` - [responsibility]
- `[path or module]` - [responsibility]
- `[path or module]` - [responsibility]

## Data Model

### [Concept]

- [field]: [type and purpose]
- [relationship]: [ownership or cardinality]

## Storage Model

- Relational data: [where it lives]
- Files/artifacts: [where they live]
- Cache/session state: [where it lives]

## Auth And Authorization

- Auth provider: [provider or none]
- User roles: [roles]
- Mutation rule: [ownership or permission rule]

## Integrations

- [Integration]: [purpose, failure behavior, required env vars without values]

## Background Work

- [Job/task]: [trigger, input, output, retry/failure behavior]

## Deployment

- Runtime: [runtime]
- Hosting: [host]
- Required environment variables: [names only]

## Invariants

1. [Rule implementation must not violate]
2. [Rule implementation must not violate]
3. [Rule implementation must not violate]
