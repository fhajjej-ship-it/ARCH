#!/usr/bin/env python3
"""Create missing ARCH context files in a project."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_templates(project_path: Path, force: bool) -> tuple[list[Path], list[Path]]:
    skill_dir = Path(__file__).resolve().parents[1]
    template_dir = skill_dir / "assets" / "context-template"
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    target_context = project_path / "context"
    created: list[Path] = []
    skipped: list[Path] = []

    for source in sorted(template_dir.rglob("*")):
        if source.is_dir():
            continue

        relative_path = source.relative_to(template_dir)
        target = target_context / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists() and not force:
            skipped.append(target)
            continue

        shutil.copy2(source, target)
        created.append(target)

    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create missing ARCH context files from bundled templates.",
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="Project root where context/ should be created. Defaults to cwd.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing context files. Use only after reading them.",
    )
    args = parser.parse_args()

    project_path = Path(args.project_path).expanduser().resolve()
    if not project_path.exists():
        parser.error(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        parser.error(f"Project path is not a directory: {project_path}")

    created, skipped = copy_templates(project_path, args.force)

    print(f"Project: {project_path}")
    print(f"Created/updated: {len(created)}")
    for path in created:
        print(f"  + {path.relative_to(project_path)}")

    if skipped:
        print(f"Skipped existing: {len(skipped)}")
        for path in skipped:
            print(f"  = {path.relative_to(project_path)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
