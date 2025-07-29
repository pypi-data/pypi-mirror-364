"""Integration layer for text-anonymizer library as lightweight fallback."""

from __future__ import annotations

from typing import Dict, Optional, Tuple, Any
import logging
import re

# Optional import - text-anonymizer is not required
try:
    from text_anonymizer import anonymize
    TEXT_ANONYMIZER_AVAILABLE = True
    logging.info("text-anonymizer library available for fallback processing")
except ImportError as e:
    TEXT_ANONYMIZER_AVAILABLE = False
    logging.info(f"text-anonymizer library not available: {e}")
except OSError as e:
    # Handle spaCy model loading errors from text-anonymizer
    TEXT_ANONYMIZER_AVAILABLE = False
    logging.warning(f"text-anonymizer library available but spaCy model missing: {e}")
    logging.info("text-anonymizer disabled due to missing spaCy model - install with: python -m spacy download en_core_web_sm")
except Exception as e:
    # Handle any other errors during text-anonymizer import
    TEXT_ANONYMIZER_AVAILABLE = False
    logging.warning(f"text-anonymizer library import failed: {e}")


class TextAnonymizerIntegration:
    """Integration layer for text-anonymizer library."""

    def __init__(self):
        """Initialize the integration layer."""
        self.available = TEXT_ANONYMIZER_AVAILABLE
        if not self.available:
            logging.info("text-anonymizer integration disabled - either library not installed or spaCy model missing")

    def is_available(self) -> bool:
        """Check if text-anonymizer is available."""
        return self.available

    def anonymize_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize text using text-anonymizer library.

        Args:
            text: Input text to anonymize

        Returns:
            Tuple of (anonymized_text, mapping_dict)
        """
        if not self.available:
            raise RuntimeError("text-anonymizer library not available")

        try:
            # Use text-anonymizer's anonymize function
            anonymized_text, anonymization_map = anonymize(text)

            # Convert text-anonymizer format to our format
            # text-anonymizer uses: [PERSON_1], [ORG_1], etc.
            # We use: <REDACTED>
            converted_text = anonymized_text
            converted_mapping = {}

            # Convert placeholders to our format
            for original, placeholder in anonymization_map.items():
                converted_text = converted_text.replace(placeholder, "<REDACTED>")
                converted_mapping[original] = "<REDACTED>"

            return converted_text, converted_mapping

        except Exception as e:
            logging.error(f"text-anonymizer anonymization failed: {e}")
            raise



    def _guess_entity_type(self, text: str) -> str:
        """Guess the entity type based on text patterns."""
        text_lower = text.lower()

        # Email pattern
        if '@' in text and '.' in text:
            return "EMAIL"

        # URL pattern
        if text.startswith(('http://', 'https://', 'www.')):
            return "URL"

        # Person name pattern (capitalized words)
        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', text):
            return "PERSON"

        # Organization pattern (contains common org words)
        org_words = ['inc', 'corp', 'company', 'llc', 'ltd', 'co', 'organization', 'association']
        if any(word in text_lower for word in org_words):
            return "ORG"

        # Location pattern (contains location indicators)
        location_words = ['street', 'avenue', 'road', 'drive', 'lane', 'city', 'state', 'country']
        if any(word in text_lower for word in location_words):
            return "LOCATION"

        # Default to PERSON for unknown types
        return "PERSON"

    def get_capabilities(self) -> Dict[str, Any]:
        """Get information about text-anonymizer capabilities."""
        return {
            "available": self.available,
            "entity_types": ["PERSON", "ORGANIZATION", "LOCATION", "EMAIL", "URL"],
            "features": [
                "Lightweight spaCy-based processing",
                "Consistent entity mapping",
                "LLM-optimized placeholders"
            ],
            "limitations": [
                "Limited entity types (5 vs 85+ in Presidio)",
                "No custom pattern support",
                "No medical/financial entity detection"
            ]
        }


# Global instance
_text_anonymizer_integration = None


def get_text_anonymizer_integration() -> Optional[TextAnonymizerIntegration]:
    """Get the global text-anonymizer integration instance."""
    global _text_anonymizer_integration
    if _text_anonymizer_integration is None:
        _text_anonymizer_integration = TextAnonymizerIntegration()
    return _text_anonymizer_integration


def is_text_anonymizer_available() -> bool:
    """Check if text-anonymizer integration is available."""
    integration = get_text_anonymizer_integration()
    return integration.is_available() if integration else False