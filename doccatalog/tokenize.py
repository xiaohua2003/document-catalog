"""Extracts and counts keywords from document text.
Converts words to lowercase and splits them using punctuation,
underscores, and spaces.
"""
from collections import Counter

def tokens(content: str) -> list[str]:
    if not isinstance(content, str):
        raise TypeError("content must be a string")
    result = []
    current = []
    for char in content:
        if char.isalnum():
            current.append(char.lower())
        elif current:
            result.append("".join(current))
            current.clear()
    if current:
        result.append("".join(current))
    return result


def frequencies(content: str) -> dict[str, int]:
    """Count occurrences of each exact normalized term in the content."""
    return dict(Counter(tokens(content)))


def normalize_query(query: str) -> list[str]:
    seen = set()
    unique = []
    for term in tokens(query):
        if term not in seen:
            unique.append(term)
            seen.add(term)
    return unique
