"""Typed error categories for the command-line boundary."""
class CatalogError(Exception):
    """A recoverable application error suitable for a CLI error message."""


class InputError(CatalogError):
    """Input file or directory cannot be safely processed."""


class StorageError(CatalogError):
    """Local catalog storage is inaccessible or corrupt."""


class InvalidQuery(CatalogError):
    """Search input is not a supported query."""
