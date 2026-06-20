# Release Notes

## v0.1.0 - 2026-06-20

Initial public release of ARCH.

### Highlights

- Added the installable `arch` Codex skill.
- Added a guided one-question-at-a-time architecture interview.
- Added recommended modern defaults for web apps, APIs, CLIs, mobile apps, AI features, auth, storage, background jobs, email, payments, and observability.
- Added `context/` templates for product overview, architecture, UI, code standards, AI workflow rules, progress tracking, and feature specs.
- Added `bootstrap_context.py` to create missing context files safely.
- Added an example context folder from a collaborative architecture workspace project.
- Added CI validation for skill metadata, assets, templates, and bootstrap behavior.

### Verification

```bash
python3 scripts/validate_arch.py
python3 -m py_compile arch/scripts/bootstrap_context.py scripts/validate_arch.py
tmpdir=$(mktemp -d); python3 arch/scripts/bootstrap_context.py "$tmpdir"; find "$tmpdir/context" -maxdepth 2 -type f | sort; rm -rf "$tmpdir"
```
