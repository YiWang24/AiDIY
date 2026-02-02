from __future__ import annotations

import hashlib
import re


_slug_re = re.compile(r"[^a-z0-9\s-]")
_space_re = re.compile(r"\s+")


def slugify(text: str) -> str:
    normalized = text.strip().lower()
    normalized = _slug_re.sub("", normalized)
    normalized = _space_re.sub("-", normalized)
    normalized = normalized.strip("-")
    return normalized or "section"


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()
