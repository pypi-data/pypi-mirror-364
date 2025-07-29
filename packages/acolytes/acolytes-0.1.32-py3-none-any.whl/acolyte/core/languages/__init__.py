"""
Language support module for Acolyte.

Provides language-specific labels and formatting for user prompts.
"""

from .es import USER_PROMPT_LABELS as ES_LABELS
from .en import USER_PROMPT_LABELS as EN_LABELS

# Language mapping
LANGUAGE_LABELS = {
    "es": ES_LABELS,
    "en": EN_LABELS,
}


def get_prompt_labels(language: str) -> dict:
    """
    Get prompt labels for the specified language.

    Args:
        language: Language code ('es' or 'en')

    Returns:
        Dictionary with language-specific labels

    Raises:
        ValueError: If language is not supported
    """
    if language not in LANGUAGE_LABELS:
        raise ValueError(
            f"Language '{language}' not supported. Available: {list(LANGUAGE_LABELS.keys())}"
        )

    return LANGUAGE_LABELS[language]


__all__ = ["get_prompt_labels", "LANGUAGE_LABELS"]
