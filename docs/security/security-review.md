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

### H1.1: CI actions pinned to immutable SHAs

The GitHub Actions workflow pins third-party actions to full commit SHAs instead of mutable major-version tags. The validator rejects any `uses:` entry that is not pinned to a 40-character SHA.

### H2: Eval baseline output confined to the repo

`scripts/evaluate_arch.py --write-baseline` now refuses absolute or relative paths that resolve outside the repository.

### H3: High-confidence secret scan added

`scripts/validate_arch.py` scans text files for common high-confidence token formats such as OpenAI-style keys, GitHub tokens, AWS access keys, private keys, Slack tokens, Supabase service keys, and Stripe live secrets.

### H4: Security reporting and ownership added

`SECURITY.md` defines private vulnerability reporting expectations. `.github/CODEOWNERS` assigns release, workflow, security documentation, and local file-write scripts to the repository owner.

## Release Provenance

### v0.2.1

- Commit: `2d6bb6d0037dc7380a811a3e3e08bd6265e15904`
- Tag: `v0.2.1`
- GitHub release: `https://github.com/fhajjej-ship-it/ARCH/releases/tag/v0.2.1`
- CI: `main` run `27871162442`, tag run `27871162512`
- Validation: `python3 scripts/validate_arch.py`, `python3 scripts/evaluate_arch.py`, `python3 scripts/evaluate_arch.py --write-baseline docs/evals/baseline-results.json`, `python3 -m py_compile arch/scripts/bootstrap_context.py scripts/validate_arch.py scripts/evaluate_arch.py`

## Residual Risk

- GitHub Actions are pinned to commit SHAs, but action updates are manual and should be refreshed during releases.
- ARCH writes developer-approved architecture context. It does not prove downstream generated applications are secure.
- The symlink protections reduce accidental and malicious path escapes, but they are not a general-purpose sandbox for running untrusted code.

## Verification Commands

```bash
python3 scripts/validate_arch.py
python3 scripts/evaluate_arch.py
python3 -m py_compile arch/scripts/bootstrap_context.py scripts/validate_arch.py scripts/evaluate_arch.py
```
