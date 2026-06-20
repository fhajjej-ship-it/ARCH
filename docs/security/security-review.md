# ARCH Security Review

Review date: 2026-06-20

## Summary

This review focused on unsafe file writes, supply-chain posture, and accidental secret leakage. ARCH is a local skill and should not need credentials. The main risk was writing context templates into a project path that may be controlled by someone else.

## Findings

### S1: Bootstrap could overwrite linked targets outside the project

Severity: Medium

Status: Fixed

Before this review, `arch/scripts/bootstrap_context.py` opened target files with normal `Path.open("wb")`. If a target project already contained `context/project-overview.md` as a symlink or hardlink to another file, running the bootstrap with `--force` could overwrite that external file.

Fix:

- Reject symlink components under the target project before creating or writing files.
- Write through a temporary file and atomically replace the project entry instead of truncating existing files.
- Use `os.open` with `O_NOFOLLOW` where available.
- Add validator regression tests for symlinked context files, symlinked `context/` directories, and hardlinked context files.

Validation:

- `scripts/validate_arch.py` now fails if bootstrap writes through symlinked paths or truncates a hardlink target.

## Hardening Changes

### H1: CI token permissions constrained

The GitHub Actions workflow now declares:

```yaml
permissions:
  contents: read
```

The validator also rejects `pull_request_target` usage.

### H2: Eval baseline output confined to the repo

`scripts/evaluate_arch.py --write-baseline` now refuses absolute or relative paths that resolve outside the repository.

### H3: High-confidence secret scan added

`scripts/validate_arch.py` scans text files for common high-confidence token formats such as OpenAI-style keys, GitHub tokens, AWS access keys, private keys, Slack tokens, Supabase service keys, and Stripe live secrets.

## Residual Risk

- GitHub Actions are pinned by major version, not commit SHA. This is acceptable for the current repo because CI only validates local files with read-only permissions. If ARCH adds automated publishing or credentialed workflows, pin actions by SHA.
- ARCH writes developer-approved architecture context. It does not prove downstream generated applications are secure.
- The symlink protections reduce accidental and malicious path escapes, but they are not a general-purpose sandbox for running untrusted code.

## Verification Commands

```bash
python3 scripts/validate_arch.py
python3 scripts/evaluate_arch.py
python3 -m py_compile arch/scripts/bootstrap_context.py scripts/validate_arch.py scripts/evaluate_arch.py
```
