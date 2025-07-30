"""
nahiarhdNLP.preprocessing - Indonesian text preprocessing utilities

This module provides comprehensive text preprocessing functionality for Indonesian language,
including cleaning, normalization, tokenization, and linguistic processing.
"""

# Import all individual utility functions
from .utils import (
    # Basic cleaning functions
    remove_html,
    remove_url,
    remove_mentions,
    remove_hashtags,
    remove_numbers,
    remove_punctuation,
    remove_extra_spaces,
    remove_special_chars,
    remove_whitespace,
    to_lowercase,
    # Normalization and correction functions
    replace_spell_corrector,
    replace_repeated_chars,
    # Emoji functions
    emoji_to_words,
    words_to_emoji,
    # Linguistic functions
    remove_stopwords,
    stem_text,
    tokenize,
    # Pipeline functions
    Pipeline,
    pipeline,
    preprocess,
)

# Import all classes for advanced usage
from .cleaning.text_cleaner import TextCleaner
from .linguistic.stemmer import Stemmer
from .linguistic.stopwords import StopwordRemover
from .normalization.emoji import EmojiConverter
from .normalization.spell_corrector import SpellCorrector
from .tokenization.tokenizer import Tokenizer

# Define what gets imported with "from nahiarhdNLP.preprocessing import *"
__all__ = [
    # Individual functions
    "remove_html",
    "remove_url",
    "remove_mentions",
    "remove_hashtags",
    "remove_numbers",
    "remove_punctuation",
    "remove_extra_spaces",
    "remove_special_chars",
    "remove_whitespace",
    "to_lowercase",
    "replace_spell_corrector",
    "replace_repeated_chars",
    "emoji_to_words",
    "words_to_emoji",
    "remove_stopwords",
    "stem_text",
    "tokenize",
    # Pipeline functions
    "Pipeline",
    "pipeline",
    "preprocess",
    # Classes
    "TextCleaner",
    "Stemmer",
    "StopwordRemover",
    "EmojiConverter",
    "SpellCorrector",
    "Tokenizer",
]
