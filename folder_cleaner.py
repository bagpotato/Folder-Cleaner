"""
Entry point for the Folder Cleaner CLI.

Usage:
    python folder_cleaner.py                    # Manual mode (one pass)
    python folder_cleaner.py --watch            # Watch mode
    python folder_cleaner.py --config path.json # Use a custom config file
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path

from categories import get_category
from logger import configure_logger
from organizer import MoveResult, organize
from paths import resolve_target_folder
from watcher import Watcher


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.json"


def load_config(path: Path) -> dict:
    """Load the JSON config; return defaults if the file does not exist."""
    if not path.exists():
        return {
            "target_folder": "auto",
            "auto_mode": False,
            "watch_interval": 10,
            "log_file": str(BASE_DIR / "folder_cleaner.log"),
            "log_level": "INFO",
            "ignore_hidden": True,
            "custom_categories": {},
        }
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def handle_result(logger, result: MoveResult) -> None:
    if result.success:
        msg = f"Moved: {result.source.name} -> {result.category}/"
        if result.destination and result.destination.name != result.source.name:
            msg += f" (renamed to {result.destination.name})"
        logger.info(msg)
    else:
        logger.error("Not moved: %s | category=%s | %s",
                     result.source, result.category, result.detail)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Folder Cleaner")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH,
                        help="Path to a JSON config file")
    parser.add_argument("--watch", action="store_true",
                        help="Watch the folder and organize new files continuously")
    parser.add_argument("--interval", type=int, default=None,
                        help="Seconds between passes in watch mode")
    parser.add_argument("--category", type=str, default=None,
                        help="Print the category for an extension and exit")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error reading config '{args.config}': {exc}", file=sys.stderr)
        return 2

    logger = configure_logger(
        "folder_cleaner",
        config.get("log_file", BASE_DIR / "folder_cleaner.log"),
        config.get("log_level", "INFO"),
    )

    if args.category is not None:
        custom = config.get("custom_categories") or {}
        print(get_category(args.category, custom))
        return 0

    try:
        target = resolve_target_folder(config)
    except (FileNotFoundError, NotADirectoryError) as exc:
        logger.error(str(exc))
        return 1

    custom = config.get("custom_categories") or {}
    ignore_hidden = bool(config.get("ignore_hidden", True))
    interval = args.interval or int(config.get("watch_interval", 10))
    watch_mode = args.watch or bool(config.get("auto_mode", False))

    logger.info("Target folder: %s", target)
    logger.info("Mode: %s", "watch" if watch_mode else "manual")

    if not watch_mode:
        results = organize(
            target,
            custom=custom,
            ignore_hidden=ignore_hidden,
            on_event=lambda r: handle_result(logger, r),
        )
        moved = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        logger.info("Pass complete. Moved: %d | Skipped: %d", moved, failed)
        return 0

    watcher = Watcher(
        folder=target,
        interval=interval,
        ignore_hidden=ignore_hidden,
        custom=custom,
        on_event=lambda r: handle_result(logger, r),
    )

    def _shutdown(_signum, _frame):
        logger.info("Shutdown signal received. Stopping watcher...")
        watcher.stop()
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, _shutdown)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, _shutdown)
    except (ValueError, OSError):
        # In some environments (e.g. secondary threads) signals are unavailable.
        pass

    watcher.start()
    logger.info("Watcher active. Press Ctrl+C to stop.")
    try:
        # Keep the main thread alive without burning CPU.
        while True:
            if hasattr(signal, "pause"):
                signal.pause()
            else:
                import time
                time.sleep(1)
    except KeyboardInterrupt:
        _shutdown(0, None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
