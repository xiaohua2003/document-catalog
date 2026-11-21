import tempfile
import unittest
from pathlib import Path
from doccatalog.reader import load_document, title_from_body
from doccatalog.errors import InputError


class ReaderTest(unittest.TestCase):
    def test_markdown_title(self):
        self.assertEqual(title_from_body(Path("a.md"), "\n# Project notes\nbody"), "Project notes")

    def test_text_title(self):
        self.assertEqual(title_from_body(Path("my-report.txt"), "body"), "my report")

    def test_utf8_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "notes.txt"
            file.write_bytes(bytes([0xEF,0xBB,0xBF]) + b"Hello")
            doc = load_document("notes.txt", file)
            self.assertEqual(doc.body, "Hello")
            self.assertEqual(doc.byte_size, 8)

    def test_invalid_utf8_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "bad.txt"
            file.write_bytes(bytes([0xFF]))
            with self.assertRaises(InputError):
                load_document("bad.txt", file)
