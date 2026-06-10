"""
Folder watcher: organizes new files periodically by running the
organizer in a background thread. Low overhead: it just lists the
folder every ``interval`` seconds.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Callable

from organizer import MoveResult, organize


class Watcher:
    """Run ``organize`` in a loop on a daemon thread."""

    def __init__(
        self,
        folder: Path,
        interval: int,
        ignore_hidden: bool = True,
        custom: dict | None = None,
        on_event: Callable[[MoveResult], None] | None = None,
    ) -> None:
        self.folder = folder
        self.interval = max(1, int(interval))
        self.ignore_hidden = ignore_hidden
        self.custom = custom
        self.on_event = on_event
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                organize(
                    self.folder,
                    custom=self.custom,
                    ignore_hidden=self.ignore_hidden,
                    on_event=self.on_event,
                )
            except Exception as exc:  # noqa: BLE001
                if self.on_event is not None:
                    try:
                        self.on_event(MoveResult(
                            source=self.folder, destination=None,
                            category="-", success=False,
                            detail=f"watcher: {exc}",
                        ))
                    except Exception:  # noqa: BLE001
                        pass
            # Interruptible wait.
            self._stop.wait(self.interval)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="folder-cleaner-watcher", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval + 1)
            self._thread = None
