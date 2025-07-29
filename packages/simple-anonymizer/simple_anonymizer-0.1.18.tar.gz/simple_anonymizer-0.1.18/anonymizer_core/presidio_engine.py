"""Presidio-based PII detection and anonymization."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging
import os

# Configure logging to reduce Presidio warnings
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
logging.getLogger("presidio-anonymizer").setLevel(logging.ERROR)

# Import configuration
from .presidio_config import NLP_CONFIGURATION, INTERNATIONAL_PATTERNS

# Optional Presidio imports
presidio_analyzer: Optional[Any] = None
presidio_anonymizer: Optional[Any] = None
spacy: Optional[Any] = None

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    import spacy as _spacy

    presidio_analyzer = AnalyzerEngine
    presidio_anonymizer = AnonymizerEngine
    spacy = _spacy
    logging.info("Presidio and spaCy successfully imported.")
except ImportError as e:
    logging.warning(f"Presidio not available: {e}")


class PresidioEngine:
    """Enhanced PII detection and anonymization using Microsoft Presidio."""

    def __init__(self, model_name: str = "en_core_web_lg") -> None:
        """Initialize Presidio engine with specified spaCy model."""
        if presidio_analyzer is None or presidio_anonymizer is None:
            raise RuntimeError(
                "Presidio not available. Install with: "
                "pip install presidio-analyzer presidio-anonymizer"
            )

        self.model_name = model_name
        self._analyzer: Optional[Any] = None
        self._anonymizer: Optional[Any] = None
        self._nlp: Optional[Any] = None

        # Default entities to detect - using ALL available Presidio entities
        self.default_entities = [
            # Core PII entities
            "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
            "IBAN_CODE", "US_SSN", "US_PASSPORT", "US_DRIVER_LICENSE",
            "UK_NHS", "URL", "IP_ADDRESS", "DATE_TIME", "LOCATION",
            "ORGANIZATION", "MEDICAL_LICENSE", "US_BANK_NUMBER",

            # Additional US entities
            "US_ITIN", "US_DEA", "US_NPI", "US_CPT_CODE", "US_HCPCS",
            "US_NDC", "US_DMV", "US_SSN", "US_PASSPORT", "US_DRIVER_LICENSE",

            # International entities
            "UK_NHS", "UK_NINO", "UK_UTR", "UK_POSTCODE",
            "AU_ABN", "AU_ACN", "AU_TFN", "AU_MEDICARE",
            "CA_SIN", "CA_PASSPORT", "CA_DRIVER_LICENSE",
            "IN_AADHAAR", "IN_PAN", "IN_PASSPORT",
            "SG_NRIC_FIN", "SG_PASSPORT",
            "ZA_ID", "ZA_PASSPORT",

            # Financial entities
            "CREDIT_CARD", "IBAN_CODE", "US_BANK_NUMBER",
            "CRYPTO", "BITCOIN_ADDRESS", "ETHEREUM_ADDRESS",

            # Technical entities
            "IP_ADDRESS", "IPV6_ADDRESS", "MAC_ADDRESS",
            "DOMAIN_NAME", "EMAIL_ADDRESS", "URL",

            # Medical/Healthcare entities
            "MEDICAL_LICENSE", "US_NPI", "AU_MEDICARE",

            # Document entities
            "US_CPT_CODE", "US_HCPCS", "US_NDC",

            # Location entities
            "LOCATION", "COUNTRY", "CITY", "STATE",

            # Organization entities
            "ORGANIZATION", "COMPANY", "GOVERNMENT",

            # Date/Time entities
            "DATE_TIME", "DATE", "TIME",

            # Custom medical/regulatory entities
            "MDR_CERTIFICATE", "IVDR_CERTIFICATE", "BSI_REFERENCE", "CE_MARKING",
            "SSN_PATTERN", "SSN_PATTERN_ALT", "STREET_ADDRESS", "ZIP_CODE",
            "MEDICARE_ID", "PATIENT_ID", "MEDICAL_CENTER", "HOSPITAL", "CLINIC"
        ]

        # Custom entity patterns
        self.custom_patterns = {
            "MDR_CERTIFICATE": r'\bMDR\d{6,}\b',
            "IVDR_CERTIFICATE": r'\bIVDR\d{6,}\b',
            "BSI_REFERENCE": r'\bBSI[-\s]?\w+\b',
            "CE_MARKING": r'\bCE\s+\d{4}\b',
            # Enhanced SSN patterns
            "SSN_PATTERN": r'\b\d{3}-\d{2}-\d{4}\b',
            "SSN_PATTERN_ALT": r'\b\d{9}\b',
            # Address patterns
            "STREET_ADDRESS": r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Drive|Dr|Road|Rd|Boulevard|Blvd|Lane|Ln|Place|Pl|Court|Ct|Way|Terrace|Ter)\b',
            "ZIP_CODE": r'\b\d{5}(?:-\d{4})?\b',
            # Medical patterns
            "MEDICARE_ID": r'\b[A-Z0-9]{4}-[A-Z0-9]{3}-[A-Z0-9]{4}\b',
            "PATIENT_ID": r'\b[A-Z]{3}\d{4}\b',
            # Organization patterns
            "MEDICAL_CENTER": r'\b[A-Za-z\s]+Medical\s+Center\b',
            "HOSPITAL": r'\b[A-Za-z\s]+Hospital\b',
            "CLINIC": r'\b[A-Za-z\s]+Clinic\b'
        }

    @property
    def analyzer(self) -> Any:
        """Lazy load Presidio analyzer."""
        if self._analyzer is None:
            self._setup_analyzer()
        return self._analyzer

    @property
    def anonymizer(self) -> Any:
        """Lazy load Presidio anonymizer."""
        if self._anonymizer is None:
            if presidio_anonymizer is None:
                raise RuntimeError("Presidio anonymizer not available")
            self._anonymizer = presidio_anonymizer()
        return self._anonymizer

    @property
    def nlp(self) -> Any:
        """Lazy load spaCy model."""
        if self._nlp is None:
            self._setup_nlp()
        return self._nlp

    def _setup_nlp(self) -> None:
        """Setup spaCy NLP model with fallback options."""
        if spacy is None:
            logging.error("spaCy not available for Presidio.")
            raise RuntimeError("spaCy not available")

        # Try to load models in order of preference
        models_to_try = [
            self.model_name,
            "en_core_web_lg",
            "en_core_web_md",
            "en_core_web_sm"
        ]

        for model in models_to_try:
            try:
                # Handle PyInstaller bundle
                if getattr(sys, 'frozen', False):
                    bundle_dir = Path(getattr(sys, '_MEIPASS', ''))
                    # Try multiple possible paths for the model
                    possible_paths = [
                        os.path.join(bundle_dir, 'en_core_web_lg'),
                        os.path.join(bundle_dir, 'Contents', 'MacOS', 'en_core_web_lg'),
                        os.path.join(bundle_dir, 'Contents', 'MacOS', 'en_core_web_lg', 'en_core_web_lg-3.8.0')
                    ]

                    for model_path in possible_paths:
                        if os.path.exists(model_path):
                            try:
                                self._nlp = spacy.load(model_path)
                                logging.info(f"Loaded spaCy model from bundle: {model_path}")
                                return
                            except Exception as e:
                                logging.warning(f"Failed to load from {model_path}: {e}")
                                continue
                # Try standard loading
                if spacy.util.is_package(model):
                    self._nlp = spacy.load(model)
                    logging.info(f"Loaded spaCy model: {model}")
                    return
            except (OSError, IOError) as e:
                logging.warning(f"Failed to load spaCy model {model}: {e}")
                continue
        logging.error(f"Could not load any spaCy model. Tried: {models_to_try}")
        raise RuntimeError(
            f"Could not load any spaCy model. "
            f"Please install one of: {', '.join(models_to_try)}"
        )

    def _setup_analyzer(self) -> None:
        """Setup Presidio analyzer with custom recognizers."""
        if presidio_analyzer is None:
            logging.error("Presidio analyzer not available.")
            raise RuntimeError("Presidio analyzer not available")

        # Setup NLP engine with comprehensive configuration
        nlp_configuration = NLP_CONFIGURATION.copy()
        nlp_configuration["models"] = [{"lang_code": "en", "model_name": self.model_name}]

        try:
            nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
            logging.info(f"Created NLP engine with model: {self.model_name}")
        except Exception as e:
            logging.warning(f"Failed to create NLP engine with {self.model_name}: {e}")
            # Fallback to default configuration
            nlp_engine = NlpEngineProvider().create_engine()
            logging.info("Falling back to default NLP engine configuration.")

        # Create analyzer
        self._analyzer = presidio_analyzer(nlp_engine=nlp_engine)
        logging.info("Presidio analyzer initialized.")

        # Add custom recognizers
        self._add_custom_recognizers()

        # Configure language support to reduce warnings
        self._configure_language_support()

    def _configure_language_support(self) -> None:
        """Configure language support to reduce warnings."""
        if self._analyzer is None:
            return

                # Add English language support for international recognizers
        try:
            from presidio_analyzer import Pattern, PatternRecognizer

            for entity_name, pattern in INTERNATIONAL_PATTERNS.items():
                recognizer = PatternRecognizer(
                    supported_entity=entity_name,
                    patterns=[Pattern(name=f"{entity_name.lower()}_pattern", regex=pattern, score=0.9)],
                    supported_language="en"  # Add English support
                )
                self._analyzer.registry.add_recognizer(recognizer)

        except Exception as e:
            logging.warning(f"Failed to configure international recognizers: {e}")

    def _add_custom_recognizers(self) -> None:
        """Add custom pattern recognizers for medical device certificates."""
        if self._analyzer is None:
            return

        from presidio_analyzer import Pattern, PatternRecognizer

        for entity_name, pattern in self.custom_patterns.items():
            recognizer = PatternRecognizer(
                supported_entity=entity_name,
                patterns=[Pattern(name=f"{entity_name.lower()}_pattern", regex=pattern, score=0.9)]
            )
            self._analyzer.registry.add_recognizer(recognizer)

    def get_all_available_entities(self) -> List[str]:
        """Get all available entities that Presidio can detect."""
        if self._analyzer is None:
            self._setup_analyzer()

        if self._analyzer is None:
            return []

        available_entities = set()

        # Get entities from all recognizers in the registry
        for recognizer in self._analyzer.registry.get_recognizers("en"):
            if hasattr(recognizer, 'supported_entities'):
                available_entities.update(recognizer.supported_entities)
            elif hasattr(recognizer, 'supported_entity'):
                available_entities.add(recognizer.supported_entity)

        # Add our custom entities
        available_entities.update(self.custom_patterns.keys())

        return sorted(list(available_entities))

    def get_recognizer_info(self) -> Dict[str, List[str]]:
        """Get information about all available recognizers and their supported entities."""
        if self._analyzer is None:
            self._setup_analyzer()

        if self._analyzer is None:
            return {}

        recognizer_info: Dict[str, List[str]] = {}

        for recognizer in self._analyzer.registry.get_recognizers("en"):
            recognizer_name = recognizer.__class__.__name__
            if hasattr(recognizer, 'supported_entities'):
                entities = recognizer.supported_entities
            elif hasattr(recognizer, 'supported_entity'):
                entities = [recognizer.supported_entity]
            else:
                entities = []

            if recognizer_name not in recognizer_info:
                recognizer_info[recognizer_name] = []
            recognizer_info[recognizer_name].extend(entities)

        return recognizer_info

    def detect_entities(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        language: str = "en"
    ) -> List[Tuple[str, str, float, int, int]]:
        """
        Detect PII entities in text.

        Returns:
            List of tuples: (entity_text, entity_type, confidence, start, end)
        """
        if entities is None:
            entities = self.default_entities

        try:
            results = self.analyzer.analyze(
                text=text,
                entities=entities,
                language=language
            )

            # Convert Presidio results to our format
            detected_entities = []
            for result in results:
                entity_text = text[result.start:result.end]
                detected_entities.append((
                    entity_text,
                    result.entity_type,
                    result.score,
                    result.start,
                    result.end
                ))

            return detected_entities

        except Exception as e:
            logging.error(f"Error in Presidio entity detection: {e}")
            return []

    def anonymize_text(
        self,
        text: str,
        entities: Optional[List[str]] = None,
        language: str = "en",
        anonymize_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize PII in text using Presidio.

        Returns:
            Tuple of (anonymized_text, mapping_dict)
        """
        if entities is None:
            entities = self.default_entities

        # Detect entities
        analyzer_results = self.analyzer.analyze(
            text=text,
            entities=entities,
            language=language
        )

        # Configure anonymization operators
        if anonymize_config is None:
            anonymize_config = self._get_default_anonymize_config()

        # Perform anonymization
        try:
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=anonymize_config
            )

            # Create mapping from original to anonymized
            mapping = self._create_mapping(text, analyzer_results, anonymized_result.text)

            return anonymized_result.text, mapping

        except Exception as e:
            logging.error(f"Error in Presidio anonymization: {e}")
            return text, {}

    def _get_default_anonymize_config(self) -> Dict[str, OperatorConfig]:
        """Get default anonymization configuration with ALL available entities."""
        from presidio_anonymizer.entities import OperatorConfig

        # Create a comprehensive configuration for all possible entities
        config = {}

        # All the entities we want to detect
        all_entities = [
            # Core PII entities
            "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
            "IBAN_CODE", "US_SSN", "US_PASSPORT", "US_DRIVER_LICENSE",
            "UK_NHS", "URL", "IP_ADDRESS", "DATE_TIME", "LOCATION",
            "ORGANIZATION", "MEDICAL_LICENSE", "US_BANK_NUMBER",

            # Additional US entities
            "US_ITIN", "US_DEA", "US_NPI", "US_CPT_CODE", "US_HCPCS",
            "US_NDC", "US_DMV",

            # International entities
            "UK_NINO", "UK_UTR", "UK_POSTCODE",
            "AU_ABN", "AU_ACN", "AU_TFN", "AU_MEDICARE",
            "CA_SIN", "CA_PASSPORT", "CA_DRIVER_LICENSE",
            "IN_AADHAAR", "IN_PAN", "IN_PASSPORT",
            "SG_NRIC_FIN", "SG_PASSPORT",
            "ZA_ID", "ZA_PASSPORT",

            # Financial entities
            "CRYPTO", "BITCOIN_ADDRESS", "ETHEREUM_ADDRESS",

            # Technical entities
            "IPV6_ADDRESS", "MAC_ADDRESS", "DOMAIN_NAME",

            # Medical/Healthcare entities
            "AU_MEDICARE",

            # Document entities
            "US_CPT_CODE", "US_HCPCS", "US_NDC",

            # Location entities
            "COUNTRY", "CITY", "STATE",

            # Organization entities
            "COMPANY", "GOVERNMENT",

            # Date/Time entities
            "DATE", "TIME",

            # Custom medical/regulatory entities
            "MDR_CERTIFICATE", "IVDR_CERTIFICATE", "BSI_REFERENCE", "CE_MARKING",
            "SSN_PATTERN", "SSN_PATTERN_ALT", "STREET_ADDRESS", "ZIP_CODE",
            "MEDICARE_ID", "PATIENT_ID", "MEDICAL_CENTER", "HOSPITAL", "CLINIC"
        ]

        # Configure all entities to use "<REDACTED>"
        for entity in all_entities:
            config[entity] = OperatorConfig("replace", {"new_value": "<REDACTED>"})

        return config

    def _create_mapping(
        self,
        original_text: str,
        analyzer_results: List[Any],
        anonymized_text: str
    ) -> Dict[str, str]:
        """Create mapping from original entities to anonymized placeholders."""
        mapping = {}

        # Sort results by start position (descending) to handle overlaps
        sorted_results = sorted(analyzer_results, key=lambda x: x.start, reverse=True)

        for result in sorted_results:
            original_entity = original_text[result.start:result.end]
            if original_entity not in mapping:
                # Find the corresponding anonymized placeholder
                # This is simplified - in practice you'd need more sophisticated mapping
                entity_type = result.entity_type
                placeholder = f"{entity_type}_{{random_int}}"
                mapping[original_entity] = placeholder

        return mapping

    def is_available(self) -> bool:
        """Check if Presidio is available and properly configured."""
        try:
            _ = self.analyzer
            _ = self.anonymizer
            _ = self.nlp
            return True
        except Exception:
            return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics and configuration info."""
        stats = {
            "presidio_available": self.is_available(),
            "model_name": self.model_name,
            "default_entities_count": len(self.default_entities),
            "custom_patterns_count": len(self.custom_patterns),
            "warnings_suppressed": True
        }

        if self._analyzer is not None:
            try:
                recognizers = self._analyzer.registry.get_recognizers("en")
                stats["recognizers_count"] = len(recognizers)
                stats["recognizer_types"] = [r.__class__.__name__ for r in recognizers]
            except Exception:
                stats["recognizers_count"] = 0
                stats["recognizer_types"] = []

        return stats


# Global instance for easy access
_presidio_engine: Optional[PresidioEngine] = None


def get_presidio_engine() -> Optional[PresidioEngine]:
    """Get global Presidio engine instance."""
    global _presidio_engine
    if _presidio_engine is None and presidio_analyzer is not None:
        try:
            _presidio_engine = PresidioEngine()
            logging.info("Presidio engine instance created.")
        except Exception as e:
            logging.warning(f"Failed to initialize Presidio engine: {e}")
    return _presidio_engine


def is_presidio_available() -> bool:
    """Check if Presidio is available for use."""
    return presidio_analyzer is not None and presidio_anonymizer is not None
