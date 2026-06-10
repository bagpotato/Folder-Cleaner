"""Basic tests (no external dependencies). Run with:
    python -m unittest test_folder_cleaner.py
"""

from __future__ import annotations

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from categories import get_category
from organizer import _resolve_duplicate, organize


class TestCategories(unittest.TestCase):
    def test_known_extensions(self):
        self.assertEqual(get_category(".pdf"), "Documents")
        self.assertEqual(get_category(".PNG"), "Images")
        self.assertEqual(get_category(".Mp4"), "Videos")

    def test_unknown_extension(self):
        self.assertEqual(get_category(".xyz123"), "Other")

    def test_empty_extension(self):
        self.assertEqual(get_category(""), "Other")

    def test_custom_overrides_default(self):
        self.assertEqual(get_category(".pdf", {".pdf": "Work"}), "Work")


class TestDuplicates(unittest.TestCase):
    def test_no_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            destination = base / "file.txt"
            self.assertEqual(_resolve_duplicate(destination), destination)

    def test_incremental_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "file.txt").write_text("a", encoding="utf-8")
            new = _resolve_duplicate(base / "file.txt")
            self.assertEqual(new, base / "file (1).txt")
            new.write_text("b", encoding="utf-8")
            another = _resolve_duplicate(base / "file.txt")
            self.assertEqual(another, base / "file (2).txt")


class TestOrganize(unittest.TestCase):
    def test_moves_by_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "a.pdf").write_text("pdf", encoding="utf-8")
            (base / "b.PNG").write_text("png", encoding="utf-8")
            (base / "c.mp3").write_text("mp3", encoding="utf-8")
            results = organize(base, ignore_hidden=False)
            moved = {r.source.name: r.destination for r in results if r.success}
            self.assertEqual(moved["a.pdf"].parent.name, "Documents")
            self.assertEqual(moved["b.PNG"].parent.name, "Images")
            self.assertEqual(moved["c.mp3"].parent.name, "Audio")

    def test_ignores_category_subfolders(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "Documents").mkdir()
            (base / "Documents" / "existing.pdf").write_text("x", encoding="utf-8")
            results = organize(base, ignore_hidden=False)
            self.assertEqual(results, [])

    def test_ignores_hidden_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / ".hidden.pdf").write_text("x", encoding="utf-8")
            results = organize(base, ignore_hidden=True)
            self.assertEqual(results, [])
            results2 = organize(base, ignore_hidden=False)
            self.assertEqual(len(results2), 1)

    def test_duplicate_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "Documents").mkdir()
            (base / "Documents" / "doc.pdf").write_text("dest", encoding="utf-8")
            (base / "doc.pdf").write_text("src", encoding="utf-8")
            results = organize(base, ignore_hidden=False)
            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].success)
            self.assertEqual(results[0].destination.name, "doc (1).pdf")


if __name__ == "__main__":
    unittest.main()
