<p align="center">
  <img src="arch/assets/logo.svg" alt="ARCH" width="420">
</p>

# ARCH

[![Release](https://img.shields.io/github/v/release/fhajjej-ship-it/ARCH?label=release)](https://github.com/fhajjej-ship-it/ARCH/releases)
[![CI](https://github.com/fhajjej-ship-it/ARCH/actions/workflows/ci.yml/badge.svg)](https://github.com/fhajjej-ship-it/ARCH/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-0ea5a3.svg)](LICENSE)

ARCH is an agent skill for turning a vague software idea into a `context/` folder that Codex, Claude Code, Cursor, and other coding assistants can execute against.

It is not a SaaS or a project generator. It is a pre-build architecture pass: interview the developer, reduce scope to the smallest useful MVP, choose a practical architecture, and write durable context files before implementation starts.

ARCH asks one decision question at a time. Each question gives three easy choices: `1. Recommended`, `2. Second option`, and `3. Other`. When the developer answers or confirms a choice, ARCH records that decision in `context/` and keeps going.

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

Install the pinned release:

```bash
curl -fsSL https://raw.githubusercontent.com/fhajjej-ship-it/ARCH/v0.5.0/scripts/install_codex_skill.sh | bash -s -- v0.5.0
```

Update to the latest release using the `v0.5.0` installer:

```bash
curl -fsSL https://raw.githubusercontent.com/fhajjej-ship-it/ARCH/v0.5.0/scripts/install_codex_skill.sh | bash
```

Install from a local checkout while developing ARCH:

```bash
ARCH_SOURCE_DIR="$PWD" bash scripts/install_codex_skill.sh
```

The installer backs up any existing `~/.codex/skills/arch` directory, installs the selected release, writes `.arch-version`, and prints the installed ARCH version. Restart Codex so the skill is discovered.

## Use

In the project you want to architect:

```text
Use $arch to interview me about this project and create the context folder.
```

For an existing project:

```text
Use $arch to inspect this repo, update the context folder, and define the next buildable feature specs.
```

## Check Context Readiness

After ARCH creates `context/`, run the installed context doctor from the project root:

```bash
python ~/.codex/skills/arch/scripts/validate_context.py .
```

It checks for required context files, stale template placeholders, and at least one buildable feature spec with verification steps.

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

## Eval Pack

ARCH includes a static eval pack in `docs/evals/` with realistic project scenarios for new apps, existing repos, AI products, CLIs, mobile apps, ops tools, and regulated-risk ideas. Use it before releases to check the 3-option interview and context-writing workflow.

## Security

ARCH is local-first and should not require secrets. Security docs live in `docs/security/`, including the current threat model and security review. Validation checks for linked-file write escapes, high-confidence committed secrets, constrained CI permissions, and eval output paths that leave the repository.

## Validation And Releases

```bash
python3 scripts/validate_arch.py
python3 scripts/evaluate_arch.py
bash -n scripts/install_codex_skill.sh
python3 -m py_compile arch/scripts/bootstrap_context.py arch/scripts/validate_context.py scripts/validate_arch.py scripts/evaluate_arch.py
```

ARCH uses semantic versions in `VERSION`, release notes in `RELEASE_NOTES.md`, Git tags like `v0.1.0`, and GitHub Releases. See `docs/release-process.md`.

## License

MIT
