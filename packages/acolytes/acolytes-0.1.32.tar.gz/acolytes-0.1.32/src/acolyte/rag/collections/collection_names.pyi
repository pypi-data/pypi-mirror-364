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

    def __str__(self) -> str: ...
    @classmethod
    def list_all(cls) -> list[str]: ...

# For backward compatibility or direct use
CONVERSATION: str
CODE_CHUNK: str
DOC_CHUNK: str
CONFIG_CHUNK: str
TEST_CHUNK: str
TASK: str
DREAM_INSIGHT: str
