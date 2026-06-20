#!/usr/bin/env python3
"""Validate the ARCH skill repo without external dependencies."""

from __future__ import annotations

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


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"[OK] {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


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
        result = subprocess.run(
            [sys.executable, str(script), tmp],
            check=False,
            capture_output=True,
            text=True,
        )
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


def validate_versioning() -> None:
    version = read(ROOT / "VERSION").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        fail("VERSION must be semantic version format X.Y.Z")

    release_notes = read(ROOT / "RELEASE_NOTES.md")
    if f"## v{version}" not in release_notes:
        fail(f"RELEASE_NOTES.md must include section for v{version}")
    ok(f"Version metadata is valid: v{version}")


def main() -> int:
    validate_skill()
    validate_agents_metadata()
    validate_templates()
    validate_bootstrap()
    validate_versioning()
    ok("ARCH validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
