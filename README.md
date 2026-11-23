# Document Catalog

A simple Python tool for indexing and searching local text and Markdown files. It stores documents in SQLite and provides command-line commands for importing, searching, and viewing documents.

## Commands

```sh
python -m doccatalog init --db catalog.sqlite
python -m doccatalog ingest documents --db catalog.sqlite
python -m doccatalog search pricing --db catalog.sqlite
python -m doccatalog list --db catalog.sqlite
python -m doccatalog show pricing.md --db catalog.sqlite
```

Run the tests with:

```sh
python -m unittest discover -s tests -v
```

## Supported Files

- `.txt` and `.md` files encoded in UTF-8, including files with a UTF-8 BOM
- Files in the selected directory and its subdirectories
- Empty documents, which are stored even if they contain no searchable words

Document paths are stored relative to the input directory using forward slashes.

## Importing Documents

The `ingest` command imports new documents into the database. If a document with the same path is already indexed, it is skipped.

Currently, the command does not update existing documents when their contents change or remove database records when files are deleted.

## Searching Documents

Search matches individual words without case sensitivity. Documents are ranked by how frequently the matching words appear.

Search results are returned as JSON and include the document path, title, and relevance score.

## Database

The SQLite database contains two main tables:

- `documents`: Stores document paths, titles, content, file sizes, and SHA-256 hashes.
- `terms`: Stores searchable words and their frequencies for each document.

Each new document and its search terms are inserted within a database transaction.

## Development

The project uses Python's standard library and SQLite. No additional packages or external services are required.

To run the tests:

```sh
python -m unittest discover -s tests -v
```

To check the available commands:

```sh
python -m doccatalog --help
```
