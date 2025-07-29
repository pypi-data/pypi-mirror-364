"""Core anonymization API."""

from __future__ import annotations

import os
import warnings

# Configure tldextract for corporate networks
os.environ['TLDEXTRACT_CACHE'] = os.path.expanduser('~/.tldextract_cache')
# Disable automatic suffix list updates to avoid SSL issues
os.environ['TLDEXTRACT_FALLBACK_TO_SNAPSHOT'] = 'true'
# Suppress SSL warnings from tldextract
warnings.filterwarnings('ignore', module='tldextract')
warnings.filterwarnings('ignore', message='.*tldextract.*')

from dataclasses import dataclass, field
from typing import Dict, List
import re

from .dictionary import _lemmatize_word
from .presidio_engine import get_presidio_engine, is_presidio_available
from .patterns import PATTERNS
from .ner import SpacyNER
from .protected_titles import PROTECTED_TITLES
from .text_anonymizer_integration import get_text_anonymizer_integration, is_text_anonymizer_available

__all__ = ["redact", "RedactionResult"]


@dataclass
class RedactionResult:
    """Result returned by :func:`redact`."""

    text: str
    mapping: Dict[str, str] = field(default_factory=dict)

    @property
    def stats(self) -> Dict[str, int]:
        return {
            k: len(v) if isinstance(v, list) else 1 for k, v in self.mapping.items()
        }


def merge_consecutive_redactions(
    text: str, mapping: Dict[str, str]
) -> tuple[str, Dict[str, str]]:
    """Merge consecutive redacted words of the same type into a single redaction."""
    # More comprehensive pattern to catch various consecutive redaction scenarios
    # This will match: NAME_1 NAME_2, NAME_1. NAME_2, NAME_1's NAME_2, etc.
    pattern = r"(\b([A-Z_]+)_\d+)(\s*[.,;]?\s*(?:\'s\s+)?\2_\d+)+"

    # Start with the original mapping - we'll only modify it as needed
    new_mapping = mapping.copy()
    merged_text = text

    # Find all consecutive patterns
    for match in re.finditer(pattern, text):
        original_sequence = match.group(0)
        base_category = match.group(2)

        # Find all placeholders in this sequence
        placeholder_pattern = rf"\b{base_category}_\d+"
        placeholders = re.findall(placeholder_pattern, original_sequence)

        # Only merge if there are actually consecutive placeholders
        if len(placeholders) > 1:
            # Use the first placeholder as the replacement
            replacement = placeholders[0]

            # Replace the entire sequence with just the first placeholder
            merged_text = merged_text.replace(original_sequence, replacement)

            # Note: We keep all original mappings intact - this preserves the count
            # The visual merging in the text is the important part for user experience

    # Additional cleanup for simpler consecutive patterns
    simple_consecutive_pattern = r"(\b([A-Z_]+)_\d+)(\s*[.,;]?\s*\2_\d+)+"

    def simple_replace(match: re.Match[str]) -> str:
        original_sequence = match.group(0)

        # Keep the first placeholder and any immediate punctuation
        first_part = match.group(1)

        # Check if there's punctuation after the first placeholder
        remaining = original_sequence[len(first_part) :]
        punctuation_match = re.match(r"^(\s*[.,;])", remaining)

        if punctuation_match:
            return first_part + punctuation_match.group(1)
        else:
            return first_part

    merged_text = re.sub(simple_consecutive_pattern, simple_replace, merged_text)

    return merged_text, new_mapping


def is_protected_title(word: str) -> bool:
    """Check if a word is a protected title that should not be anonymized."""
    # Remove common punctuation and convert to lowercase
    clean_word = word.lower().rstrip('.,;:')
    return clean_word in PROTECTED_TITLES


def is_in_lexicon(word: str, lexicon: set) -> bool:
    """Check if a word is in the lexicon.

    Considers both original and lemmatized forms.
    """
    word_lower = word.lower()

    # Check original form first
    if word_lower in lexicon:
        return True

    # Check lemmatized form
    try:
        lemma = _lemmatize_word(word_lower)
        return lemma in lexicon
    except Exception:
        # Fallback to original check if lemmatization fails
        return word_lower in lexicon


def _is_common_role_or_title(word: str) -> bool:
    """Check if a word is a common role, title, or professional designation."""
    common_roles_titles = {
        # Professional roles
        "reviewer",
        "manager",
        "director",
        "coordinator",
        "specialist",
        "analyst",
        "consultant",
        "engineer",
        "developer",
        "designer",
        "administrator",
        "supervisor",
        "executive",
        "officer",
        "assistant",
        "representative",
        "agent",
        "advisor",
        "auditor",
        "inspector",
        # Academic/Medical
        "professor",
        "doctor",
        "researcher",
        "scientist",
        "physician",
        "nurse",
        "therapist",
        "technician",
        "student",
        "instructor",
        # Business titles
        "president",
        "vice",
        "chairman",
        "ceo",
        "cfo",
        "cto",
        "founder",
        "partner",
        "associate",
        "principal",
        "senior",
        "junior",
        "lead",
        # General terms
        "team",
        "department",
        "division",
        "unit",
        "group",
        "committee",
        "board",
        "panel",
        "staff",
        "member",
        "colleague",
        "client",
        "customer",
        "vendor",
        "supplier",
        "contractor",
        "participant",
        # Document/Process terms
        "document",
        "report",
        "form",
        "application",
        "submission",
        "review",
        "evaluation",
        "assessment",
        "analysis",
        "study",
        "research",
        "investigation",
        "audit",
        "inspection",
        "examination",
        # Common words that might be capitalized
        "regarding",
        "concerning",
        "following",
        "attached",
        "enclosed",
        "provided",
        "included",
        "submitted",
        "uploaded",
        "downloaded",
        "updated",
        "revised",
        "modified",
        "changed",
        "completed",
        "finished",
        "started",
        "initiated",
        "approved",
        "rejected",
        "accepted",
        "declined",
        "pending",
        "processing",
        "reviewed",
        # Greeting words that should never be redacted
        "dear",
        "mr",
        "ms",
        "mrs",
        "dr",
        "hello",
        "hi",
        "greetings",
    }

    return word.lower() in common_roles_titles


def _looks_like_proper_name(word: str) -> bool:
    """Determine if a word looks like a proper name that should be redacted."""
    # This is a conservative heuristic - only redact words that are very
    # likely to be names

    # Don't redact words that end with common suffixes that indicate they're
    # regular words
    common_word_endings = {
        "ing",
        "ed",
        "er",
        "est",
        "ly",
        "tion",
        "sion",
        "ness",
        "ment",
        "able",
        "ible",
        "ful",
        "less",
        "ous",
        "ive",
        "al",
        "ic",
        "ant",
        "ent",
    }

    for ending in common_word_endings:
        if word.lower().endswith(ending):
            return False

    # Don't redact words that are clearly technical terms or common business words
    if any(char.isdigit() for char in word):
        return False

    # Don't redact words that contain common word patterns
    common_patterns = ["tech", "system", "manage", "process", "service", "product"]
    word_lower = word.lower()
    for pattern in common_patterns:
        if pattern in word_lower:
            return False

    # If it passes all these filters, it might be a proper name
    # But still be conservative - only redact if it's not at sentence start
    return True


def redact(
    text: str,
    *,
    lang: str = "en",
    lexicon_paths: List[str] | None = None,
    placeholder_fmt: str = "<REDACTED>",
    use_presidio: bool = True,  # Prefer Presidio if available
    use_fallback_ner: bool = True,  # Use fallback NER when Presidio is disabled
    use_text_anonymizer: bool = True,  # Always use text-anonymizer as additional layer
    merge_multi_word: bool = True,
    # Backward compatibility parameters
    use_ner: bool | None = None,  # Legacy parameter for backward compatibility
    use_conservative_dict: bool | None = None,  # Legacy parameter for backward compatibility
) -> RedactionResult:
    """Redact personal data from ``text``.

    Uses Microsoft Presidio as the primary PII detection engine for production-grade
    anonymization. Falls back to custom pattern matching and NER only if Presidio
    is unavailable.

    Args:
        text: The input text to redact
        lang: Language code for NLP model (default: "en")
        lexicon_paths: Optional list of lexicon file paths
        placeholder_fmt: Format string for placeholders, with {cat} and {idx}
        use_presidio: Whether to use Microsoft Presidio for PII detection (recommended)
        use_fallback_ner: Whether to use fallback NER/patterns if Presidio unavailable
        merge_multi_word: Whether to merge multi-word entities
        use_ner: (DEPRECATED) Use use_fallback_ner instead
        use_conservative_dict: (DEPRECATED) No longer used with Presidio

    Returns:
        RedactionResult containing redacted text and substitution mapping
    """
    import logging
    logging.info(f"Redact called with use_presidio={use_presidio}, use_fallback_ner={use_fallback_ner}, use_text_anonymizer={use_text_anonymizer}")

    # Handle backward compatibility
    if use_ner is not None:
        use_fallback_ner = use_ner
    # use_conservative_dict is ignored - Presidio doesn't need it

    result_text = text
    mapping: Dict[str, str] = {}
    counters: Dict[str, int] = {}
    redacted_positions = set()



    def placeholder(category: str) -> str:
        counters[category] = counters.get(category, 0) + 1
        if placeholder_fmt == "<REDACTED>":
            return "<REDACTED>"
        else:
            return placeholder_fmt.format(cat=category, idx=counters[category])

    # PRIMARY TIER - Microsoft Presidio PII detection (recommended approach)
    if use_presidio and is_presidio_available():
        try:
            logging.info("Attempting to use Presidio for PII detection.")
            presidio_engine = get_presidio_engine()

            if presidio_engine is not None:
                # Analyze the text for PII using Presidio
                analyzer_results = presidio_engine.analyzer.analyze(
                    text=result_text,
                    language=lang,
                    entities=None  # Use all available entity types
                )

                # Sort by start position, but prioritize EMAIL_ADDRESS over URL for overlapping ranges
                def sort_key(result):
                    # Prioritize EMAIL_ADDRESS over URL for same position
                    priority = 0 if result.entity_type == 'EMAIL_ADDRESS' else 1 if result.entity_type == 'URL' else 0.5
                    return (result.start, priority)

                # Sort by start position (reverse order) to maintain text indices during replacement
                # But prioritize EMAIL over URL when they overlap
                sorted_results = sorted(analyzer_results, key=lambda x: x.start, reverse=True)

                # Filter out overlapping URL entities when EMAIL_ADDRESS exists in the same range
                # Also filter out protected titles
                filtered_results = []
                for result in sorted_results:
                    entity_text = result_text[result.start:result.end]

                    # Skip protected titles
                    if is_protected_title(entity_text):
                        continue

                    # Check if this is a URL that overlaps with an EMAIL_ADDRESS
                    if result.entity_type == 'URL':
                        # Check if there's an EMAIL_ADDRESS that contains this URL
                        email_overlap = any(
                            other.entity_type == 'EMAIL_ADDRESS' and
                            other.start <= result.start < other.end and
                            other.start < result.end <= other.end
                            for other in analyzer_results
                        )
                        if email_overlap:
                            continue  # Skip this URL as it's part of an email

                    filtered_results.append(result)

                for result in filtered_results:
                    start, end = result.start, result.end
                    entity_text = result_text[start:end]
                    entity_type = result.entity_type

                    # Skip if already redacted
                    if any(pos in range(start, end) for pos in redacted_positions):
                        continue

                    # Skip if already in mapping
                    if entity_text in mapping:
                        continue

                    # Map Presidio entity types to our categories
                    # Note: EMAIL_ADDRESS should be prioritized over URL for email patterns
                    entity_mapping = {
                        'EMAIL_ADDRESS': 'EMAIL',  # Prioritize email detection
                        'PERSON': 'PERSON',
                        'PHONE_NUMBER': 'PHONE',
                        'CREDIT_CARD': 'CREDIT_CARD',
                        'IBAN_CODE': 'BANK',
                        'US_SSN': 'SSN',
                        'US_PASSPORT': 'PASSPORT',
                        'US_DRIVER_LICENSE': 'DRIVER_LICENSE',
                        'DATE_TIME': 'DATE',
                        'IP_ADDRESS': 'IP',
                        'URL': 'URL',
                        'LOCATION': 'LOCATION',
                        'NRP': 'NATIONALITY',
                        'ORGANIZATION': 'COMPANY',
                        # Custom recognizers
                        'EU_MDR_CERTIFICATE': 'EU_MDR_CERTIFICATE',
                        'EU_IVDR_CERTIFICATE': 'EU_IVDR_CERTIFICATE',
                    }

                    # Special handling for email vs URL detection
                    if entity_type == 'URL' and '@' in entity_text and '.' in entity_text:
                        # If it looks like an email but was detected as URL, treat as email
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        if re.match(email_pattern, entity_text):
                            placeholder_category = 'EMAIL'
                        else:
                            placeholder_category = entity_mapping.get(entity_type, entity_type)
                    else:
                        placeholder_category = entity_mapping.get(entity_type, entity_type)

                    if placeholder_category is None:
                        placeholder_category = "UNKNOWN_PII"
                    ph = placeholder(placeholder_category)

                    # Replace the entity in the text
                    result_text = result_text[:start] + ph + result_text[end:]
                    redacted_positions.update(range(start, start + len(ph)))
                    mapping[entity_text] = ph

                # If Presidio worked, we're mostly done!

                # Additional pattern matching for entities Presidio might miss
                # Keep this very conservative to avoid false positives
                additional_patterns = {
                    "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
                    "ZIP_CODE": r'\b\d{5}(?:-\d{4})?\b',
                    # Modified street address pattern to avoid matching titles
                    "STREET_ADDRESS": r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Drive|Road|Rd|Boulevard|Blvd|Lane|Ln|Place|Pl|Court|Ct|Way|Terrace|Ter)\b',
                    "MEDICARE_ID": r'\b[A-Z0-9]{4}-[A-Z0-9]{3}-[A-Z0-9]{4}\b',
                    "PATIENT_ID": r'\b[A-Z]{3}\d{4}\b',
                    "MEDICAL_CENTER": r'\b[A-Za-z\s]+Medical\s+Center\b',
                    "HOSPITAL": r'\b[A-Za-z\s]+Hospital\b',
                    # Phone number detection (in case Presidio misses it)
                    "PHONE": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
                    # Removed PERSON_NAME pattern - too prone to false positives
                }

                for pattern_name, pattern in additional_patterns.items():
                    matches = list(re.finditer(pattern, result_text, re.IGNORECASE))
                    for match in reversed(matches):
                        original_text = match.group(0)
                        start, end = match.span()

                        # Skip if it's a protected title
                        if is_protected_title(original_text):
                            continue

                        if original_text not in mapping and not any(
                            pos in range(start, end) for pos in redacted_positions
                        ):
                            ph = placeholder(pattern_name)
                            result_text = result_text[:start] + ph + result_text[end:]
                            redacted_positions.update(range(start, start + len(ph)))
                            mapping[original_text] = ph

                # Conservative additional pass to catch obvious person names that Presidio missed
                # Only look for very specific patterns that are likely to be names
                # Pattern 1: Title + Name (e.g., "Dr Smith", "Mr Johnson")
                title_name_pattern = r'\b(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Miss|Prof\.?|Professor)\s+([A-Z][a-z]+)\b'
                title_matches = list(re.finditer(title_name_pattern, result_text, re.IGNORECASE))
                for match in reversed(title_matches):
                    name_part = match.group(1)  # Extract just the name part
                    name_start = match.start(1)
                    name_end = match.end(1)

                    if not any(pos in range(name_start, name_end) for pos in redacted_positions):
                        if name_part not in mapping and not is_protected_title(name_part):
                            ph = placeholder("PERSON")
                            result_text = result_text[:name_start] + ph + result_text[name_end:]
                            redacted_positions.update(range(name_start, name_start + len(ph)))
                            mapping[name_part] = ph

                # Pattern 2: First Name Last Name (two consecutive capitalized words)
                # But be very conservative - only if they appear in contexts that suggest names
                full_name_pattern = r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
                full_name_matches = list(re.finditer(full_name_pattern, result_text))
                for match in reversed(full_name_matches):
                    full_name = match.group(0)
                    first_name = match.group(1)
                    last_name = match.group(2)
                    start, end = match.span()

                    # Skip if already redacted
                    if any(pos in range(start, end) for pos in redacted_positions):
                        continue

                    # Skip if either part is a protected title
                    if is_protected_title(first_name) or is_protected_title(last_name):
                        continue

                    # Only consider as names if both parts are not common words
                    # Use a small set of the most obvious non-name words
                    obvious_non_names = {
                        'Data', 'Quality', 'Image', 'System', 'Network', 'Model', 'Algorithm',
                        'Process', 'Method', 'Test', 'Analysis', 'Assessment', 'Training',
                        'Vessel', 'Sample', 'Size', 'Volume', 'Contrast', 'Risk', 'Time',
                        'Problem', 'Result', 'Study', 'Research', 'Report', 'Document',
                        'File', 'Format', 'Type', 'Category', 'Group', 'Set', 'List',
                        'Table', 'Database', 'Information', 'Content', 'Text', 'Message',
                        'Note', 'Comment', 'Response', 'Output', 'Input', 'Feedback',
                        'Review', 'Evaluation', 'Examination', 'Investigation', 'Survey',
                        'Discussion', 'Meeting', 'Conference', 'Session', 'Workshop',
                        'Course', 'Class', 'Lesson', 'Tutorial', 'Guide', 'Manual',
                        'Instructions', 'Directions', 'Steps', 'Procedures', 'Rules',
                        'Standards', 'Requirements', 'Conditions', 'Terms', 'Policies'
                    }

                    if (first_name not in obvious_non_names and
                        last_name not in obvious_non_names and
                        full_name not in mapping):

                        # Additional heuristic: check if it's in a context that suggests a name
                        # Look for patterns like "by John Smith", "from Mary Jones", etc.
                        context_start = max(0, start - 20)
                        context_end = min(len(result_text), end + 20)
                        context = result_text[context_start:context_end].lower()

                        name_contexts = ['by ', 'from ', 'to ', 'dear ', 'sincerely ',
                                       'regards ', 'contact ', 'author ', 'written by ',
                                       'signed by ', 'prepared by ', 'reviewed by ']

                        has_name_context = any(ctx in context for ctx in name_contexts)

                        # Only redact if it has name context or both words are uncommon
                        if has_name_context or (len(first_name) >= 4 and len(last_name) >= 4):
                            ph = placeholder("PERSON")
                            result_text = result_text[:start] + ph + result_text[end:]
                            redacted_positions.update(range(start, start + len(ph)))
                            mapping[full_name] = ph

                # Merge consecutive redactions but don't return early - let always_redact processing continue
                if merge_multi_word:
                    result_text, mapping = merge_consecutive_redactions(result_text, mapping)
                logging.info("Presidio PII detection succeeded.")
                # Don't return here - continue to always_redact processing

        except Exception as e:
            logging.warning(f"Presidio anonymization failed: {e}. Falling back to custom methods.")
    else:
        logging.info("Presidio not available or not requested. Using fallback methods.")

    # ADDITIONAL LAYER - text-anonymizer for enhanced processing
    if use_text_anonymizer and is_text_anonymizer_available():
        try:
            logging.info("Applying text-anonymizer as additional processing layer.")
            ta_integration = get_text_anonymizer_integration()
            if ta_integration:
                # Process the already-anonymized text through text-anonymizer
                ta_result_text, ta_mapping = ta_integration.anonymize_text(result_text)

                # Merge any new entities found by text-anonymizer
                for original, placeholder_text in ta_mapping.items():
                    if original not in mapping:  # Only add if not already processed by Presidio
                        mapping[original] = placeholder_text
                        # Replace in the result text
                        result_text = result_text.replace(original, placeholder_text)

                logging.info("text-anonymizer additional processing completed.")
        except Exception as e:
            logging.warning(f"text-anonymizer additional processing failed: {e}")

    # ALWAYS REDACT TIER - Always process user-specified sensitive terms regardless of engine
    try:
        from .dictionary import load_always_redact_words
        always_redact = load_always_redact_words(lang)
        if always_redact:
            # Find all always_redact words in the ORIGINAL text first, then process them
            all_matches = []
            for word in always_redact:
                if not word.strip():
                    continue
                word_stripped = word.strip()

                # Note: We do NOT skip protected titles for always_redact
                # If a user explicitly adds a word to always_redact, it should be redacted
                # regardless of whether it's also a protected title

                escaped_word = re.escape(word_stripped)
                pattern = r"\b" + escaped_word + r"\b"
                # Search in the ORIGINAL text to get correct positions
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                for match in matches:
                    all_matches.append((match.start(), match.end(), match.group(0), word_stripped))

            # Sort matches by start position in reverse order for safe replacement
            all_matches.sort(key=lambda x: x[0], reverse=True)

            # Process all matches
            for start, end, original_text, word_stripped in all_matches:
                overlap_check = any(pos in range(start, end) for pos in redacted_positions)
                if not overlap_check:
                    ph = placeholder("ALWAYS_REDACT")
                    result_text = result_text[:start] + ph + result_text[end:]
                    redacted_positions.update(range(start, start + len(ph)))
                    mapping[original_text] = ph
    except Exception:
        pass

    # FALLBACK TIERS - Only used if Presidio is unavailable or disabled
    if not use_fallback_ner:
        logging.info("Fallback NER is disabled. Returning minimal processing.")
        # If user disabled fallback and Presidio failed/unavailable, return minimal processing
        if merge_multi_word:
            result_text, mapping = merge_consecutive_redactions(result_text, mapping)
        return RedactionResult(text=result_text, mapping=mapping)

    # Legacy fallback processing (simplified)

    def safe_replace(text: str, original: str, replacement: str, positions_to_avoid: set) -> tuple[str, set]:
        """Replace text while avoiding overlapping positions."""
        # Find all matches that don't overlap with existing redacted positions
        valid_matches = []
        for match in re.finditer(re.escape(original), text):
            start, end = match.span()
            if not any(pos in range(start, end) for pos in positions_to_avoid):
                valid_matches.append((start, end))

        if valid_matches:
            # Sort matches by start position in reverse order to replace from right to left
            # This ensures position indices remain valid during replacement
            valid_matches.sort(key=lambda x: x[0], reverse=True)

            # Perform replacements from right to left
            for start, end in valid_matches:
                text = text[:start] + replacement + text[end:]

            # Update positions_to_avoid with new positions after all replacements
            # We need to calculate the shift caused by all previous replacements
            length_diff = len(replacement) - len(original)
            new_positions = set()

            # Process matches from left to right to calculate cumulative shift
            valid_matches.sort(key=lambda x: x[0])  # Sort back to left-to-right order
            cumulative_shift = 0

            for start, end in valid_matches:
                # Calculate new position after all previous shifts
                new_start = start + cumulative_shift
                new_end = new_start + len(replacement)
                new_positions.update(range(new_start, new_end))
                cumulative_shift += length_diff

            positions_to_avoid.update(new_positions)

        return text, positions_to_avoid

    # Tier 1 - Critical patterns (EU certificates, etc.)
    for cat, pattern in PATTERNS.items():
        for m in pattern.finditer(result_text):
            original = m.group(0)
            start, end = m.span()

            # Skip protected titles
            if is_protected_title(original):
                continue

            if not any(pos in range(start, end) for pos in redacted_positions):
                ph = placeholder(cat)
                result_text, redacted_positions = safe_replace(result_text, original, ph, redacted_positions)
                mapping[original] = ph

    # Tier 2 - Always redact words (handled centrally above)

    # Tier 3 - Basic NER fallback
    try:
        ner = SpacyNER()
        entities = sorted(ner.extract(text), key=lambda x: len(x[0]), reverse=True)
        for ent_text, label in entities:
            if ent_text in mapping or is_protected_title(ent_text):
                continue
            entity_positions = []
            for match in re.finditer(re.escape(ent_text), result_text):
                start, end = match.span()
                if not any(pos in range(start, end) for pos in redacted_positions):
                    entity_positions.append((start, end))
            if entity_positions:
                ph = placeholder(label)
                result_text, redacted_positions = safe_replace(result_text, ent_text, ph, redacted_positions)
                mapping[ent_text] = ph
        logging.info("Fallback NER completed successfully.")
    except RuntimeError as e:
        logging.warning(f"spaCy NER not available: {e}")

        # Tier 4 - Final basic pattern fallback when neither Presidio nor spaCy is available
        # This provides minimal name detection for tests and basic functionality
        if not mapping:  # Only use this if no other methods found anything
            logging.info("Using basic pattern fallback for name detection")

            # Pattern 1: Single names after titles (search original text)
            title_name_fallback = r'\b(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Miss|Prof\.?|Professor)\s+([A-Z][a-z]{2,})\b'
            title_matches = []
            for match in re.finditer(title_name_fallback, text, re.IGNORECASE):
                name_part = match.group(1)
                name_start = match.start(1)
                name_end = match.end(1)

                if (not any(pos in range(name_start, name_end) for pos in redacted_positions) and
                    not is_protected_title(name_part) and
                    name_part not in mapping):
                    title_matches.append((name_start, name_end, name_part))

            # Sort by position and apply replacements
            for name_start, name_end, name_part in sorted(title_matches, reverse=True):
                ph = placeholder("PERSON")
                result_text = result_text[:name_start] + ph + result_text[name_end:]
                redacted_positions.update(range(name_start, name_start + len(ph)))
                mapping[name_part] = ph

            # Pattern 2: Simple two-word names (search original text, very conservative)
            simple_names = r'\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b'
            name_matches = []
            for match in re.finditer(simple_names, text):
                full_name = match.group(0)
                first_name = match.group(1)
                last_name = match.group(2)
                start, end = match.span()

                # Very restrictive conditions for fallback
                if (not any(pos in range(start, end) for pos in redacted_positions) and
                    not is_protected_title(first_name) and
                    not is_protected_title(last_name) and
                    full_name not in mapping and
                    len(first_name) >= 3 and len(last_name) >= 3 and
                    # Only names that are likely to be actual person names
                    first_name not in {'Data', 'System', 'Paris', 'France', 'United', 'States'}):
                    name_matches.append((start, end, full_name))

            # Sort by position and apply replacements
            for start, end, full_name in sorted(name_matches, reverse=True):
                ph = placeholder("PERSON")
                result_text = result_text[:start] + ph + result_text[end:]
                redacted_positions.update(range(start, start + len(ph)))
                mapping[full_name] = ph

    # Merge consecutive redactions of the same type (e.g., "NAME_1 NAME_2" -> "NAME_1")
    if merge_multi_word:
        result_text, mapping = merge_consecutive_redactions(result_text, mapping)

    return RedactionResult(text=result_text, mapping=mapping)


# Auto-setup spaCy models on first import (for pip installs)
def _ensure_spacy_models():
    """Ensure spaCy models are available, install if needed."""
    try:
        from .ner import SpacyNER
        # Try to create a SpacyNER instance - this will trigger model loading
        ner = SpacyNER()
        # If we get here, the model is available
        return True
    except RuntimeError as e:
        if "Failed to load spaCy model" in str(e):
            # Model not found, try to install it
            try:
                from .setup_models import install_spacy_model
                print("🔧 Installing required spaCy model for simple-anonymizer...")
                success = install_spacy_model("en_core_web_lg")
                if success:
                    print("✅ spaCy model installed successfully!")
                return success
            except ImportError:
                pass
        return False


# Only auto-install if spaCy is available but model is missing
try:
    import spacy
    _ensure_spacy_models()
except ImportError:
    pass  # spaCy not installed, skip auto-setup
