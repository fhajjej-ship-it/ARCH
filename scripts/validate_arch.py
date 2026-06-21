#!/usr/bin/env python3
"""Validate the ARCH skill repo without external dependencies."""

from __future__ import annotations

import os
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CONTEXT_FILES = {
    "context/project-overview.md",
    "context/architecture-context.md",
    "context/ui-context.md",
    "context/code-standards.md",
    "context/ai-workflow-rules.md",
    "context/progress-tracker.md",
    "context/feature-specs/README.md",
    "context/feature-specs/00-feature-template.md",
}
RUN_TIMEOUT_SECONDS = 30
TEXT_FILE_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = [
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("Supabase service key", re.compile(r"\bsb_secret_[A-Za-z0-9]{20,}\b")),
    ("Stripe live secret", re.compile(r"\b(?:sk_live|rk_live)_[A-Za-z0-9]{20,}\b")),
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def run_arch_command(
    args: list[str],
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_SECONDS,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        fail(f"Command timed out after {RUN_TIMEOUT_SECONDS}s: {' '.join(args)}")
        raise AssertionError("unreachable") from exc


def parse_frontmatter(skill_md: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", skill_md, re.DOTALL)
    if not match:
        fail("arch/SKILL.md must start with YAML frontmatter")

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter


def validate_skill() -> None:
    skill_text = read(ROOT / "arch" / "SKILL.md")
    frontmatter = parse_frontmatter(skill_text)

    if set(frontmatter) != {"name", "description"}:
        fail("arch/SKILL.md frontmatter must contain only name and description")
    if frontmatter["name"] != "arch":
        fail("Skill name must be arch")
    description = frontmatter["description"]
    if not description or len(description) > 1024:
        fail("Skill description must be non-empty and at most 1024 characters")
    if "<" in description or ">" in description:
        fail("Skill description must not contain angle brackets")

    required_phrases = [
        "Ask exactly one question at a time",
        "confirmed architecture decision",
        "Do not leave confirmed decisions only in chat",
        "After each confirmed decision",
        "1. Recommended",
        "2. Second option",
        "3. Other",
        "Reply with 1, 2, or 3",
    ]
    missing = [phrase for phrase in required_phrases if phrase not in skill_text]
    if missing:
        fail(f"Missing required behavior phrase(s): {', '.join(missing)}")
    ok("Skill metadata and core behavior are valid")


def validate_agents_metadata() -> None:
    metadata = read(ROOT / "arch" / "agents" / "openai.yaml")
    for phrase in (
        'display_name: "ARCH"',
        'short_description: "Architect projects for AI coding agents"',
        'default_prompt: "Use $arch',
    ):
        if phrase not in metadata:
            fail(f"agents/openai.yaml missing: {phrase}")

    for relative_path in ("arch/assets/logo.svg", "arch/assets/logo-small.png"):
        if not (ROOT / relative_path).exists():
            fail(f"Missing metadata asset: {relative_path}")
    ok("Agent metadata is valid")


def validate_templates() -> None:
    template_root = ROOT / "arch" / "assets" / "context-template"
    missing = [
        path
        for path in EXPECTED_CONTEXT_FILES
        if not (template_root / Path(path).relative_to("context")).exists()
    ]
    if missing:
        fail(f"Missing context template(s): {', '.join(missing)}")

    for template in sorted(template_root.rglob("*.md")):
        if template.stat().st_size == 0:
            fail(f"Template is empty: {template.relative_to(ROOT)}")
    ok("Context templates are present")


def validate_bootstrap() -> None:
    script = ROOT / "arch" / "scripts" / "bootstrap_context.py"
    if not script.exists():
        fail("Missing arch/scripts/bootstrap_context.py")

    with tempfile.TemporaryDirectory() as tmp:
        result = run_arch_command([sys.executable, str(script), tmp])
        if result.returncode != 0:
            fail(f"bootstrap_context.py failed:\n{result.stderr}\n{result.stdout}")

        created = {
            str(path.relative_to(tmp))
            for path in Path(tmp).joinpath("context").rglob("*")
            if path.is_file()
        }
        missing = sorted(EXPECTED_CONTEXT_FILES - created)
        if missing:
            fail(f"Bootstrap did not create: {', '.join(missing)}")
    ok("Bootstrap script creates expected files")


def write_ready_context(context_root: Path) -> None:
    feature_root = context_root / "feature-specs"
    feature_root.mkdir(parents=True)
    (context_root / "project-overview.md").write_text(
        """# Project Overview

## Product

- Name: Ready Context
- One-sentence description: Validates ARCH handoff quality.
- Target user: solo developer
- Core job-to-be-done: confirm context is actionable.

## MVP Goal

Validate that context files contain concrete implementation guidance.

## Core User Flow

1. Developer runs ARCH.
2. Developer checks context.
3. Coding assistant starts the first feature.
4. Verification passes.

## In Scope For V1

- Context validation
- Feature spec readiness
- Verification guidance

## Out Of Scope For V1

- Runtime app generation
- Cloud deployment
- Billing

## Success Criteria

1. Required files exist.
2. Feature spec has verification.
3. No template placeholders remain.
""",
        encoding="utf-8",
    )
    (context_root / "architecture-context.md").write_text(
        """# Architecture Context

## Stack

| Layer | Technology | Role |
| --- | --- | --- |
| Script | Python standard library | Context validation |

## System Boundaries

- `arch/scripts/validate_context.py` - validates project context files.

## Data Model

### Issue

- path: context file path.
- message: actionable validation result.

## Storage Model

- Relational data: none.
- Files/artifacts: local Markdown context files.
- Cache/session state: none.

## Auth And Authorization

- Auth provider: none.
- User roles: local developer.
- Mutation rule: validation is read-only.

## Integrations

- None.

## Background Work

- None.

## Deployment

- Runtime: local Python.
- Hosting: none.
- Required environment variables: none.

## Invariants

1. Validation must not modify project files.
2. Missing required context files fail the check.
3. Feature specs must include verification steps.
""",
        encoding="utf-8",
    )
    (context_root / "ui-context.md").write_text(
        """# UI Context

## UX Principles

- Keep output scannable.
- Put failures before summaries.
- Use concrete file paths.

## Primary Navigation

- CLI output: validation report.

## Key Screens

### Terminal Report

- Goal: show whether context is ready.
- Primary action: fix listed issues.
- Empty state: report missing context.
- Loading state: not applicable for local script.
- Error state: print failing issue list.

## Responsive Behavior

- Mobile: not applicable.
- Tablet: not applicable.
- Desktop: terminal width should remain readable.

## Accessibility

- Keyboard: script is command-line only.
- Screen reader: plain text output.
- Color/contrast: no color required.
- Focus states: not applicable.

## Visual System

- Theme: terminal default.
- Typography: terminal default.
- Color use: none.
- Components: none.
""",
        encoding="utf-8",
    )
    (context_root / "code-standards.md").write_text(
        """# Code Standards

## General

- Use Python standard library.
- Keep validation deterministic.
- Return nonzero on failure.

## Language And Framework

- Python scripts should run with `python3`.

## API And Server Logic

- No server logic.

## Data

- Read local Markdown files only.

## Dependencies

- Do not add runtime dependencies.

## Testing And Verification

- Run `python3 arch/scripts/validate_context.py .`.
- Run JSON mode for automation.

## File Organization

- `arch/scripts/validate_context.py` - installed validator.
""",
        encoding="utf-8",
    )
    (context_root / "ai-workflow-rules.md").write_text(
        """# AI Workflow Rules

## How To Work

- Read context before implementation.
- Implement one feature spec at a time.
- Update progress after verification.

## Scoping Rules

- Keep changes tied to the active spec.

## Quality Rules

- Do not skip validation.

## Verification

- Run the context validator before starting implementation.

## Progress Updates

- Record completed checks in progress tracker.
""",
        encoding="utf-8",
    )
    (context_root / "progress-tracker.md").write_text(
        """# Progress Tracker

## Current Phase

- Hardening

## Current Goal

- Validate context readiness.

## Completed

- Context files drafted with concrete content.

## In Progress

- None

## Next Up

- Run first implementation feature.

## Open Questions

- None

## Architecture Decisions

- Use local Python validation.

## Verification Log

- 2026-06-21 - context doctor - pending
""",
        encoding="utf-8",
    )
    (feature_root / "README.md").write_text(
        """# Feature Specs

Feature specs are one focused implementation unit each.
""",
        encoding="utf-8",
    )
    (feature_root / "01-context-doctor.md").write_text(
        """# Feature 01: Context Doctor

## Goal

Validate ARCH context readiness.

## User Value

Developers know whether Codex can safely start implementation.

## Requirements

- Detect missing context files.
- Detect stale template placeholders.
- Require verification steps.

## Data And State

- Local Markdown context files.

## UX

- Happy path: print ready status.
- Empty state: report missing context folder.
- Loading state: not applicable.
- Error state: list actionable issues.

## Implementation Notes

- Use Python standard library only.
- Keep output deterministic.

## Out Of Scope

- Auto-fixing context content.

## Check When Done

- Run `python3 arch/scripts/validate_context.py .`.
""",
        encoding="utf-8",
    )


def validate_context_doctor() -> None:
    script = ROOT / "arch" / "scripts" / "validate_context.py"
    bootstrap = ROOT / "arch" / "scripts" / "bootstrap_context.py"
    if not script.exists():
        fail("Missing arch/scripts/validate_context.py")
    if not os.access(script, os.X_OK):
        fail("arch/scripts/validate_context.py must be executable")

    syntax = run_arch_command([sys.executable, "-m", "py_compile", str(script)])
    if syntax.returncode != 0:
        fail(f"validate_context.py does not compile:\n{syntax.stderr}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        templated_project = tmp_path / "templated"
        templated_project.mkdir()
        bootstrap_result = run_arch_command([sys.executable, str(bootstrap), str(templated_project)])
        if bootstrap_result.returncode != 0:
            fail(f"Bootstrap failed before context doctor test:\n{bootstrap_result.stderr}")
        result = run_arch_command([sys.executable, str(script), str(templated_project)])
        if result.returncode == 0:
            fail("Context doctor should fail on untouched template placeholders")
        if "stale placeholder" not in result.stdout:
            fail("Context doctor failure should mention stale placeholders")

        ready_project = tmp_path / "ready"
        ready_project.mkdir()
        write_ready_context(ready_project / "context")
        result = run_arch_command([sys.executable, str(script), str(ready_project), "--json"])
        if result.returncode != 0:
            fail(f"Context doctor should pass ready context:\n{result.stderr}\n{result.stdout}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            fail(f"Context doctor JSON output is invalid: {exc}")
        if payload.get("passed") is not True or payload.get("issue_count") != 0:
            fail("Context doctor JSON output should report a passing context")

    ok("Context doctor validates generated context readiness")


def validate_bootstrap_rejects_symlinks() -> None:
    script = ROOT / "arch" / "scripts" / "bootstrap_context.py"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        project = tmp_path / "project"
        project.mkdir()
        context = project / "context"
        context.mkdir()
        outside_file = tmp_path / "outside.md"
        outside_file.write_text("do-not-overwrite", encoding="utf-8")
        (context / "project-overview.md").symlink_to(outside_file)

        result = run_arch_command([sys.executable, str(script), str(project), "--force"])
        if result.returncode == 0:
            fail("bootstrap_context.py allowed a symlinked context file")
        if outside_file.read_text(encoding="utf-8") != "do-not-overwrite":
            fail("bootstrap_context.py overwrote a file outside the project")

        project_with_context_link = tmp_path / "project-with-context-link"
        project_with_context_link.mkdir()
        outside_context = tmp_path / "outside-context"
        outside_context.mkdir()
        (project_with_context_link / "context").symlink_to(
            outside_context,
            target_is_directory=True,
        )

        result = run_arch_command(
            [sys.executable, str(script), str(project_with_context_link)]
        )
        if result.returncode == 0:
            fail("bootstrap_context.py allowed context/ to be a symlink")
        if any(outside_context.iterdir()):
            fail("bootstrap_context.py wrote through a symlinked context directory")

    ok("Bootstrap script rejects symlink write escapes")


def validate_bootstrap_preserves_hardlink_targets() -> None:
    script = ROOT / "arch" / "scripts" / "bootstrap_context.py"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        project = tmp_path / "hardlink-project"
        context = project / "context"
        context.mkdir(parents=True)
        outside_file = tmp_path / "outside-hardlink.md"
        outside_file.write_text("do-not-overwrite", encoding="utf-8")
        target = context / "project-overview.md"
        os.link(outside_file, target)

        result = run_arch_command([sys.executable, str(script), str(project), "--force"])
        if result.returncode != 0:
            fail(f"bootstrap_context.py failed hardlink regression:\n{result.stderr}")
        if outside_file.read_text(encoding="utf-8") != "do-not-overwrite":
            fail("bootstrap_context.py truncated a hardlinked file outside the project")
        if target.read_text(encoding="utf-8") == "do-not-overwrite":
            fail("bootstrap_context.py did not replace the hardlinked context file")

    ok("Bootstrap force writes replace hardlinks instead of truncating them")


def validate_versioning() -> None:
    version = read(ROOT / "VERSION").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        fail("VERSION must be semantic version format X.Y.Z")

    release_notes = read(ROOT / "RELEASE_NOTES.md")
    if f"## v{version}" not in release_notes:
        fail(f"RELEASE_NOTES.md must include section for v{version}")
    ok(f"Version metadata is valid: v{version}")


def validate_eval_pack() -> None:
    required_paths = [
        ROOT / "docs" / "evals" / "README.md",
        ROOT / "docs" / "evals" / "scenarios.json",
        ROOT / "docs" / "evals" / "golden-transcripts.json",
        ROOT / "docs" / "evals" / "baseline-results.json",
        ROOT / "scripts" / "evaluate_arch.py",
    ]
    for path in required_paths:
        if not path.exists():
            fail(f"Missing eval artifact: {path.relative_to(ROOT)}")
    ok("Eval pack files are present")


def validate_eval_output_path_safety() -> None:
    script = ROOT / "scripts" / "evaluate_arch.py"
    with tempfile.TemporaryDirectory() as tmp:
        outside_path = Path(tmp) / "outside-baseline.json"
        result = run_arch_command(
            [sys.executable, str(script), "--write-baseline", str(outside_path)]
        )
        if result.returncode == 0:
            fail("evaluate_arch.py allowed --write-baseline outside the repository")
        if outside_path.exists():
            fail("evaluate_arch.py wrote a baseline outside the repository")
    ok("Eval baseline writes are confined to the repository")


def validate_installer() -> None:
    script = ROOT / "scripts" / "install_codex_skill.sh"
    if not script.exists():
        fail("Missing scripts/install_codex_skill.sh")
    if not os.access(script, os.X_OK):
        fail("scripts/install_codex_skill.sh must be executable")

    installer_text = script.read_text(encoding="utf-8")
    for phrase in (
        "ARCH_INSTALL_DIR",
        "ARCH_SOURCE_DIR",
        "backup",
        ".arch-version",
        "Restart Codex",
    ):
        if phrase not in installer_text:
            fail(f"Installer missing required behavior phrase: {phrase}")

    syntax = run_arch_command(["bash", "-n", str(script)])
    if syntax.returncode != 0:
        fail(f"Installer shell syntax failed:\n{syntax.stderr}")

    version = f"v{read(ROOT / 'VERSION').strip()}"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        install_dir = tmp_path / "codex" / "skills" / "arch"
        env = os.environ.copy()
        env.update(
            {
                "ARCH_INSTALL_DIR": str(install_dir),
                "ARCH_SOURCE_DIR": str(ROOT),
                "HOME": str(tmp_path / "home"),
            }
        )

        result = run_arch_command(["bash", str(script)], env=env)
        if result.returncode != 0:
            fail(f"Installer local-source install failed:\n{result.stderr}\n{result.stdout}")
        if not (install_dir / "SKILL.md").exists():
            fail("Installer did not copy SKILL.md")
        if (install_dir / ".arch-version").read_text(encoding="utf-8").strip() != version:
            fail("Installer did not write the installed ARCH version")

        marker = install_dir / "old-marker.txt"
        marker.write_text("previous install", encoding="utf-8")
        result = run_arch_command(["bash", str(script), version], env=env)
        if result.returncode != 0:
            fail(f"Installer update failed:\n{result.stderr}\n{result.stdout}")
        backup_dirs = sorted(install_dir.parent.glob("arch.backup.*"))
        if not backup_dirs:
            fail("Installer did not create a backup for an existing install")
        if not any((backup / "old-marker.txt").exists() for backup in backup_dirs):
            fail("Installer backup did not preserve the previous install")

    ok("Codex skill installer is valid")


def validate_ci_security() -> None:
    workflow = read(ROOT / ".github" / "workflows" / "ci.yml")
    if re.search(r"(?m)^\s*pull_request_target\s*:", workflow):
        fail("CI must not use pull_request_target for untrusted changes")
    if not re.search(r"(?m)^permissions:\s*$", workflow):
        fail("CI must declare top-level permissions")
    if not re.search(r"(?m)^\s+contents:\s+read\s*$", workflow):
        fail("CI permissions must limit contents to read")
    unpinned_actions = [
        line.strip()
        for line in workflow.splitlines()
        if re.match(r"uses:\s+.+@", line.strip())
        and not re.match(r"uses:\s+[^@\s]+@[0-9a-f]{40}(?:\s+#.*)?$", line.strip())
    ]
    if unpinned_actions:
        fail("CI actions must be pinned to commit SHAs: " + ", ".join(unpinned_actions))
    ok("CI workflow permissions are constrained")


def validate_secret_hygiene() -> None:
    findings: list[str] = []
    ignored_dirs = {".git", "__pycache__"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in ignored_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_FILE_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {label}")

    if findings:
        fail("Potential committed secret(s): " + ", ".join(findings))
    ok("No high-confidence committed secrets detected")


def validate_security_docs() -> None:
    for relative_path in (
        "SECURITY.md",
        ".github/CODEOWNERS",
        "docs/security/threat-model.md",
        "docs/security/security-review.md",
    ):
        path = ROOT / relative_path
        if not path.exists():
            fail(f"Missing security documentation: {relative_path}")
        if not path.read_text(encoding="utf-8").strip():
            fail(f"Security documentation is empty: {relative_path}")
    security_policy = read(ROOT / "SECURITY.md")
    for phrase in (
        "Reporting A Vulnerability",
        "GitHub private vulnerability reporting",
        "Release Security",
    ):
        if phrase not in security_policy:
            fail(f"SECURITY.md missing required section or phrase: {phrase}")
    codeowners = read(ROOT / ".github" / "CODEOWNERS")
    for phrase in (
        "/.github/workflows/ci.yml @fhajjej-ship-it",
        "/arch/scripts/bootstrap_context.py @fhajjej-ship-it",
        "/arch/scripts/validate_context.py @fhajjej-ship-it",
        "/scripts/install_codex_skill.sh @fhajjej-ship-it",
        "/scripts/validate_arch.py @fhajjej-ship-it",
    ):
        if phrase not in codeowners:
            fail(f"CODEOWNERS missing sensitive path owner: {phrase}")
    release_process = read(ROOT / "docs" / "release-process.md")
    for phrase in (
        "Keep `.github/workflows/ci.yml` pinned to full 40-character commit SHAs.",
        "bash -n scripts/install_codex_skill.sh",
        "ARCH_SOURCE_DIR=\"$PWD\" bash scripts/install_codex_skill.sh",
        "git tag -s",
        "Record release provenance",
    ):
        if phrase not in release_process:
            fail(f"Release process missing security provenance requirement: {phrase}")
    ok("Security documentation is present")


def main() -> int:
    validate_skill()
    validate_agents_metadata()
    validate_templates()
    validate_bootstrap()
    validate_context_doctor()
    validate_bootstrap_rejects_symlinks()
    validate_bootstrap_preserves_hardlink_targets()
    validate_versioning()
    validate_eval_pack()
    validate_eval_output_path_safety()
    validate_installer()
    validate_ci_security()
    validate_secret_hygiene()
    validate_security_docs()
    ok("ARCH validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
