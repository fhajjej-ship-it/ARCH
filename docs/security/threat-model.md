# ARCH Threat Model

Last reviewed: 2026-06-20

## Scope

ARCH is a local Codex skill that interviews a developer and writes architecture context files into a target project's `context/` folder. The repository also includes validation scripts, an eval pack, and a GitHub Actions CI workflow.

In scope:

- `arch/SKILL.md`
- `arch/scripts/bootstrap_context.py`
- `arch/assets/context-template/`
- `scripts/validate_arch.py`
- `scripts/evaluate_arch.py`
- `.github/workflows/ci.yml`
- release and install documentation

Out of scope:

- Third-party coding agents that consume the generated `context/` files.
- User projects after ARCH has handed off implementation work.
- Secrets, credentials, or production data. ARCH should not require any.

## Assets

- Developer workstations running the skill.
- Target project files where `context/` is created or updated.
- ARCH release tags and GitHub release artifacts.
- The public repository and CI results.

## Trust Boundaries

- The ARCH repository is trusted after the developer selects a release.
- The target project path may be untrusted, especially when ARCH is run against a downloaded or forked repository.
- GitHub pull requests are untrusted code and must not receive write-scoped CI tokens.
- Eval scenarios and context templates are repository-owned data.

## Primary Threats

### T1: Link-based write escape

An untrusted project could place symlinks or hardlinks under `context/` before ARCH runs. If the bootstrap script overwrites those paths unsafely, it could modify files outside the project.

Controls:

- `bootstrap_context.py` rejects symlink components before writing.
- Forced updates write a temporary file and atomically replace the project entry instead of truncating an existing inode.
- File writes use `os.open` with `O_NOFOLLOW` when the platform supports it.
- Validation includes regression tests for symlinked files, symlinked `context/` directories, and hardlinked files.

### T2: Supply-chain drift in CI and installs

GitHub Actions and install instructions depend on remote release references. A compromised action, moved tag, or broad CI token could weaken release trust.

Controls:

- CI runs with top-level `contents: read` permissions.
- CI does not use `pull_request_target`.
- Release installs are pinned to explicit version tags.
- Release notes and eval baselines record verification evidence per version.

Accepted tradeoff:

- GitHub Actions are version-pinned by major version instead of commit SHA. For this small public repo, this keeps maintenance reasonable. Revisit SHA pinning if ARCH starts handling credentials, publishing artifacts automatically, or accepting external contributors at higher volume.

### T3: Committed secret leakage

ARCH should not contain secrets. A contributor could accidentally commit a token into docs, examples, scripts, or workflows.

Controls:

- Validation scans text files for high-confidence token formats.
- CI runs the validation on pushes and pull requests.

### T4: Unsafe developer tooling writes

Repo scripts that accept output paths could write outside the repository by mistake or through malicious input.

Controls:

- `evaluate_arch.py --write-baseline` refuses paths outside the repository.
- Validation includes a regression check for outside-repo baseline writes.

## Security Non-Goals

- ARCH does not sandbox coding agents.
- ARCH does not guarantee the generated architecture is secure for every downstream app.
- ARCH does not manage credentials, auth sessions, deployment keys, or production infrastructure.

## Review Triggers

Review this threat model when ARCH adds:

- network access
- package installation
- automatic GitHub release publishing
- generated executable code
- agent-to-agent tool invocation
- credentials, tokens, or user account integrations
