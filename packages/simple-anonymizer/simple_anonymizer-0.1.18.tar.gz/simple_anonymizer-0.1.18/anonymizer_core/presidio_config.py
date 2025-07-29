"""Presidio configuration settings."""

# Presidio NLP Configuration
NLP_CONFIGURATION = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
    # Comprehensive entity mapping to eliminate warnings
    "model_to_presidio_entity_mapping": {
        "PERSON": "PERSON",
        "ORG": "ORGANIZATION",
        "GPE": "LOCATION",
        "LOC": "LOCATION",
        "FAC": "LOCATION",  # Map FAC to LOCATION to eliminate warning
        "PRODUCT": "ORGANIZATION",
        "EVENT": "DATE_TIME",
        "WORK_OF_ART": "ORGANIZATION",
        "LAW": "ORGANIZATION",
        "LANGUAGE": "ORGANIZATION",
        "DATE": "DATE_TIME",
        "TIME": "DATE_TIME",
        "PERCENT": "DATE_TIME",
        "MONEY": "CREDIT_CARD",
        "QUANTITY": "DATE_TIME",
        "ORDINAL": "DATE_TIME",
        "CARDINAL": "DATE_TIME"
    },
    # Low score entities to ignore
    "low_score_entity_names": [
        "FAC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"
    ],
    # Labels to ignore completely
    "labels_to_ignore": [
        "FAC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"
    ]
}

# International recognizer patterns
INTERNATIONAL_PATTERNS = {
    "ES_NIF": r'\b[0-9]{8}[A-Z]\b',
    "ES_NIE": r'\b[A-Z][0-9]{7}[A-Z]\b',
    "IT_DRIVER_LICENSE": r'\b[A-Z]{2}[0-9]{7}\b',
    "IT_FISCAL_CODE": r'\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b',
    "IT_VAT_CODE": r'\bIT[0-9]{11}\b',
    "IT_IDENTITY_CARD": r'\b[A-Z]{2}[0-9]{7}\b',
    "IT_PASSPORT": r'\b[A-Z]{2}[0-9]{7}\b',
    "PL_PESEL": r'\b[0-9]{11}\b'
}

# Logging configuration
LOGGING_CONFIG = {
    "presidio_analyzer_level": "ERROR",
    "presidio_anonymizer_level": "ERROR",
    "presidio_engine_level": "INFO"
}

# Performance settings
PERFORMANCE_CONFIG = {
    "enable_caching": True,
    "cache_size": 1000,
    "enable_parallel_processing": False,
    "max_text_length": 100000
}