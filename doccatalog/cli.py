"""Command-line interface for the document catalog.
Handles command-line arguments, reports errors to stderr,
and outputs results in JSON format.
"""
import argparse
import json
import sys
from pathlib import Path
from .errors import CatalogError
from .ingest import ingest_folder
from .storage import Catalog


def parser():
    p = argparse.ArgumentParser(prog="doccatalog", description="Offline document catalog")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="initialize local SQLite catalog")
    init.add_argument("--db", default="catalog.sqlite")
    ingest = sub.add_parser("ingest", help="import new documents from a directory")
    ingest.add_argument("root", type=Path)
    ingest.add_argument("--db", default="catalog.sqlite")
    search = sub.add_parser("search", help="search indexed terms")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--db", default="catalog.sqlite")
    listing = sub.add_parser("list", help="list all indexed documents")
    listing.add_argument("--db", default="catalog.sqlite")
    show = sub.add_parser("show", help="show indexed content for a relative path")
    show.add_argument("path")
    show.add_argument("--db", default="catalog.sqlite")
    return p


def emit(value):
    print(json.dumps(value, sort_keys=True, ensure_ascii=False))


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        store = Catalog(args.db)
        if args.command == "init":
            store.initialize()
            emit({"status": "initialized", "database": str(store.database)})
        elif args.command == "ingest":
            store.initialize()
            emit(ingest_folder(store, args.root).as_dict())
        elif args.command == "search":
            emit(store.search(args.query, args.limit))
        elif args.command == "list":
            emit(store.list_documents())
        elif args.command == "show":
            doc = store.get_document(args.path)
            if doc is None:
                print(f"not found: {args.path}", file=sys.stderr)
                return 1
            emit(doc)
        return 0
    except (CatalogError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
