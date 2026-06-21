# Release Process

ARCH uses simple semantic versioning.

## Version Files

- `VERSION` is the source of truth.
- `RELEASE_NOTES.md` records public changes and verification commands.
- Git tags use `vX.Y.Z`.
- GitHub releases use the tag name and the relevant release notes section.

## Version Rules

- Patch: wording fixes, docs, small template corrections.
- Minor: new workflow behavior, new context files, new validation, new assistant support.
- Major: breaking install path, renamed skill, or incompatible context contract changes.

## Release Checklist

1. Update `VERSION`.
2. Update `RELEASE_NOTES.md`.
3. Refresh pinned GitHub Action SHAs when the upstream action tag changes:

```bash
git ls-remote https://github.com/actions/checkout.git refs/tags/v4
git ls-remote https://github.com/actions/setup-python.git refs/tags/v5
```

Keep `.github/workflows/ci.yml` pinned to full 40-character commit SHAs.

4. Run validation:

```bash
python3 scripts/validate_arch.py
python3 scripts/evaluate_arch.py
python3 scripts/evaluate_arch.py --write-baseline docs/evals/baseline-results.json
bash -n scripts/install_codex_skill.sh
python3 -m py_compile arch/scripts/bootstrap_context.py arch/scripts/validate_context.py scripts/validate_arch.py scripts/evaluate_arch.py
```

5. Commit the release changes.
6. Prefer a signed tag when local signing is configured:

```bash
git tag -s "v$(cat VERSION)" -m "ARCH v$(cat VERSION)"
```

If signing is not configured, use an annotated tag and record that limitation in the release provenance:

```bash
git tag -a "v$(cat VERSION)" -m "ARCH v$(cat VERSION)"
```

7. Push the release commit and tag:

```bash
git push origin main --tags
```

8. Create the GitHub release:

```bash
gh release create "v$(cat VERSION)" --title "ARCH v$(cat VERSION)" --notes-file /tmp/arch-release-notes.md
```

Use the matching section from `RELEASE_NOTES.md` as the notes file content.

9. Record release provenance in `docs/security/security-review.md` or the release notes:

- release version
- release commit SHA
- tag name and whether the tag is signed or annotated
- GitHub release URL
- CI run IDs for `main` and the release tag
- validation commands run locally
- pinned GitHub Action SHAs

## Local Install From A Release

```bash
curl -fsSL https://raw.githubusercontent.com/fhajjej-ship-it/ARCH/v0.6.0/scripts/install_codex_skill.sh | bash -s -- v0.6.0
```

## Local Install From A Checkout

```bash
ARCH_SOURCE_DIR="$PWD" bash scripts/install_codex_skill.sh
```
