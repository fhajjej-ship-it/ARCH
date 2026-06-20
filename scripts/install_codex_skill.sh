#!/usr/bin/env bash
set -euo pipefail

REPO="${ARCH_REPO:-fhajjej-ship-it/ARCH}"
REQUESTED_VERSION="${1:-${ARCH_VERSION:-latest}}"

if [ -z "${HOME:-}" ]; then
  echo "error: HOME is required" >&2
  exit 1
fi

INSTALL_DIR="${ARCH_INSTALL_DIR:-${HOME}/.codex/skills/arch}"
TMP_BASE="${TMPDIR:-/tmp}"

usage() {
  cat <<'USAGE'
Install or update the ARCH Codex skill.

Usage:
  install_codex_skill.sh [version|latest]

Examples:
  install_codex_skill.sh
  install_codex_skill.sh v0.3.0
  ARCH_INSTALL_DIR=/tmp/arch-skill install_codex_skill.sh v0.3.0

Environment:
  ARCH_VERSION       Version to install when no argument is provided.
  ARCH_INSTALL_DIR   Destination skill directory. Defaults to ~/.codex/skills/arch.
  ARCH_REPO          GitHub repo. Defaults to fhajjej-ship-it/ARCH.
  ARCH_SOURCE_DIR    Local ARCH checkout or extracted release root for offline installs.
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

normalize_version() {
  case "$1" in
    latest)
      echo "latest"
      ;;
    v[0-9]*.[0-9]*.[0-9]*)
      echo "$1"
      ;;
    [0-9]*.[0-9]*.[0-9]*)
      echo "v$1"
      ;;
    *)
      die "version must be latest or a semantic version like v0.3.0"
      ;;
  esac
}

resolve_latest_version() {
  require_cmd curl
  latest_url="$(curl -fsSL -o /dev/null -w "%{url_effective}" "https://github.com/${REPO}/releases/latest")"
  latest_tag="${latest_url##*/}"
  case "$latest_tag" in
    v[0-9]*.[0-9]*.[0-9]*)
      echo "$latest_tag"
      ;;
    *)
      die "could not resolve latest release tag from ${latest_url}"
      ;;
  esac
}

read_release_version() {
  release_root="$1"
  version_file="${release_root}/VERSION"
  [ -f "$version_file" ] || die "missing VERSION in release root: ${release_root}"
  version="$(tr -d '[:space:]' <"$version_file")"
  [ -n "$version" ] || die "empty VERSION in release root: ${release_root}"
  echo "v${version#v}"
}

prepare_release_root() {
  requested="$(normalize_version "$REQUESTED_VERSION")"

  if [ -n "${ARCH_SOURCE_DIR:-}" ]; then
    release_root="$(cd "$ARCH_SOURCE_DIR" && pwd -P)"
    source_version="$(read_release_version "$release_root")"
    if [ "$requested" != "latest" ] && [ "$source_version" != "$requested" ]; then
      die "ARCH_SOURCE_DIR is ${source_version}, but requested ${requested}"
    fi
    version="$source_version"
    echo "${release_root}|${version}"
    return
  fi

  if [ "${requested}" = "latest" ]; then
    version="$(resolve_latest_version)"
  else
    version="$requested"
  fi

  require_cmd curl
  require_cmd tar
  require_cmd mktemp

  tmp_dir="$(mktemp -d "${TMP_BASE%/}/arch-install.XXXXXX")"
  archive_path="${tmp_dir}/arch.tar.gz"
  archive_url="https://github.com/${REPO}/archive/refs/tags/${version}.tar.gz"

  curl -fsSL "$archive_url" -o "$archive_path"
  tar -xzf "$archive_path" -C "$tmp_dir"
  release_root="$(find "$tmp_dir" -mindepth 1 -maxdepth 1 -type d | sort | head -n 1)"
  [ -n "$release_root" ] || die "release archive did not contain a root directory"

  source_version="$(read_release_version "$release_root")"
  [ "$source_version" = "$version" ] || die "release archive version ${source_version} did not match ${version}"

  echo "${release_root}|${version}|${tmp_dir}"
}

restore_backup() {
  if [ -n "${backup_dir:-}" ] && { [ -e "$backup_dir" ] || [ -L "$backup_dir" ]; }; then
    rm -rf "$INSTALL_DIR"
    mv "$backup_dir" "$INSTALL_DIR"
  fi
}

install_skill() {
  release_root="$1"
  version="$2"
  skill_src="${release_root}/arch"

  [ -d "$skill_src" ] || die "release does not contain arch/ skill directory"
  [ -f "${skill_src}/SKILL.md" ] || die "release does not contain arch/SKILL.md"

  case "$INSTALL_DIR" in
    ""|"/"|"$HOME"|"$HOME/")
      die "refusing unsafe install directory: ${INSTALL_DIR}"
      ;;
  esac

  parent_dir="$(dirname "$INSTALL_DIR")"
  mkdir -p "$parent_dir"

  timestamp="$(date +%Y%m%d%H%M%S)"
  backup_dir=""
  if [ -e "$INSTALL_DIR" ] || [ -L "$INSTALL_DIR" ]; then
    backup_base="${INSTALL_DIR}.backup.${timestamp}"
    backup_dir="$backup_base"
    backup_suffix=0
    while [ -e "$backup_dir" ] || [ -L "$backup_dir" ]; do
      backup_suffix=$((backup_suffix + 1))
      backup_dir="${backup_base}.${backup_suffix}"
    done
    if [ -e "$backup_dir" ] || [ -L "$backup_dir" ]; then
      die "backup path already exists: ${backup_dir}"
    fi
    mv "$INSTALL_DIR" "$backup_dir"
  fi

  if ! mkdir -p "$INSTALL_DIR"; then
    restore_backup
    die "could not create install directory: ${INSTALL_DIR}"
  fi

  if ! cp -R "${skill_src}/." "$INSTALL_DIR/"; then
    restore_backup
    die "could not copy ARCH skill into ${INSTALL_DIR}"
  fi

  if ! printf "%s\n" "$version" >"${INSTALL_DIR}/.arch-version"; then
    restore_backup
    die "could not write installed version marker"
  fi

  echo "Installed ARCH ${version} for Codex"
  echo "Install dir: ${INSTALL_DIR}"
  if [ -n "$backup_dir" ]; then
    echo "Backup: ${backup_dir}"
  else
    echo "Backup: none"
  fi
  echo "Restart Codex so the skill is discovered."
}

main() {
  case "${1:-}" in
    -h|--help)
      usage
      exit 0
      ;;
  esac

  prepared="$(prepare_release_root)"
  release_root="$(printf "%s" "$prepared" | cut -d "|" -f 1)"
  version="$(printf "%s" "$prepared" | cut -d "|" -f 2)"
  tmp_dir="$(printf "%s" "$prepared" | cut -d "|" -f 3-)"

  trap 'if [ -n "${tmp_dir:-}" ] && [ -d "$tmp_dir" ]; then rm -rf "$tmp_dir"; fi' EXIT
  install_skill "$release_root" "$version"
}

main "$@"
