"""spaCy NER wrapper."""

from __future__ import annotations

from types import ModuleType
from typing import Optional, Any
import sys

spacy: Optional[ModuleType]
try:
    import spacy as _spacy
except Exception:  # pragma: no cover - optional dependency
    spacy = None
else:
    spacy = _spacy


class SpacyNER:
    """Thin wrapper around spaCy pipeline with lazy loading."""

    def __init__(self, model: str = "en_core_web_lg") -> None:
        if spacy is None:
            raise RuntimeError("spaCy not installed")

        self.model = model
        self._nlp = None  # Lazy loading - only load when first used

    @property
    def nlp(self) -> Any:  # noqa: ANN401
        """Lazy load the spaCy model only when first accessed."""
        if self._nlp is None:
            import os

            # If running in PyInstaller bundle, load model from bundled path
            if getattr(sys, "frozen", False):
                bundle_dir = getattr(sys, "_MEIPASS", "")
                # Try multiple possible paths for the model
                possible_paths = [
                    os.path.join(bundle_dir, "en_core_web_lg"),
                    os.path.join(bundle_dir, "Contents", "MacOS", "en_core_web_lg"),
                    os.path.join(bundle_dir, "Contents", "MacOS", "en_core_web_lg", "en_core_web_lg-3.8.0")
                ]

                for model_path in possible_paths:
                    if os.path.exists(model_path):
                        try:
                            self._nlp = spacy.load(model_path)  # type: ignore
                            return self._nlp
                        except Exception as e:
                            import logging
                            logging.warning(f"Failed to load from {model_path}: {e}")
                            continue

                raise RuntimeError(
                    f"Failed to load spaCy model from bundled paths {possible_paths}: not found."
                )
            else:
                # If the requested model isn't available, try to download it
                if not spacy.util.is_package(self.model):  # type: ignore
                    try:
                        import importlib
                        importlib.import_module("spacy.cli").download(self.model)
                    except Exception as e:
                        raise RuntimeError(
                            f"Failed to download spaCy model '{self.model}': {e}"
                        ) from e
                try:
                    self._nlp = spacy.load(self.model)  # type: ignore
                except OSError as e:
                    raise RuntimeError(
                        f"Failed to load spaCy model '{self.model}': {e}"
                    ) from e

        return self._nlp

    def extract(self, text: str) -> list[tuple[str, str]]:
        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            # Normalize entity labels for better anonymization
            label = ent.label_
            entity_text = ent.text.strip()

            # Skip certain entity types that are usually not sensitive
            if label in ("CARDINAL", "ORDINAL", "QUANTITY", "PERCENT", "MONEY", "TIME"):
                continue

            # Skip common file formats and technical terms
            if entity_text.upper() in (
                "PDF",
                "DOC",
                "DOCX",
                "XLS",
                "XLSX",
                "PPT",
                "PPTX",
                "TXT",
                "CSV",
            ):
                continue

            # Skip common business terms that might be misclassified
            # Use lemmatization for more robust matching
            if self._is_business_term_with_lemma(entity_text):
                continue

            # Skip common compound phrases that shouldn't be redacted
            if self._is_common_phrase(entity_text):
                continue

            # Map organization-related labels to a consistent COMPANY label
            # But be more selective about what we consider a company
            if label in ("ORG", "ORGANIZATION"):
                # Skip single word "organizations" that are likely just roles/titles
                # Use lemmatization for more robust role detection
                if len(entity_text.split()) == 1 and self._is_role_title_with_lemma(entity_text):
                    continue

                # Skip entities that start with common greetings and likely
                # contain person names
                if entity_text.lower().startswith(
                    ("dear ", "mr ", "ms ", "mrs ", "dr ")
                ):
                    # Extract the potential person name from the greeting
                    name_part = (
                        entity_text.split(" ", 1)[1] if " " in entity_text else ""
                    )
                    if name_part:
                        # Add the person name as a separate PERSON entity
                        entities.append((name_part, "PERSON"))
                    continue

                label = "COMPANY"
            # Map location labels
            elif label in ("GPE", "LOC", "LOCATION"):
                label = "LOCATION"
            # Map person labels
            elif label in ("PERSON", "PER"):
                label = "PERSON"
            # Map miscellaneous entities that might be sensitive
            elif label in ("MISC", "PRODUCT", "WORK_OF_ART", "EVENT"):
                label = "ENTITY"
            # Map dates but be selective
            elif label in ("DATE", "TIME"):
                # Only redact specific dates, not general time references
                if any(char.isdigit() for char in entity_text):
                    label = "DATE"
                else:
                    continue

            entities.append((entity_text, label))

        return entities

    def _is_business_term_with_lemma(self, text: str) -> bool:
        """Check if text is a business term using lemmatization for robust matching."""
        # Import here to avoid circular imports
        try:
            from .dictionary import _lemmatize_word
        except ImportError:
            # Fallback to simple matching if lemmatization not available
            return text.lower() in (
                "reviewer",
                "manager",
                "coordinator",
                "specialist",
                "scheme",
                "response",
                "responses",
                "regarding",
            )

        # Business terms that should not be redacted (base forms)
        business_terms = {
            "reviewer", "review", "manager", "manage", "coordinator", "coordinate",
            "specialist", "special", "scheme", "response", "respond", "regarding", "regard",
            "management", "director", "direct", "supervisor", "supervise",
            "administrator", "administer", "executive", "execute", "officer",
            "assistant", "assist", "representative", "represent", "analyst", "analyze",
            "consultant", "consult", "engineer", "developer", "develop", "designer", "design",
            "technician", "technical",
            # Common closings and greetings
            "kind", "regards", "best", "sincerely", "truly", "faithfully", "greetings",
            "dear", "hello", "hi", "hey",
            # Common business words
            "round", "app", "application", "document", "file", "form", "report",
            "question", "answer", "information", "data", "system", "process",
            "evaluation", "assessment", "analysis", "study", "research"
        }

        text_lower = text.lower()

        # Check exact match first
        if text_lower in business_terms:
            return True

        # Check lemmatized form
        try:
            lemma = _lemmatize_word(text_lower)
            return lemma in business_terms
        except Exception:
            return False

    def _is_role_title_with_lemma(self, text: str) -> bool:
        """Check if text is a role/title using lemmatization for robust matching."""
        try:
            from .dictionary import _lemmatize_word
        except ImportError:
            # Fallback to simple matching if lemmatization not available
            return text.lower() in (
                "reviewer", "manager", "director", "coordinator", "specialist",
                "analyst", "consultant", "engineer", "developer", "designer",
                "administrator", "supervisor", "executive", "officer", "assistant"
            )

        # Role titles that should not be redacted (base forms)
        role_titles = {
            "reviewer", "review", "manager", "manage", "director", "direct",
            "coordinator", "coordinate", "specialist", "special", "analyst", "analyze",
            "consultant", "consult", "engineer", "developer", "develop", "designer",
            "design", "administrator", "administer", "supervisor", "supervise",
            "executive", "execute", "officer", "assistant", "assist", "representative",
            "represent", "agent", "advisor", "advise", "auditor", "audit",
            "inspector", "inspect", "professor", "doctor", "researcher", "research",
            "scientist", "physician", "nurse", "therapist", "therapy", "technician",
            "technical", "student", "instructor", "instruct", "president",
            "chairman", "founder", "partner", "associate", "principal"
        }

        text_lower = text.lower()

        # Check exact match first
        if text_lower in role_titles:
            return True

        # Check lemmatized form
        try:
            lemma = _lemmatize_word(text_lower)
            return lemma in role_titles
        except Exception:
            return False

    def _is_common_phrase(self, text: str) -> bool:
        """Check if text is a common phrase that shouldn't be redacted."""
        common_phrases = {
            "kind regards", "best regards", "yours truly", "yours sincerely",
            "yours faithfully", "thank you", "please note", "please find",
            "please contact", "please provide", "please complete",
            "ai expert", "expert review", "review questions", "manufacturer response",
            "red lined", "red-lined", "single bookmarked", "client portal",
            "conference call", "round 2", "app -", "myreha app", "word document",
            "pdf file", "supporting documentation", "review schedule",
            "three rounds", "attached form", "this review", "each form",
            "continuation of", "these circumstances", "expected date"
        }

        text_lower = text.lower().strip()
        return text_lower in common_phrases
