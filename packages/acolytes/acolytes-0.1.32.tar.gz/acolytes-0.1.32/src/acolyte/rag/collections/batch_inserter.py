"""
Weaviate Batch Inserter - Optimized batch insertion for collections.

This module handles efficient batch insertion of chunks into Weaviate,
with error handling, metrics, and automatic fallback.

Implements the official Weaviate v3 batch API pattern with asyncio support.
"""

import asyncio
import threading
from typing import List, Dict, Any, Tuple, Optional, TYPE_CHECKING, Set
from dataclasses import dataclass, field

from acolyte.core.logging import logger, PerformanceLogger
from acolyte.core.tracing import MetricsCollector
from acolyte.core.secure_config import Settings, get_settings
from acolyte.core.exceptions import ExternalServiceError

if TYPE_CHECKING:
    import weaviate


@dataclass
class BatchResult:
    """Result of a batch insertion operation."""

    successful: int = 0
    failed: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total objects processed."""
        return self.successful + self.failed


class WeaviateBatchInserter:
    """
    Optimized batch insertion for Weaviate collections.

    Features:
    - Configurable batch size from settings
    - Async support with run_in_executor (sync client in async context)
    - Detailed error tracking and metrics
    - Automatic retry on failures
    - Thread-safe operation (single batch at a time)
    """

    def __init__(self, weaviate_client: 'weaviate.Client', config: Optional[Settings] = None):
        """
        Initialize the batch inserter.

        Args:
            weaviate_client: Weaviate client instance
            config: Optional Settings instance (creates new if not provided)
        """
        self.client = weaviate_client
        self.config = config or get_settings()
        self.metrics = MetricsCollector()
        self.perf_logger = PerformanceLogger()

        # Get batch configuration
        self.batch_size = self.config.get("search.weaviate_batch_size", 100)
        self.num_workers = self.config.get("weaviate.num_workers", 2)  # Default 2 workers
        self.dynamic_batching = self.config.get("weaviate.dynamic_batching", True)
        self.timeout_retries = self.config.get("weaviate.timeout_retries", 3)
        self.connection_error_retries = self.config.get("weaviate.connection_error_retries", 3)

        # Thread lock to ensure only one batch operation at a time
        # Weaviate v3 batch is NOT thread-safe
        self._batch_lock = threading.Lock()

        logger.info(
            "WeaviateBatchInserter initialized",
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            dynamic=self.dynamic_batching,
        )

    async def batch_insert(
        self,
        data_objects: List[Dict[str, Any]],
        vectors: List[Optional[List[float]]],
        collection_names: List[str],
        unique_collections: Set[str],
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Insert objects in batch using Weaviate v3 batch API.

        This method is async but uses a sync Weaviate client internally,
        so it runs in a thread executor to avoid blocking the event loop.

        Args:
            data_objects: List of objects to insert (without vectors)
            vectors: List of vectors (can contain None for objects without embeddings)
            collection_names: Target Weaviate class name for each object.

        Returns:
            Tuple of (successful_count, list_of_errors)

        Raises:
            ExternalServiceError: If batch operation fails completely
        """
        if not data_objects:
            return 0, []

        # Validate inputs
        if len(data_objects) != len(vectors) or len(data_objects) != len(collection_names):
            raise ValueError(
                f"Mismatch between objects ({len(data_objects)}), vectors ({len(vectors)}), and collection_names ({len(collection_names)})"
            )

        logger.info(
            "Starting batch insertion",
            collections=list(unique_collections),
            object_count=len(data_objects),
        )

        # Run the sync batch operation in executor to avoid blocking
        loop = asyncio.get_event_loop()

        try:
            with self.perf_logger.measure(
                "batch_insert_weaviate",
                collections=",".join(unique_collections),
                count=len(data_objects),
            ):
                result = await loop.run_in_executor(
                    None,  # Use default ThreadPoolExecutor
                    self._sync_batch_insert,
                    data_objects,
                    vectors,
                    collection_names,
                )

            # Update metrics
            self.metrics.increment("weaviate.batch.successful", result.successful)
            self.metrics.increment("weaviate.batch.failed", result.failed)
            self.metrics.gauge("weaviate.batch.last_size", len(data_objects))

            if result.failed > 0:
                logger.warning(
                    "Batch insertion completed with errors",
                    successful=result.successful,
                    failed=result.failed,
                    error_sample=result.errors[:3],  # First 3 errors as sample
                )
            else:
                logger.info("Batch insertion completed successfully", successful=result.successful)

            return result.successful, result.errors

        except Exception as e:
            logger.error("Batch insertion failed", error=str(e), error_type=type(e).__name__)
            self.metrics.increment("weaviate.batch.total_failures")

            # Wrap in ExternalServiceError (retryable by default)
            raise ExternalServiceError(
                f"Weaviate batch insertion failed: {str(e)}",
                context={
                    "collections": list(unique_collections),
                    "object_count": len(data_objects),
                    "batch_size": self.batch_size,
                },
            )

    def _sync_batch_insert(
        self,
        data_objects: List[Dict[str, Any]],
        vectors: List[Optional[List[float]]],
        collection_names: List[str],
    ) -> BatchResult:
        """
        Synchronous batch insertion using Weaviate client.

        This method runs in a thread executor to avoid blocking asyncio.

        Args:
            data_objects: Objects to insert
            vectors: Corresponding vectors
            collection_names: Target class for each object

        Returns:
            BatchResult with counts and errors
        """
        result = BatchResult()

        # Acquire lock to ensure thread safety
        # Only one batch operation can run at a time in Weaviate v3
        with self._batch_lock:
            logger.debug("Acquired batch lock for thread-safe operation")

            # Use a callback to collect errors from the batch operation
            batch_errors = []

            def record_error_callback(errors: List[Dict[str, Any]]):
                """Callback to append errors from the batch operation."""
                nonlocal batch_errors
                batch_errors.extend(errors)
                for error in errors:
                    logger.warning(
                        "Weaviate batch error reported",
                        message=error.get("message"),
                        object_index=error.get("original_index"),
                        weaviate_error=error.get("error"),
                    )

            try:
                with self.client.batch(
                    batch_size=self.batch_size,
                    num_workers=self.num_workers,
                    dynamic=self.dynamic_batching,
                    timeout_retries=self.timeout_retries,
                    connection_error_retries=self.connection_error_retries,
                    callback=record_error_callback,
                ) as batch:
                    # Add each object to the batch
                    for i, (data_object, vector, collection_name) in enumerate(
                        zip(data_objects, vectors, collection_names)
                    ):
                        try:
                            # Weaviate batch API handles both cases
                            if vector is not None:
                                batch.add_data_object(
                                    data_object=data_object,
                                    class_name=collection_name,
                                    vector=vector,
                                )
                            else:
                                # Without vector - Weaviate may generate if configured
                                batch.add_data_object(
                                    data_object=data_object, class_name=collection_name
                                )
                        except Exception as e:
                            # This catches errors *before* adding to the batch (e.g., validation)
                            # The callback will catch errors *during* insertion.
                            error_info = {
                                "original_index": i,
                                "message": f"Failed to add object to batch: {str(e)}",
                                "error": {"type": type(e).__name__, "details": str(e)},
                                "file_path": data_object.get("file_path", "unknown"),
                                "collection": collection_name,
                            }
                            batch_errors.append(error_info)
                            logger.debug(
                                "Failed to add object to batch queue",
                                index=i,
                                collection=collection_name,
                                error=str(e),
                            )

                # After the `with` block, the batch is flushed and the callback has been called.
                # Now, we process the results collected by the callback.
                result.errors = batch_errors
                result.failed = len(batch_errors)
                result.successful = len(data_objects) - result.failed

                if result.failed > 0:
                    logger.warning(
                        "Batch insertion finished with errors",
                        successful=result.successful,
                        failed=result.failed,
                    )
            except Exception as context_exc:
                # This catches errors if the batch context manager itself fails
                logger.error(
                    "Weaviate batch context manager failed",
                    error=str(context_exc),
                    error_type=type(context_exc).__name__,
                )
                # All objects in the batch are considered failed
                result.failed = len(data_objects)
                result.successful = 0
                result.errors.append(
                    {
                        "batch_flush_error": str(context_exc),
                        "error_type": type(context_exc).__name__,
                        "message": "Batch context manager failed unexpectedly.",
                    }
                )

        return result

    # Note: Weaviate v3 batch API doesn't use callbacks in the same way as v4
    # Results are tracked internally by the batch context manager
    # Errors are caught when adding objects to the batch

    def validate_objects(
        self, data_objects: List[Dict[str, Any]], class_name: str = "CodeChunk"
    ) -> List[str]:
        """
        Validate objects before batch insertion.

        Args:
            data_objects: Objects to validate
            class_name: Target class name

        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []

        # Get expected properties from schema
        try:
            schema = self.client.schema.get(class_name)
            if not schema:
                errors.append(f"Class {class_name} not found in schema")
                return errors

            # Extract property names
            expected_props = {prop["name"] for prop in schema.get("properties", [])}

        except Exception as e:
            errors.append(f"Failed to get schema: {str(e)}")
            return errors

        # Validate each object
        for i, obj in enumerate(data_objects):
            obj_errors = []

            # Check for unexpected properties
            for key in obj.keys():
                if key not in expected_props and key not in ["id", "_additional"]:
                    obj_errors.append(f"Unexpected property: {key}")

            # Check for required properties (basic validation)
            if class_name == "CodeChunk":
                required = ["content", "file_path", "chunk_type"]
                for prop in required:
                    if prop not in obj:
                        obj_errors.append(f"Missing required property: {prop}")

            if obj_errors:
                errors.append(f"Object {i}: {', '.join(obj_errors)}")

        return errors
