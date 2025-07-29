"""
Embeddings module for ACOLYTE.

Generates vector representations of code using UniXcoder
for advanced semantic search.
"""

from typing import TYPE_CHECKING

from acolyte.core.logging import logger

# Always import lightweight types
from acolyte.embeddings.types import (
    EmbeddingVector,
    EmbeddingsMetricsSummaryDict,
    RerankerMetricsSummary,
    MetricsProvider,
)

# Lazy imports for heavy modules
if TYPE_CHECKING:
    from acolyte.embeddings.unixcoder import UniXcoderEmbeddings
    from acolyte.embeddings.context import RichCodeContext, RichCodeContextDict
    from acolyte.embeddings.reranker import CrossEncoderReranker
    from acolyte.embeddings.cache import ContextAwareCache, CacheEntry, CacheStats
    from acolyte.embeddings.persistent_cache import SmartPersistentCache
    from acolyte.embeddings.metrics import (
        EmbeddingsMetrics,
        PerformanceMetrics,
        SearchQualityMetrics,
        PerformanceStatsDict,
        SearchQualityReport,
        EmbeddingsMetricsSummary,
    )

# Thread-safe singletons
_embeddings_instance = None
_reranker_instance = None
_metrics_instance = None

# Compatible async/thread lock - lazy creation to avoid event loop binding issues
_lock = None


def _get_lock():
    """Get or create a thread-safe lock that works with asyncio."""
    global _lock
    if _lock is None:
        import threading

        _lock = threading.RLock()  # Use RLock instead of Lock for re-entrance
    return _lock


def get_embeddings():  # -> UniXcoderEmbeddings
    """Returns the unique instance of the embeddings generator.

    Implements the Singleton thread-safe pattern using Double-Checked Locking (DCL).

    Why is DCL necessary?
    ====================================

    1. **Concurrency problem**: In FastAPI, multiple requests can call
       get_embeddings() simultaneously in different threads.

    2. **Costly load**: UniXcoder takes ~3-30 seconds to load. Without synchronization,
       we could load the model multiple times wasting memory and CPU.

    3. **DCL solution**: We check twice with a lock in between:
       - First check (without lock): Fast, avoids lock in the common case
       - Lock: Guarantees that only one thread can create the instance
       - Second check (with lock): Avoids duplicates if another thread
         already created the instance while we were waiting

    Benefits:
    - Only the model is loaded once (saves ~1GB RAM)
    - Thread-safe without penalizing performance after initialization
    - Robust error handling without leaving the state corrupted

    Returns:
        Singleton instance of UniXcoderEmbeddings

    Raises:
        Exception: If the model initialization fails
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        with _get_lock():
            # Double-check locking pattern
            if _embeddings_instance is None:
                try:
                    # Lazy import
                    from acolyte.embeddings.unixcoder import UniXcoderEmbeddings

                    # Create temporary instance first
                    temp_instance = UniXcoderEmbeddings()
                    # Only assign to singleton if initialization was successful
                    _embeddings_instance = temp_instance
                except Exception as e:
                    print(f"[PRINT] Exception in get_embeddings: {e}")
                    # If initialization fails, don't leave the singleton corrupted
                    # Re-raise the exception so the caller can handle it
                    raise Exception(f"Failed to initialize UniXcoderEmbeddings: {e}") from e
    return _embeddings_instance


def get_reranker():  # -> CrossEncoderReranker
    """Returns the unique instance of the re-ranker.

    Implements the Singleton thread-safe pattern using Double-Checked Locking.
    See get_embeddings() for detailed explanation of the DCL pattern.

    Specific to CrossEncoderReranker:
    - Smaller model (~400MB) but still costly to load
    - Used less frequently (only in advanced re-ranking)
    - Shares device with UniXcoderEmbeddings for efficiency

    Returns:
        Singleton instance of CrossEncoderReranker

    Raises:
        Exception: If the model initialization fails
    """
    global _reranker_instance
    if _reranker_instance is None:
        with _get_lock():
            # Double-check locking pattern
            if _reranker_instance is None:
                try:
                    # Lazy import
                    from acolyte.embeddings.reranker import CrossEncoderReranker

                    # Create temporary instance first
                    temp_instance = CrossEncoderReranker()
                    # Only assign to singleton if initialization was successful
                    _reranker_instance = temp_instance
                except Exception as e:
                    raise Exception(f"Failed to initialize CrossEncoderReranker: {e}") from e
    return _reranker_instance


def get_embeddings_metrics():  # -> Optional[MetricsProvider]
    """Returns the unique instance of the embeddings metrics module.

    Implements the Singleton thread-safe pattern to share metrics
    between UniXcoderEmbeddings and CrossEncoderReranker.

    IMPORTANT: Only created if enable_metrics is enabled in the configuration.

    Returns:
        MetricsProvider or None if metrics are disabled.
        The Protocol type allows flexibility in implementation.
    """
    global _metrics_instance

    # Check if metrics are enabled
    from acolyte.core.secure_config import get_settings

    config = get_settings()
    if not config.get("embeddings.enable_metrics", True):
        return None

    if _metrics_instance is None:
        with _get_lock():
            # Double-check locking pattern
            if _metrics_instance is None:
                try:
                    # Lazy import
                    from acolyte.embeddings.metrics import EmbeddingsMetrics

                    _metrics_instance = EmbeddingsMetrics()
                    logger.info("EmbeddingsMetrics singleton created")
                except Exception as e:
                    logger.error("Failed to initialize EmbeddingsMetrics", error=str(e))
                    return None
    return _metrics_instance


# Lazy attribute access for other exports
def __getattr__(name):
    """Lazy load module attributes."""
    # Classes that need lazy loading
    lazy_imports = {
        "UniXcoderEmbeddings": "acolyte.embeddings.unixcoder",
        "CrossEncoderReranker": "acolyte.embeddings.reranker",
        "RichCodeContext": "acolyte.embeddings.context",
        "RichCodeContextDict": "acolyte.embeddings.context",
        "ContextAwareCache": "acolyte.embeddings.cache",
        "CacheEntry": "acolyte.embeddings.cache",
        "CacheStats": "acolyte.embeddings.cache",
        "SmartPersistentCache": "acolyte.embeddings.persistent_cache",
        "EmbeddingsMetrics": "acolyte.embeddings.metrics",
        "PerformanceMetrics": "acolyte.embeddings.metrics",
        "SearchQualityMetrics": "acolyte.embeddings.metrics",
        "PerformanceStatsDict": "acolyte.embeddings.metrics",
        "SearchQualityReport": "acolyte.embeddings.metrics",
        "EmbeddingsMetricsSummary": "acolyte.embeddings.metrics",
    }

    if name in lazy_imports:
        import importlib

        module = importlib.import_module(lazy_imports[name])
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Public exports of the module
__all__ = [
    # Standard types (always available)
    "EmbeddingVector",
    # Protocol to prevent circular imports
    "MetricsProvider",
    # Main classes (lazy loaded)
    "UniXcoderEmbeddings",
    "CrossEncoderReranker",
    "RichCodeContext",
    # Cache
    "ContextAwareCache",
    "CacheEntry",
    "CacheStats",
    "SmartPersistentCache",
    # Metrics
    "EmbeddingsMetrics",
    "PerformanceMetrics",
    "SearchQualityMetrics",
    # TypedDicts for improved type safety
    "RichCodeContextDict",
    "EmbeddingsMetricsSummaryDict",
    "RerankerMetricsSummary",
    "PerformanceStatsDict",
    "SearchQualityReport",
    "EmbeddingsMetricsSummary",
    # Singleton functions
    "get_embeddings",
    "get_reranker",
    "get_embeddings_metrics",
]
