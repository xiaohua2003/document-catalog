"""Document import orchestration.

Scans supported files and imports new documents into the catalog.
Existing documents are skipped to prevent duplicate entries.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
from .paths import iter_documents
from .reader import load_document
from .storage import Catalog
from .errors import InputError


@dataclass
class ImportSummary:
    scanned: int = 0
    added: int = 0
    skipped: int = 0

    def as_dict(self):
        return asdict(self)


def ingest_folder(catalog: Catalog, root: Path) -> ImportSummary:
    result = ImportSummary()
    for key, file in iter_documents(root):
        result.scanned += 1
        if catalog.contains(key):
            result.skipped += 1
            continue
        document = load_document(key, file)
        if catalog.add_if_missing(document):
            result.added += 1
        else:
            result.skipped += 1
    return result
