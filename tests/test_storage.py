import tempfile
import unittest
from pathlib import Path
from doccatalog.storage import Catalog
from doccatalog.reader import DocumentSource


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Catalog(Path(self.temp.name) / "cat.sqlite")
        self.store.initialize()

    def tearDown(self):
        self.temp.cleanup()

    def source(self, key, body="risk risk pricing"):
        return DocumentSource(key, key, body, "0" * 64, len(body))

    def test_insert_is_idempotent(self):
        self.assertTrue(self.store.add_if_missing(self.source("a.md")))
        self.assertFalse(self.store.add_if_missing(self.source("a.md", "changed")))
        self.assertEqual(self.store.count(), 1)
        self.assertEqual(self.store.get_document("a.md")["body"], "risk risk pricing")

    def test_search_ranked_by_frequency(self):
        self.store.add_if_missing(self.source("a.md"))
        self.store.add_if_missing(self.source("b.md", "risk"))
        self.assertEqual([r["path"] for r in self.store.search("risk")], ["a.md", "b.md"])

    def test_search_no_results(self):
        self.assertEqual(self.store.search("doesnotexist"), [])
        self.assertEqual(self.store.search(""), [])

    def test_listing_sorted(self):
        self.store.add_if_missing(self.source("z.txt"))
        self.store.add_if_missing(self.source("a.txt"))
        self.assertEqual([x["path"] for x in self.store.list_documents()], ["a.txt", "z.txt"])
