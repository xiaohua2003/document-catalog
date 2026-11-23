"""Utilities for file discovery and path handling.
Uses relative paths and ignores symlinks outside the root directory.
"""
from pathlib import Path
from .errors import InputError

EXTENSIONS = frozenset({".md", ".txt"})


def check_root(root: Path) -> Path:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise InputError(f"not a directory: {root}")
    return root


def relative_key(root: Path, file: Path) -> str:
    try:
        return file.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise InputError(f"path escapes the chosen root: {file}") from exc


def supported(file: Path) -> bool:
    return file.suffix.lower() in EXTENSIONS


def iter_documents(root: Path):
    root = check_root(root)
    matches = []
    try:
        for file in root.rglob("*"):
            if file.is_file() and supported(file):
                try:
                    key = relative_key(root, file)
                except InputError:
                    continue
                matches.append((key, file))
    except OSError as exc:
        raise InputError(f"cannot list directory {root}: {exc}") from exc
    yield from sorted(matches, key=lambda item: item[0])
