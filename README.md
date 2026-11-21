# Document Catalog

A local, dependency-free searchable catalog of plain text and Markdown documents.
It indexes a directory into an SQLite database, then supports simple token-based
search and document inspection from the command line.

## Commands

```sh
python -m doccatalog init --db catalog.sqlite
python -m doccatalog ingest documents --db catalog.sqlite
python -m doccatalog search pricing --db catalog.sqlite
python -m doccatalog list --db catalog.sqlite
python -m unittest discover -s tests -v
```

The `ingest` command is an initial import: it skips documents whose paths already
exist in the catalog. In particular, it currently **does not update existing rows**
when files change and **does not remove stale rows** when files disappear. This is a
known limitation, not the intended end-state for a continuously managed collection.

The project uses only Python's standard library and SQLite, with no network
services. It is intended for a laptop or a local batch job, not for web crawling.

## Supported inputs

- `.txt` and `.md`, UTF-8 (including a leading UTF-8 BOM)
- A user-provided directory, traversed recursively
- Paths normalized to POSIX separators for stable catalog identity
- Empty documents retained as metadata even when they have no searchable terms

## Search behavior

Documents are tokenized into lowercased alphanumeric terms. Search uses exact
term matches with a simple frequency score and returns the highest-scoring
matches first. Search is purposely not a semantic retriever.

## Design notes

The store has a `documents` table and a `terms` table containing term frequency
for each document. The schema includes a content digest to enable future change
detection, but the current import path is append-only. Each document is inserted
in one transaction so an individual failure does not leave half-written term rows.

The CLI uses JSON for machine-readable results so downstream scripts need not
parse tables. Human-readable errors go to stderr and exit nonzero.

## Contributing

Run unit tests with `python -m unittest discover -s tests -v` and verify the CLI
help with `python -m doccatalog --help`. Please add tests with temporary folders
and SQLite files, rather than requiring a real document collection.
