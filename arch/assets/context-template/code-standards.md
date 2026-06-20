# Code Standards

## General

- Keep modules small and single-purpose.
- Preserve existing behavior unless a feature spec changes it.
- Validate external input before using it.
- Fix root causes instead of adding silent fallbacks.
- Keep implementation aligned with `context/architecture-context.md`.

## Language And Framework

- [Language/framework rule]
- [Language/framework rule]
- [Language/framework rule]

## API And Server Logic

- Validate request input at the boundary.
- Enforce auth and authorization before mutation.
- Return predictable response shapes.
- Keep long-running work out of request handlers.

## Data

- Model real concepts, not UI components.
- Keep ownership and permissions explicit.
- Do not store large generated content in relational rows unless justified.

## Dependencies

- Reuse existing dependencies first.
- Add a dependency only when it removes meaningful risk or complexity.
- Document why any new major dependency is needed.

## Testing And Verification

- [Unit test expectation]
- [Integration or manual verification expectation]
- [Build/typecheck/lint command]

## File Organization

- `[path]` - [responsibility]
- `[path]` - [responsibility]
- `[path]` - [responsibility]
