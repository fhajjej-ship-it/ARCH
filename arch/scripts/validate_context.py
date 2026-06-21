#!/usr/bin/env python3
"""Validate an ARCH-generated context folder."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_CONTEXT_FILES = (
    "project-overview.md",
    "architecture-context.md",
    "ui-context.md",
    "code-standards.md",
    "ai-workflow-rules.md",
    "progress-tracker.md",
    "feature-specs/README.md",
)
REQUIRED_SECTIONS = {
    "project-overview.md": (
        "## Product",
        "## MVP Goal",
        "## Core User Flow",
        "## In Scope For V1",
        "## Out Of Scope For V1",
        "## Success Criteria",
    ),
    "architecture-context.md": (
        "## Stack",
        "## System Boundaries",
        "## Data Model",
        "## Auth And Authorization",
        "## Deployment",
        "## Invariants",
    ),
    "ui-context.md": (
        "## UX Principles",
        "## Key Screens",
        "## Responsive Behavior",
        "## Accessibility",
    ),
    "code-standards.md": (
        "## General",
        "## Testing And Verification",
        "## File Organization",
    ),
    "ai-workflow-rules.md": (
        "## How To Work",
        "## Scoping Rules",
        "## Verification",
    ),
    "progress-tracker.md": (
        "## Current Phase",
        "## Current Goal",
        "## Next Up",
        "## Open Questions",
        "## Architecture Decisions",
        "## Verification Log",
    ),
}
FEATURE_REQUIRED_SECTIONS = (
    "## Goal",
    "## Requirements",
    "## Implementation Notes",
    "## Check When Done",
)
PLACEHOLDER_WORDS = re.compile(r"\b(?:TODO|TBD|PLACEHOLDER)\b", re.IGNORECASE)
BRACKET_PLACEHOLDER = re.compile(r"\[[A-Za-z0-9][A-Za-z0-9 _/.,:-]{1,80}\]")


@dataclass(frozen=True)
class Issue:
    path: str
    message: str


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def context_path(path: Path, context_root: Path) -> str:
    return f"context/{relative(path, context_root)}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_heading(text: str, heading: str) -> bool:
    return bool(re.search(rf"(?m)^{re.escape(heading)}\s*$", text))


def has_non_placeholder_bullet(text: str, heading: str) -> bool:
    lines = text.splitlines()
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            return False
        if in_section and re.match(r"^\s*[-*]\s+\S", line):
            if not contains_placeholder(line):
                return True
    return False


def contains_placeholder(line: str) -> bool:
    if PLACEHOLDER_WORDS.search(line):
        return True
    if "](" in line:
        return False
    return bool(BRACKET_PLACEHOLDER.search(line))


def find_placeholders(text: str) -> Iterable[tuple[int, str]]:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if contains_placeholder(line):
            yield line_number, line.strip()


def validate_markdown_file(path: Path, context_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    rel = relative(path, context_root)
    display_path = context_path(path, context_root)
    text = read_text(path)
    if not text.strip():
        return [Issue(display_path, "file is empty")]

    for line_number, line in find_placeholders(text):
        issues.append(
            Issue(display_path, f"stale placeholder on line {line_number}: {line}")
        )

    for heading in REQUIRED_SECTIONS.get(rel, ()):
        if not has_heading(text, heading):
            issues.append(Issue(display_path, f"missing required section: {heading}"))

    return issues


def validate_feature_spec(path: Path, context_root: Path) -> list[Issue]:
    issues: list[Issue] = validate_markdown_file(path, context_root)
    display_path = context_path(path, context_root)
    text = read_text(path)

    for heading in FEATURE_REQUIRED_SECTIONS:
        if not has_heading(text, heading):
            issues.append(
                Issue(display_path, f"missing required feature section: {heading}")
            )

    if has_heading(text, "## Check When Done") and not has_non_placeholder_bullet(
        text,
        "## Check When Done",
    ):
        issues.append(
            Issue(display_path, "feature spec needs a concrete verification bullet")
        )

    return issues


def validate_context(project_path: Path) -> tuple[Path, list[Issue]]:
    context_root = project_path / "context"
    issues: list[Issue] = []

    if not context_root.exists():
        return context_root, [Issue("context", "context folder is missing")]
    if not context_root.is_dir():
        return context_root, [Issue("context", "context path is not a directory")]

    for required in REQUIRED_CONTEXT_FILES:
        path = context_root / required
        if not path.exists():
            issues.append(Issue(f"context/{required}", "required file is missing"))
            continue
        if not path.is_file():
            issues.append(Issue(f"context/{required}", "required path is not a file"))
            continue
        issues.extend(validate_markdown_file(path, context_root))

    feature_root = context_root / "feature-specs"
    feature_specs = [
        path
        for path in sorted(feature_root.glob("*.md"))
        if path.name not in {"README.md", "00-feature-template.md"}
    ]
    if not feature_specs:
        issues.append(
            Issue(
                "context/feature-specs",
                "at least one buildable feature spec is required",
            )
        )
    for feature_spec in feature_specs:
        issues.extend(validate_feature_spec(feature_spec, context_root))

    return context_root, issues


def print_text_report(project_path: Path, context_root: Path, issues: list[Issue]) -> None:
    print(f"Project: {project_path}")
    print(f"Context: {context_root}")
    if not issues:
        print("[OK] ARCH context is ready for a coding assistant")
        return

    print(f"[FAIL] ARCH context has {len(issues)} issue(s)")
    for issue in issues:
        print(f"  - {issue.path}: {issue.message}")


def print_json_report(project_path: Path, context_root: Path, issues: list[Issue]) -> None:
    payload = {
        "passed": not issues,
        "project_path": str(project_path),
        "context_path": str(context_root),
        "issue_count": len(issues),
        "issues": [
            {
                "path": issue.path,
                "message": issue.message,
            }
            for issue in issues
        ],
    }
    print(json.dumps(payload, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that an ARCH context folder is ready for agent handoff.",
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root containing context/. Defaults to cwd.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON.",
    )
    args = parser.parse_args()

    project_path = Path(args.project_path).expanduser().resolve()
    if not project_path.exists():
        parser.error(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        parser.error(f"Project path is not a directory: {project_path}")

    context_root, issues = validate_context(project_path)
    if args.json:
        print_json_report(project_path, context_root, issues)
    else:
        print_text_report(project_path, context_root, issues)

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
