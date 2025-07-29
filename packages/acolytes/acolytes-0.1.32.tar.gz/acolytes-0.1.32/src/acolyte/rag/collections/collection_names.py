"""
Collection names enum for collections module.
Defines ACOLYTE's 5 mandatory collections.
"""

from enum import Enum


class CollectionName(str, Enum):
    """Enum for Weaviate collection names to avoid typos."""

    CONVERSATION = "Conversation"
    CODE_CHUNK = "CodeChunk"
    DOC_CHUNK = "DocChunk"
    CONFIG_CHUNK = "ConfigChunk"
    TEST_CHUNK = "TestChunk"
    TASK = "Task"
    DREAM_INSIGHT = "DreamInsight"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def list_all(cls) -> list[str]:
        """Return all collection names as a list of strings."""
        return [item.value for item in cls]


# For backward compatibility or direct use
CONVERSATION = CollectionName.CONVERSATION
CODE_CHUNK = CollectionName.CODE_CHUNK
DOC_CHUNK = CollectionName.DOC_CHUNK
CONFIG_CHUNK = CollectionName.CONFIG_CHUNK
TEST_CHUNK = CollectionName.TEST_CHUNK
TASK = CollectionName.TASK
DREAM_INSIGHT = CollectionName.DREAM_INSIGHT
