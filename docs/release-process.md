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
3. Run validation:

```bash
python3 scripts/validate_arch.py
python3 scripts/evaluate_arch.py
python3 scripts/evaluate_arch.py --write-baseline docs/evals/baseline-results.json
python3 -m py_compile arch/scripts/bootstrap_context.py scripts/validate_arch.py scripts/evaluate_arch.py
```

4. Commit the release changes.
5. Tag the commit:

```bash
git tag v$(cat VERSION)
git push origin main --tags
```

6. Create the GitHub release:

```bash
gh release create "v$(cat VERSION)" --title "ARCH v$(cat VERSION)" --notes-file /tmp/arch-release-notes.md
```

Use the matching section from `RELEASE_NOTES.md` as the notes file content.

## Local Install From A Release

```bash
git clone --branch v0.1.0 --depth 1 https://github.com/fhajjej-ship-it/ARCH.git
cd ARCH
mkdir -p ~/.codex/skills/arch
cp -R arch/. ~/.codex/skills/arch/
```
