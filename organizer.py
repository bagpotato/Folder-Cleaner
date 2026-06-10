"""
Core organizer logic. Detects files in the target folder, classifies
them by extension and moves them into per-category subfolders. Handles
duplicates, in-use files, permission errors and mixed-case extensions.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from categories import CATEGORIES, FALLBACK_CATEGORY, get_category


@dataclass
class MoveResult:
    source: Path
    destination: Path | None
    category: str
    success: bool
    detail: str = ""


def _resolve_duplicate(destination: Path) -> Path:
    """If ``destination`` already exists, return an alternative ``(n)`` path.

    Never overwrites. ``file.txt`` -> ``file (1).txt`` -> ...
    """
    if not destination.exists():
        return destination

    parent = destination.parent
    name = destination.name
    stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _iter_files(folder: Path, ignore_hidden: bool) -> Iterable[Path]:
    """Iterate files (not folders) at the root of ``folder``.

    Skips subfolders already created by the app itself (those matching
    known categories plus the fallback category).
    """
    reserved = set(CATEGORIES.keys()) | {FALLBACK_CATEGORY}

    for entry in folder.iterdir():
        if not entry.is_file():
            continue
        if entry.name in reserved:
            continue
        if ignore_hidden and entry.name.startswith("."):
            continue
        yield entry


def organize(
    folder: Path,
    custom: dict | None = None,
    ignore_hidden: bool = True,
    on_event: Callable[[MoveResult], None] | None = None,
) -> list[MoveResult]:
    """Run a single organizing pass. Returns the list of move results."""
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Invalid folder: {folder}")

    results: list[MoveResult] = []

    for file_path in _iter_files(folder, ignore_hidden):
        category = get_category(file_path.suffix, custom)
        dest_dir = folder / category
        dest = _resolve_duplicate(dest_dir / file_path.name)
        extra_detail = ""

        try:
            dest_dir.mkdir(exist_ok=True)
            shutil.move(str(file_path), str(dest))
        except PermissionError as exc:
            result = MoveResult(
                source=file_path, destination=None, category=category,
                success=False, detail=f"permission denied: {exc}",
            )
        except OSError as exc:
            errno = getattr(exc, "errno", None)
            if errno in (13, 32):  # EACCES on POSIX / ERROR_SHARING_VIOLATION on Windows
                result = MoveResult(
                    source=file_path, destination=None, category=category,
                    success=False, detail=f"file locked or no permission: {exc}",
                )
            else:
                result = MoveResult(
                    source=file_path, destination=None, category=category,
                    success=False, detail=f"I/O error: {exc}",
                )
        else:
            if dest != (dest_dir / file_path.name):
                extra_detail = " (renamed due to duplicate)"
            result = MoveResult(
                source=file_path, destination=dest, category=category,
                success=True, detail=extra_detail.strip(),
            )

        results.append(result)
        if on_event is not None:
            try:
                on_event(result)
            except Exception:  # noqa: BLE001
                # A broken callback must not stop the organization pass.
                pass

    return results
