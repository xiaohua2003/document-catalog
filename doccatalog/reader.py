"""Document decoding and metadata extraction.
There are no remote readers or file-type plugins.
"""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from .errors import InputError


@dataclass(frozen=True)
class DocumentSource:
    key: str
    title: str
    body: str
    sha256: str
    byte_size: int


def title_from_body(path: Path, body: str) -> str:
    """Use the first Markdown heading, or fall back to the file stem."""
    if path.suffix.lower() == ".md":
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                if title:
                    return title[:240]
    return path.stem.replace("_", " ").replace("-", " ")[:240]


def load_document(key: str, path: Path) -> DocumentSource:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise InputError(f"cannot read {key}: {exc}") from exc
    try:
        body = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(f"expected UTF-8 text in {key}") from exc
    return DocumentSource(
        key=key,
        title=title_from_body(path, body),
        body=body,
        sha256=sha256(raw).hexdigest(),
        byte_size=len(raw),
    )
