"""
Cross-platform detection of special folders (Downloads, Home).
Compatible with Windows, Linux and macOS.
"""

from __future__ import annotations

import os
from pathlib import Path


def _expand(path: str) -> Path:
    """Expand environment variables and ``~`` and return an absolute Path."""
    return Path(os.path.expandvars(os.path.expanduser(path))).resolve()


def get_home() -> Path:
    """Return the current user's home folder."""
    return Path(os.path.expanduser("~")).resolve()


def get_downloads() -> Path:
    """Detect the user's Downloads folder based on the operating system.

    Windows: uses the ``User Shell Folders`` registry entry (or
    ``{USERPROFILE}\\Downloads`` as fallback). Linux/macOS: uses
    ``$XDG_DOWNLOAD_DIR`` or ``~/Downloads``.
    """
    home = get_home()

    if os.name == "nt":
        try:
            import winreg  # type: ignore
            with winreg.OpenKey(  # type: ignore
                winreg.HKEY_CURRENT_USER,  # type: ignore
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                downloads, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")  # type: ignore
            path = _expand(downloads)
            if path.exists():
                return path
        except (OSError, ImportError, ValueError):
            pass
        return home / "Downloads"

    # Linux and macOS
    xdg_downloads = os.environ.get("XDG_DOWNLOAD_DIR")
    if xdg_downloads:
        path = _expand(xdg_downloads)
        if path.exists():
            return path

    for candidate in ("Downloads",):
        path = home / candidate
        if path.exists():
            return path

    return home / "Downloads"


def resolve_target_folder(config: dict) -> Path:
    """Resolve the target folder from the configuration.

    ``"auto"`` (or empty string) uses the OS-level auto-detection.
    Any other value is treated as a path and expanded.
    """
    value = (config.get("target_folder") or "auto").strip()
    if not value or value.lower() == "auto":
        return get_downloads()

    path = _expand(value)
    if not path.exists():
        raise FileNotFoundError(f"Target folder does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    return path
