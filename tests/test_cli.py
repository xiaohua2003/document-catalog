import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from doccatalog.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "cat.sqlite"

    def tearDown(self):
        self.temp.cleanup()

    def call(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main([*args, "--db", str(self.db)])
        return status, json.loads(output.getvalue())

    def test_init_and_list(self):
        self.assertEqual(self.call("init")[0], 0)
        self.assertEqual(self.call("list"), (0, []))

    def test_ingest_search_show(self):
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "hello.txt").write_text("a pricing example")
        self.assertEqual(self.call("ingest", str(docs))[1]["added"], 1)
        self.assertEqual(self.call("search", "pricing")[1][0]["path"], "hello.txt")
        self.assertIn("pricing", self.call("show", "hello.txt")[1]["body"])
