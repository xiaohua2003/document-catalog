import unittest
from doccatalog.tokenize import tokens, frequencies, normalize_query


class TokenizeTest(unittest.TestCase):
    def test_punctuation_breaks_words(self):
        self.assertEqual(tokens("Hello, WORLD!"), ["hello", "world"])

    def test_mixed_case_counted_together(self):
        self.assertEqual(frequencies("Risk risk RISK"), {"risk": 3})

    def test_query_is_unique(self):
        self.assertEqual(normalize_query("Risk risk pricing"), ["risk", "pricing"])

    def test_empty_documents(self):
        self.assertEqual(frequencies(" \n---"), {})

    def test_unicode_alphanumerics(self):
        self.assertEqual(tokens("Café 東京_2026"), ["café", "東京", "2026"])
