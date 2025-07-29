"""Precompiled regex patterns for tier-1 replacement."""

from __future__ import annotations

import re

PATTERNS = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "URL": re.compile(r"https?://[\w.-]+(?:/[\w./?%&=-]*)?"),
    "IP": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "PHONE": re.compile(
        r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
    ),
    # MDR certificate numbers (format: MDR + 6 digits)
    "MDR_CERT": re.compile(r"\bMDR\d{6}\b", re.IGNORECASE),
    # IVDR certificate numbers (format: IVDR + 6 digits)
    "IVDR_CERT": re.compile(r"\bIVDR\d{6}\b", re.IGNORECASE),
    # Removed overly broad COMPANY_SUFFIX pattern - company detection is now
    # handled in enhanced NER tier
}
