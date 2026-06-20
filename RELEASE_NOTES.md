# Release Notes

## v0.2.0 - 2026-06-20

Evaluation loop release.

### Highlights

- Added an ARCH eval pack with realistic project scenarios across new web apps, AI products, existing repos, CLIs, mobile, ops tools, and regulated-risk ideas.
- Added a static evaluator for the 3-option interview contract and context-writing expectations.
- Added baseline eval result generation for release evidence.
- Wired evals into CI and local validation docs.

### Verification

```bash
python3 scripts/validate_arch.py
python3 scripts/evaluate_arch.py
python3 -m py_compile arch/scripts/bootstrap_context.py scripts/validate_arch.py scripts/evaluate_arch.py
```

## v0.1.1 - 2026-06-20

Question usability release.

### Highlights

- Changed ARCH interview questions to use exactly three answer options.
- Made option 1 the recommended default, option 2 the strongest alternative, and option 3 a free-form "Other" answer.
- Updated decision recording rules so numeric answers map directly to confirmed context decisions.
- Updated install docs to pin the latest release tag.

### Verification

```bash
python3 scripts/validate_arch.py
python3 -m py_compile arch/scripts/bootstrap_context.py scripts/validate_arch.py
```

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
