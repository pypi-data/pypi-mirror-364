"""Lexicon loader reading pre-generated word lists."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Iterable, Set, Any
from unidecode import unidecode

# Global variables for spaCy model caching
_nlp_model = None
_lemma_cache = {}


def _get_nlp_model() -> Any | None:  # noqa: ANN401
    """Get or load the spaCy model for lemmatization."""
    global _nlp_model
    if _nlp_model is None:
        try:
            import spacy

            # Try to load the model from different paths
            try:
                import en_core_web_sm

                _nlp_model = en_core_web_sm.load()
            except ImportError:
                # Fallback to loading from PyInstaller bundle or standard installation
                import sys

                if getattr(sys, "frozen", False):
                    # Running in PyInstaller bundle
                    bundle_dir = Path(getattr(sys, "_MEIPASS", ""))
                    model_path = bundle_dir / "en_core_web_sm" / "en_core_web_sm-3.7.1"
                    if model_path.exists():
                        _nlp_model = spacy.load(str(model_path))
                    else:
                        _nlp_model = spacy.load("en_core_web_sm")
                else:
                    _nlp_model = spacy.load("en_core_web_sm")
        except Exception:
            # If spaCy fails, return None and fall back to non-lemmatized matching
            _nlp_model = None
    return _nlp_model


def _lemmatize_word(word: str) -> str:
    """Lemmatize a single word using spaCy."""
    global _lemma_cache

    if word in _lemma_cache:
        return _lemma_cache[word]

    nlp = _get_nlp_model()
    if nlp is None:
        # Fallback: return the word as-is if spaCy is not available
        _lemma_cache[word] = word.lower()
        return word.lower()

    try:
        doc = nlp(word)
        if doc and len(doc) > 0:
            lemma = doc[0].lemma_.lower()
            _lemma_cache[word] = lemma
            return lemma
        else:
            _lemma_cache[word] = word.lower()
            return word.lower()
    except Exception:
        # Fallback on any error
        _lemma_cache[word] = word.lower()
        return word.lower()


def _create_lemmatized_lexicon(words: Set[str]) -> Set[str]:
    """Create a lemmatized version of the lexicon for more robust matching."""
    lemmatized_words = set()

    for word in words:
        # Add both original and lemmatized forms
        lemmatized_words.add(word)
        lemma = _lemmatize_word(word)
        if lemma != word:
            lemmatized_words.add(lemma)

    return lemmatized_words


def load_lexicon(lang: str, paths: Iterable[str] | None = None) -> Set[str]:
    """Return a set of known words for ``lang`` merged with any ``paths``."""
    words: Set[str] = set()

    # Try multiple ways to load the lexicon file
    lexicon_loaded = False

    # Method 1: importlib.resources (works in normal Python)
    try:
        data_file = resources.files("data").joinpath(f"lexicon_{lang}.txt")
        words.update(
            unidecode(w.strip().lower())
            for w in data_file.read_text(encoding="utf-8").splitlines()
            if w.strip()
        )
        lexicon_loaded = True
    except (FileNotFoundError, AttributeError):
        pass

    # Method 2: PyInstaller bundle (when frozen)
    if not lexicon_loaded:
        try:
            import sys

            if getattr(sys, "frozen", False):
                # Running in PyInstaller bundle
                bundle_dir = Path(getattr(sys, "_MEIPASS", ""))
                lexicon_path = bundle_dir / "data" / f"lexicon_{lang}.txt"
            else:
                # Running in development
                lexicon_path = (
                    Path(__file__).parent.parent / "data" / f"lexicon_{lang}.txt"
                )

            if lexicon_path.exists():
                words.update(
                    unidecode(w.strip().lower())
                    for w in lexicon_path.read_text(encoding="utf-8").splitlines()
                    if w.strip()
                )
                lexicon_loaded = True
        except Exception:
            pass

    # Method 3: Fallback - relative to current directory
    if not lexicon_loaded:
        try:
            fallback_path = Path(f"data/lexicon_{lang}.txt")
            if fallback_path.exists():
                words.update(
                    unidecode(w.strip().lower())
                    for w in fallback_path.read_text(encoding="utf-8").splitlines()
                    if w.strip()
                )
        except Exception:
            pass

    if paths:
        for p in paths:
            for line in Path(p).read_text(encoding="utf-8").splitlines():
                words.add(unidecode(line.strip().lower()))

    # Create lemmatized version for more robust matching
    return _create_lemmatized_lexicon(words)


def _get_always_redact_path() -> Path:
    """Get the path to the always_redact.txt file in the user's home directory."""
    anonymizer_dir = Path.home() / ".anonymizer"
    anonymizer_dir.mkdir(exist_ok=True)
    return anonymizer_dir / "always_redact.txt"


def _ensure_always_redact_file() -> None:
    """Ensure the always_redact.txt file exists, creating it if necessary."""
    always_redact_path = _get_always_redact_path()
    if not always_redact_path.exists():
        always_redact_path.touch()


def load_always_redact_words(lang: str) -> Set[str]:
    """Return a set of words that should always be redacted, regardless of context."""
    words: Set[str] = set()
    
    # Ensure the file exists
    _ensure_always_redact_file()
    
    # Load from the user's .anonymizer directory
    always_redact_path = _get_always_redact_path()
    
    try:
        if always_redact_path.exists():
            words.update(
                w.strip()
                for w in always_redact_path.read_text(encoding="utf-8").splitlines()
                if w.strip()
            )
    except Exception:
        # If there's an error reading the file, just return empty set
        pass

    return words


def add_always_redact_word(word: str) -> bool:
    """
    Add a word to the always redact list.
    
    Args:
        word: The word to add to the always redact list
        
    Returns:
        True if word was added, False if it already existed
    """
    if not word or not word.strip():
        return False
        
    word = word.strip()
    
    # Ensure the file exists
    _ensure_always_redact_file()
    
    # Load existing words
    existing_words = load_always_redact_words("en")  # lang parameter is not used in our implementation
    
    # Check if word already exists (case-insensitive)
    existing_words_lower = {w.lower() for w in existing_words}
    if word.lower() in existing_words_lower:
        return False
    
    # Add the word
    existing_words.add(word)
    
    # Write back to file
    always_redact_path = _get_always_redact_path()
    try:
        with always_redact_path.open('w', encoding='utf-8') as f:
            for w in sorted(existing_words):
                f.write(f"{w}\n")
        return True
    except Exception:
        return False


def remove_always_redact_word(word: str) -> bool:
    """
    Remove a word from the always redact list.
    
    Args:
        word: The word to remove from the always redact list
        
    Returns:
        True if word was removed, False if it didn't exist
    """
    if not word or not word.strip():
        return False
        
    word = word.strip()
    
    # Ensure the file exists
    _ensure_always_redact_file()
    
    # Load existing words
    existing_words = load_always_redact_words("en")  # lang parameter is not used in our implementation
    
    # Find and remove the word (case-insensitive)
    word_to_remove = None
    for existing_word in existing_words:
        if existing_word.lower() == word.lower():
            word_to_remove = existing_word
            break
    
    if word_to_remove is None:
        return False
    
    existing_words.remove(word_to_remove)
    
    # Write back to file
    always_redact_path = _get_always_redact_path()
    try:
        with always_redact_path.open('w', encoding='utf-8') as f:
            for w in sorted(existing_words):
                f.write(f"{w}\n")
        return True
    except Exception:
        return False


def list_always_redact_words() -> Set[str]:
    """
    List all words in the always redact list.
    
    Returns:
        Set of words that are always redacted
    """
    return load_always_redact_words("en")  # lang parameter is not used in our implementation
