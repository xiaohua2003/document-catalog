import tempfile
import unittest
from pathlib import Path
from doccatalog.ingest import ingest_folder
from doccatalog.storage import Catalog


class IngestTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "docs"
        self.root.mkdir()
        self.store = Catalog(Path(self.temp.name) / "db.sqlite")
        self.store.initialize()

    def tearDown(self):
        self.temp.cleanup()

    def test_first_ingest_adds_documents(self):
        (self.root / "a.md").write_text("# Finance\nAnnual revenue")
        summary = ingest_folder(self.store, self.root)
        self.assertEqual((summary.scanned, summary.added, summary.skipped), (1, 1, 0))
        self.assertEqual(self.store.search("revenue")[0]["title"], "Finance")

    def test_second_ingest_skips_existing(self):
        file = self.root / "a.txt"
        file.write_text("original")
        ingest_folder(self.store, self.root)
        file.write_text("modified")
        summary = ingest_folder(self.store, self.root)
        self.assertEqual(summary.skipped, 1)
        self.assertEqual(self.store.get_document("a.txt")["body"], "original")

    def test_removing_source_does_not_prune(self):
        file = self.root / "a.txt"
        file.write_text("original")
        ingest_folder(self.store, self.root)
        file.unlink()
        ingest_folder(self.store, self.root)
        self.assertEqual(self.store.count(), 1)
