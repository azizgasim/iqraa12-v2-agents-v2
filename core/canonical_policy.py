"""IQRAA V2 — Canonical Text Policy.

Defines how Arabic text is normalized before offset calculation.
All offsets in the system refer to the CANONICAL form, not raw.
This is non-negotiable for academic reproducibility.

References:
- OpenITI mARkdown conventions
- CAMeL Tools normalization
- Unicode NFC standard
"""

from __future__ import annotations

import re
import hashlib
import unicodedata
from dataclasses import dataclass, field
from typing import Optional


POLICY_VERSION = "1.0.0"


@dataclass(frozen=True)
class CanonicalPolicy:
    """Immutable canonicalization policy."""
    version: str = POLICY_VERSION
    unicode_form: str = "NFC"
    strip_diacritics: bool = True
    normalize_hamza: bool = True       # أ إ آ → ا
    normalize_alef_maqsura: bool = False  # ى ≠ ي (critical in classical)
    remove_tatweel: bool = True        # ـ kashida removal
    strip_honorifics: bool = False     # صلى الله عليه وسلم etc
    encoding: str = "utf-8"


# Arabic diacritics Unicode range
_DIACRITICS = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]')

# Hamza forms → bare alef
_HAMZA_MAP = str.maketrans({
    '\u0623': '\u0627',  # أ → ا
    '\u0625': '\u0627',  # إ → ا
    '\u0622': '\u0627',  # آ → ا
})

# Tatweel
_TATWEEL = re.compile(r'\u0640')


def canonicalize(text: str, policy: Optional[CanonicalPolicy] = None) -> str:
    """Apply canonical normalization to Arabic text."""
    if policy is None:
        policy = CanonicalPolicy()

    # Step 1: Unicode normalization
    result = unicodedata.normalize(policy.unicode_form, text)

    # Step 2: Strip diacritics (before offset calc)
    if policy.strip_diacritics:
        result = _DIACRITICS.sub('', result)

    # Step 3: Hamza normalization
    if policy.normalize_hamza:
        result = result.translate(_HAMZA_MAP)

    # Step 4: Remove tatweel
    if policy.remove_tatweel:
        result = _TATWEEL.sub('', result)

    return result


def text_hash(text: str) -> str:
    """SHA-256 hash of canonical text for integrity verification."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def make_canonical_span(
    raw_text: str,
    source_id: str,
    raw_start: int,
    raw_end: int,
    policy: Optional[CanonicalPolicy] = None,
) -> dict:
    """Create a canonical text span with both raw and canonical forms."""
    if policy is None:
        policy = CanonicalPolicy()

    raw_slice = raw_text[raw_start:raw_end]
    canonical_full = canonicalize(raw_text, policy)
    canonical_slice = canonicalize(raw_slice, policy)

    # Find canonical offsets
    can_start = canonical_full.find(canonical_slice)
    can_end = can_start + len(canonical_slice) if can_start >= 0 else -1

    return {
        "text_raw": raw_slice,
        "text_canonical": canonical_slice,
        "source_id": source_id,
        "raw_start": raw_start,
        "raw_end": raw_end,
        "canonical_start": can_start,
        "canonical_end": can_end,
        "canonicalizer_version": policy.version,
        "source_hash": text_hash(canonical_full),
    }
