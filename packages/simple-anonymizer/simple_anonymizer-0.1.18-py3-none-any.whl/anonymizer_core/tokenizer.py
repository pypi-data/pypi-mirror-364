"""Unicode-aware tokenizer."""

from __future__ import annotations

import regex as re
from typing import List, cast

TOKEN_RE = re.compile(r"\p{L}[\p{L}\p{N}]*|\p{N}+|\S")


def tokenize(text: str) -> List[str]:
    """Return list of word and punctuation tokens."""
    return cast(List[str], TOKEN_RE.findall(text))
