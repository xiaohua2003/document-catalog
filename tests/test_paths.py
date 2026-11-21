import tempfile
import unittest
from pathlib import Path
from doccatalog.paths import iter_documents, relative_key
from doccatalog.errors import InputError


class PathTest(unittest.TestCase):
    def test_extension_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub").mkdir()
            (root / "sub" / "a.md").write_text("hello")
            (root / "b.txt").write_text("world")
            (root / "c.bin").write_text("no")
            self.assertEqual([key for key, _ in iter_documents(root)], ["b.txt", "sub/a.md"])

    def test_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            root.mkdir()
            with self.assertRaises(InputError):
                relative_key(root, Path(tmp) / "elsewhere.txt")

    def test_missing_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(InputError):
                list(iter_documents(Path(tmp) / "missing"))
