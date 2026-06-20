#!/usr/bin/env python3
"""Create missing ARCH context files in a project."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


COPY_CHUNK_SIZE = 64 * 1024


def reject_symlink_components(path: Path, root: Path) -> None:
    """Refuse to operate through symlinks inside the target project."""
    relative_parts = path.relative_to(root).parts
    current = root
    for part in relative_parts:
        current = current / part
        if current.is_symlink():
            raise RuntimeError(f"Refusing to write through symlink: {current}")


def open_new_file_for_write(target: Path) -> object:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    try:
        fd = os.open(target, flags, 0o644)
    except OSError as exc:
        if target.is_symlink():
            raise RuntimeError(f"Refusing to overwrite symlink: {target}") from exc
        raise
    return os.fdopen(fd, "wb")


def write_template_file(source: Path, target: Path, force: bool) -> None:
    temp_path: Path | None = None
    for attempt in range(100):
        candidate = target.with_name(f".{target.name}.tmp.{os.getpid()}.{attempt}")
        try:
            dst = open_new_file_for_write(candidate)
        except FileExistsError:
            continue
        temp_path = candidate
        break
    else:
        raise RuntimeError(f"Could not create temporary file near: {target}")

    try:
        with dst:
            src = source.open("rb")
            with src:
                while True:
                    chunk = src.read(COPY_CHUNK_SIZE)
                    if not chunk:
                        break
                    dst.write(chunk)

        if not force and (target.exists() or target.is_symlink()):
            raise RuntimeError(f"Refusing to overwrite existing file: {target}")
        os.replace(temp_path, target)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


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
        reject_symlink_components(target.parent, project_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        reject_symlink_components(target, project_path)

        if target.exists() and not force:
            skipped.append(target)
            continue

        write_template_file(source, target, force)
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

    try:
        created, skipped = copy_templates(project_path, args.force)
    except RuntimeError as exc:
        parser.error(str(exc))

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
