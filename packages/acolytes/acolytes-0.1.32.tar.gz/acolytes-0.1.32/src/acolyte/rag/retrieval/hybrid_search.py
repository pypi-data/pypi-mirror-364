"""
Hybrid search implementation combining semantic (70%) and lexical (30%) search.

This module implements the CRITICAL hybrid search that is the heart of the RAG system.
ConversationService and other modules DEPEND on this implementation.
"""

from typing import Dict, List, Optional, Any, TYPE_CHECKING
from dataclasses import dataclass, field

from acolyte.core.logging import logger
from acolyte.core.secure_config import get_settings
from acolyte.core.token_counter import SmartTokenCounter
from acolyte.models.chunk import Chunk, ChunkType, ChunkMetadata
from acolyte.models.common.metadata import GitMetadata
from acolyte.rag.compression import ContextualCompressor
from acolyte.rag.retrieval.fuzzy_matcher import get_fuzzy_matcher
from acolyte.rag.retrieval.cache import SearchCache

# Use TYPE_CHECKING for imports that are only for type hints
if TYPE_CHECKING:
    from acolyte.api.openai import EditorContext

# Define ALL possible properties across collections to retrieve them all
ALL_CHUNK_PROPERTIES = [
    "content",
    "file_path",
    "language",
    "chunk_type",
    "chunk_name",
    "start_line",
    "end_line",
    "summary",
    "last_modified",
    "git_metadata",
    "document_type",
    "title",
    "config_format",
    "key_path",
    "value",
]


@dataclass
class ScoredChunk:
    """Chunk with relevance score."""

    chunk: Chunk
    score: float
    source: str = ""  # 'semantic', 'lexical', or 'hybrid'


@dataclass
class SearchFilters:
    """Optional filters for search."""

    file_path: Optional[str] = None
    file_types: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    chunk_types: Optional[List[str]] = None
    excluded_file_paths: List[str] = field(default_factory=list)  # Nueva propiedad para exclusiones


class HybridSearch:
    """
    Implements hybrid search 70/30 for code retrieval.

    This is the ONLY search implementation in ACOLYTE.
    Other modules must use this class, not reimplement.
    """

    def __init__(
        self,
        weaviate_client,
        lexical_index=None,  # TBD: Actual lexical search implementation
        semantic_weight: float = 0.7,
        lexical_weight: float = 0.3,
        enable_compression: bool = True,
    ):
        """
        Initialize hybrid search.

        Args:
            weaviate_client: Weaviate client for semantic search
            lexical_index: Lexical search implementation (TBD)
            semantic_weight: Weight for semantic results (default 0.7)
            lexical_weight: Weight for lexical results (default 0.3)
            enable_compression: Enable contextual compression
        """
        self.weaviate_client = weaviate_client
        self.lexical_index = lexical_index
        self.semantic_weight = semantic_weight
        self.lexical_weight = lexical_weight

        # Ensure weights sum to 1.0
        total_weight = semantic_weight + lexical_weight
        if abs(total_weight - 1.0) > 0.001:
            logger.warning("Weights don't sum to 1.0, normalizing", total_weight=total_weight)
            self.semantic_weight = semantic_weight / total_weight
            self.lexical_weight = lexical_weight / total_weight

        # Initialize compression if enabled
        self.enable_compression = enable_compression
        if enable_compression:
            self.token_counter = SmartTokenCounter()
            self.compressor = ContextualCompressor(token_counter=self.token_counter)
        else:
            self.compressor = None

        # Initialize proper LRU cache with TTL
        config = get_settings()
        self.cache = SearchCache(
            max_size=config.get("cache.max_size", 1000), ttl=config.get("cache.ttl_seconds", 3600)
        )

        logger.info(
            "HybridSearch initialized",
            semantic_weight=self.semantic_weight,
            lexical_weight=self.lexical_weight,
            compression="enabled" if enable_compression else "disabled",
        )

    async def search(
        self,
        query: str,
        max_chunks: int = 10,
        filters: Optional[SearchFilters] = None,
        collection_names: Optional[List[str]] = None,
        editor_context: Optional['EditorContext'] = None,
    ) -> List[ScoredChunk]:
        """
        Perform hybrid search without compression.

        Args:
            query: Search query text
            max_chunks: Maximum number of results
            filters: Optional search filters
            collection_names: Optional list of collections to search in. Defaults to all chunk collections.
            editor_context: Optional context from the editor (file paths, selections, etc.)

        Returns:
            List of chunks sorted by hybrid score
        """
        # Default to all chunk collections if not specified
        if not collection_names:
            from acolyte.rag.collections.collection_names import (
                CODE_CHUNK,
                DOC_CHUNK,
                CONFIG_CHUNK,
                TEST_CHUNK,
            )

            collection_names = [CODE_CHUNK, DOC_CHUNK, CONFIG_CHUNK, TEST_CHUNK]

        # Convert filters to dict for cache key
        filters_dict = filters.__dict__ if filters else None

        # Try to get from cache first
        cached_chunks = self.cache.get(query, filters_dict, collection_names)
        if cached_chunks is not None:
            # Convert cached Chunks back to ScoredChunks
            # Since we don't store scores, mark them as cached with score 1.0
            cached_results = [
                ScoredChunk(chunk=chunk, score=1.0, source="cached")
                for chunk in cached_chunks[:max_chunks]
            ]
            logger.debug("Cache hit for query", query=query[:50], collections=collection_names)
            return cached_results

        # Use editor context aware search if available
        if editor_context and editor_context.current_file_path:
            logger.debug(
                "Using editor context aware search",
                current_file=editor_context.current_file_path,
                open_tabs_count=len(editor_context.open_tabs) if editor_context.open_tabs else 0,
                has_selection=editor_context.selection is not None,
            )

            # Use editor-aware search
            final_results = await self._search_with_editor_context(
                query, max_chunks, filters, collection_names, editor_context
            )
        else:
            # Get more results than needed for better combination
            search_limit = max_chunks * 2

            # Perform both searches in parallel - pass collection_names
            semantic_results = await self._semantic_search(
                query, search_limit, filters, collection_names
            )
            lexical_results = await self._lexical_search(
                query, search_limit, filters, collection_names
            )

            # Combine results with weights
            combined_results = self._combine_results(semantic_results, lexical_results)

            # Sort by final score and return top results
            combined_results.sort(key=lambda x: x.score, reverse=True)
            final_results = combined_results[:max_chunks]

        # Cache the chunks (not the scores)
        chunks_to_cache = [
            r.chunk for r in final_results[: max_chunks * 2]
        ]  # Cache more for flexibility
        self.cache.set(query, chunks_to_cache, filters_dict, collection_names)

        logger.debug(
            "Search completed",
            query=query[:50],
            collections=collection_names,
            editor_aware=editor_context is not None,
            returned=len(final_results),
        )

        return final_results

    async def search_with_compression(
        self,
        query: str,
        max_chunks: int = 10,
        token_budget: Optional[int] = None,
        compression_ratio: Optional[float] = None,
        filters: Optional[SearchFilters] = None,
        collection_names: Optional[List[str]] = None,
        editor_context: Optional['EditorContext'] = None,
    ) -> List[Chunk]:
        """
        Perform hybrid search with query-specific compression.

        Args:
            query: Search query text
            max_chunks: Maximum number of chunks to return
            token_budget: Optional token budget to fit results within
            compression_ratio: Optional target compression ratio
            filters: Optional search filters
            collection_names: Optional list of collections to search in
            editor_context: Optional context from the editor (file paths, selections, etc.)

        Returns:
            List of compressed chunks
        """
        if not self.compressor:
            raise ValueError("Cannot use compression - compressor not initialized")

        # If token_budget not specified, use default
        if token_budget is None:
            token_budget = self.token_counter.count_tokens(query) * 10

        # Create cache key for compressed results
        # Note: We cache the compressed results separately with budget info
        cache_key = f"compressed:{query}:{max_chunks}:{token_budget}"
        filters_dict = filters.__dict__ if filters else None

        # Try cache first
        cached_compressed = self.cache.get(cache_key, filters_dict, collection_names)
        if cached_compressed is not None:
            logger.debug(
                "Cache hit for compressed query", query=query[:50], collections=collection_names
            )
            return cached_compressed[:max_chunks]

        # Perform regular hybrid search first to get scored results
        scored_results = await self.search(
            query, max_chunks * 2, filters, collection_names, editor_context
        )

        # Extract chunks from scored results
        chunks = [result.chunk for result in scored_results]

        # Decide if compression is needed
        if not self.compressor.should_compress(query, chunks, token_budget):
            # Not worth compressing, return first max_chunks
            uncompressed_results = chunks[:max_chunks]
            # Cache even uncompressed results
            self.cache.set(cache_key, uncompressed_results, filters_dict, collection_names)
            return uncompressed_results

        # Compress intelligently
        compressed_chunks, compression_result = self.compressor.compress_chunks(
            chunks=chunks, query=query, token_budget=token_budget
        )

        # Cache compressed results
        self.cache.set(cache_key, compressed_chunks, filters_dict, collection_names)

        # Log compression metrics
        logger.info(
            "Compression applied",
            query_type=compression_result.query_type,
            tokens_saved=compression_result.tokens_saved,
            compression_ratio=compression_result.compression_ratio,
        )

        return compressed_chunks

    async def _semantic_search(
        self,
        query: str,
        limit: int,
        filters: Optional[SearchFilters] = None,
        collection_names: Optional[List[str]] = None,
    ) -> List[ScoredChunk]:
        """
        Perform semantic search using embeddings.

        Uses query embedding to find similar chunks in vector space.
        """
        if not collection_names:
            logger.warning(
                "Semantic search called without collection names, falling back to CodeChunk."
            )
            collection_names = ["CodeChunk"]

        try:
            # Get query embedding from embeddings service
            from acolyte.embeddings import get_embeddings

            embedder = get_embeddings()

            # encode() is NOT async, it's a regular method
            query_embedding = embedder.encode(query)

            # Convert to Weaviate format (float64)
            query_vector = query_embedding.to_weaviate()

            logger.info(
                "[DEBUG] Query vector generated",
                vector_length=len(query_vector),
                vector_type=type(query_vector),
                first_values=query_vector[:5] if len(query_vector) >= 5 else query_vector,
            )

            # Build Weaviate query
            query_builder = (
                self.weaviate_client.query.get(
                    collection_names,
                    ALL_CHUNK_PROPERTIES,
                )
                .with_near_vector(
                    {
                        "vector": query_vector,
                        "certainty": 0.75,
                    }  # Balanced threshold for good precision/recall
                )
                .with_limit(limit)
                .with_additional(["certainty", "id", "vector"])  # Get score, ID, and vector
            )

            # Apply filters if provided
            if filters:
                where_conditions = []

                if filters.file_path:
                    where_conditions.append(
                        {
                            "path": ["file_path"],
                            "operator": "Equal",
                            "valueString": filters.file_path,
                        }
                    )

                if filters.chunk_types:
                    # Weaviate doesn't support "In" operator, use "Or" with multiple "Equal"
                    chunk_types_upper = [ct.upper() for ct in filters.chunk_types]
                    if len(chunk_types_upper) == 1:
                        where_conditions.append(
                            {
                                "path": ["chunk_type"],
                                "operator": "Equal",
                                "valueString": chunk_types_upper[0],
                            }
                        )
                    else:
                        # Multiple chunk types: use "Or" with multiple "Equal"
                        or_conditions = []
                        for chunk_type in chunk_types_upper:
                            or_conditions.append(
                                {
                                    "path": ["chunk_type"],
                                    "operator": "Equal",
                                    "valueString": chunk_type,
                                }
                            )
                        where_conditions.append({"operator": "Or", "operands": or_conditions})

                if filters.file_types:
                    # Weaviate doesn't support "In" operator, use "Or" with multiple "Equal"
                    if len(filters.file_types) == 1:
                        where_conditions.append(
                            {
                                "path": ["language"],
                                "operator": "Equal",
                                "valueString": filters.file_types[0],
                            }
                        )
                    else:
                        # Multiple file types: use "Or" with multiple "Equal"
                        or_conditions = []
                        for file_type in filters.file_types:
                            or_conditions.append(
                                {
                                    "path": ["language"],
                                    "operator": "Equal",
                                    "valueString": file_type,
                                }
                            )
                        where_conditions.append({"operator": "Or", "operands": or_conditions})

                if filters.excluded_file_paths:
                    # Weaviate doesn't support "Not" operator, use "And" with "Not"
                    not_conditions = []
                    for excluded_path in filters.excluded_file_paths:
                        not_conditions.append(
                            {
                                "path": ["file_path"],
                                "operator": "NotEqual",
                                "valueString": excluded_path,
                            }
                        )
                    if not_conditions:
                        where_conditions.append({"operator": "And", "operands": not_conditions})

                if where_conditions:
                    if len(where_conditions) > 1:
                        logger.info("[TRACE] Multiple where conditions in semantic search")
                        where_clause = {"operator": "And", "operands": where_conditions}
                    else:
                        where_clause = where_conditions[0]
                    query_builder = query_builder.with_where(where_clause)

            # Execute search
            results = query_builder.do()

            logger.info(
                "[DEBUG] Weaviate search executed",
                results_type=type(results),
                has_data="data" in results if results else False,
            )

            # Convert to ScoredChunks
            scored_chunks = []

            # Verify response structure
            if not results or "data" not in results or "Get" not in results["data"]:
                logger.warning("No data from semantic search", query=query[:50])
                return []

            # Process results from all collections
            for collection_name, items in results["data"]["Get"].items():
                if not items:
                    continue

                logger.info(
                    "Semantic search raw results",
                    query=query[:50],
                    collection=collection_name,
                    raw_results_count=len(items),
                    threshold=0.3,
                )

                for item in items:
                    # Create Chunk object from result, now with all properties
                    metadata = self._reconstruct_metadata(item, collection_name)
                    chunk = Chunk(content=item.get("content", ""), metadata=metadata)

                    # Extract similarity score
                    score = item.get("_additional", {}).get("certainty", 0.0)

                    scored_chunks.append(ScoredChunk(chunk=chunk, score=score, source="semantic"))

            logger.info(
                "Semantic search completed",
                query=query[:50],
                limit=limit,
                results=len(scored_chunks),
                avg_score=sum(sc.score for sc in scored_chunks) / max(1, len(scored_chunks)),
            )

            return scored_chunks

        except ImportError as e:
            logger.info("[TRACE] Failed to import embeddings service")
            logger.error("Failed to import embeddings service", error=str(e))
            return []
        except Exception as e:
            logger.info("[TRACE] Semantic search failed with exception")
            logger.error("Semantic search failed", error=str(e))
            return []

    async def _lexical_search(
        self,
        query: str,
        limit: int,
        filters: Optional[SearchFilters] = None,
        collection_names: Optional[List[str]] = None,
    ) -> List[ScoredChunk]:
        """
        Perform lexical search for exact term matches.

        Uses Weaviate BM25 search with fuzzy query expansion to find chunks
        containing query terms regardless of naming convention.
        """
        if not collection_names:
            logger.warning(
                "Lexical search called without collection names, falling back to CodeChunk."
            )
            collection_names = ["CodeChunk"]

        try:
            logger.info("Starting lexical search", query=query[:50], limit=limit)

            # Ensure limit is an integer
            limit = int(limit)

            # Skip lexical search for empty queries - BM25 doesn't handle them well
            if not query or not query.strip():
                logger.debug("Skipping lexical search for empty query")
                return []

            # Expand query with fuzzy variations
            fuzzy_matcher = get_fuzzy_matcher()
            query_variations = fuzzy_matcher.expand_query(query)

            logger.info(
                "Lexical search variations generated",
                original_query=query[:50],
                variations=query_variations,
                variations_count=len(query_variations),
            )

            # Ensure we have at least one variation
            if not query_variations:
                logger.warning("No query variations generated", query=query)
                return []

            # Collect all results from variations
            all_scored_chunks = []

            for i, variation in enumerate(query_variations):
                # Reduce weight for variations (original gets full weight)
                variation_weight = 1.0 if i == 0 else 0.8

                # Calculate limit for this variation
                variation_limit = max(1, int(limit // len(query_variations) + 1))
                logger.debug(
                    "Lexical search variation",
                    variation=variation,
                    limit=limit,
                    limit_type=type(limit),
                    query_variations_count=len(query_variations),
                    calculated_limit=variation_limit,
                    calculated_limit_type=type(variation_limit),
                )

                # Use Weaviate BM25 search
                query_builder = (
                    self.weaviate_client.query.get(
                        collection_names,
                        ALL_CHUNK_PROPERTIES,
                    )
                    .with_bm25(
                        query=variation,
                        properties=[
                            "content",
                            "file_path",
                            "chunk_name",
                            "title",
                            "key_path",
                        ],  # Search in these relevant text fields
                    )
                    .with_limit(variation_limit)  # Use pre-calculated limit
                    .with_additional(["score", "id"])  # Get BM25 score and ID
                )

                # Apply filters if provided
                if filters:
                    where_conditions = []

                    if filters.file_path:
                        where_conditions.append(
                            {
                                "path": ["file_path"],
                                "operator": "Equal",
                                "valueString": filters.file_path,
                            }
                        )

                    if filters.chunk_types:
                        # Weaviate doesn't support "In" operator, use "Or" with multiple "Equal"
                        chunk_types_upper = [ct.upper() for ct in filters.chunk_types]
                        if len(chunk_types_upper) == 1:
                            where_conditions.append(
                                {
                                    "path": ["chunk_type"],
                                    "operator": "Equal",
                                    "valueString": chunk_types_upper[0],
                                }
                            )
                        else:
                            # Multiple chunk types: use "Or" with multiple "Equal"
                            or_conditions = []
                            for chunk_type in chunk_types_upper:
                                or_conditions.append(
                                    {
                                        "path": ["chunk_type"],
                                        "operator": "Equal",
                                        "valueString": chunk_type,
                                    }
                                )
                            where_conditions.append({"operator": "Or", "operands": or_conditions})

                    if filters.file_types:
                        # Weaviate doesn't support "In" operator, use "Or" with multiple "Equal"
                        if len(filters.file_types) == 1:
                            where_conditions.append(
                                {
                                    "path": ["language"],
                                    "operator": "Equal",
                                    "valueString": filters.file_types[0],
                                }
                            )
                        else:
                            # Multiple file types: use "Or" with multiple "Equal"
                            or_conditions = []
                            for file_type in filters.file_types:
                                or_conditions.append(
                                    {
                                        "path": ["language"],
                                        "operator": "Equal",
                                        "valueString": file_type,
                                    }
                                )
                            where_conditions.append({"operator": "Or", "operands": or_conditions})

                    if filters.excluded_file_paths:
                        # Weaviate doesn't support "Not" operator, use "And" with "Not"
                        not_conditions = []
                        for excluded_path in filters.excluded_file_paths:
                            not_conditions.append(
                                {
                                    "path": ["file_path"],
                                    "operator": "NotEqual",
                                    "valueString": excluded_path,
                                }
                            )
                        if not_conditions:
                            where_conditions.append({"operator": "And", "operands": not_conditions})

                    if where_conditions:
                        if len(where_conditions) > 1:
                            logger.info("[TRACE] Multiple where conditions in lexical search")
                            where_clause = {"operator": "And", "operands": where_conditions}
                        else:
                            where_clause = where_conditions[0]
                        query_builder = query_builder.with_where(where_clause)

                # Execute search
                results = query_builder.do()

                # Handle None response from Weaviate
                if results is None:
                    logger.warning("Weaviate returned None for lexical search", query=variation)
                    continue

                # Process results for this variation
                if not results.get("data", {}).get("Get"):
                    continue

                for collection_name, items in results["data"]["Get"].items():
                    if not items:
                        continue

                    for item in items:
                        # Create Chunk object from result
                        metadata = self._reconstruct_metadata(item, collection_name)
                        chunk = Chunk(content=item.get("content", ""), metadata=metadata)

                        # Extract BM25 score and apply variation weight
                        base_score = item.get("_additional", {}).get("score", 0.0)

                        # Ensure base_score is a number (Weaviate might return a list/tuple)
                        if isinstance(base_score, (list, tuple)):
                            base_score = base_score[0] if base_score else 0.0
                        elif not isinstance(base_score, (int, float)):
                            base_score = 0.0

                        weighted_score = base_score * variation_weight

                        all_scored_chunks.append(
                            ScoredChunk(chunk=chunk, score=weighted_score, source="lexical")
                        )

            # Deduplicate results based on chunk ID
            seen_chunks = {}
            for scored_chunk in all_scored_chunks:
                chunk_id = scored_chunk.chunk.id
                if chunk_id not in seen_chunks or scored_chunk.score > seen_chunks[chunk_id].score:
                    seen_chunks[chunk_id] = scored_chunk

            # Get unique results and sort by score
            unique_chunks = list(seen_chunks.values())
            unique_chunks.sort(key=lambda x: x.score, reverse=True)

            # Return top results up to limit
            final_results = unique_chunks[:limit]

            logger.info(
                "Lexical search completed",
                query=query[:50],
                variations=len(query_variations),
                limit=limit,
                results=len(final_results),
                avg_score=sum(sc.score for sc in final_results) / max(1, len(final_results)),
            )

            return final_results

        except Exception as e:
            logger.info("[TRACE] Lexical search failed with exception")
            logger.error("Lexical search failed", error=str(e))
            # Fallback to empty results on error
            return []

    def _combine_results(
        self, semantic_results: List[ScoredChunk], lexical_results: List[ScoredChunk]
    ) -> List[ScoredChunk]:
        """
        Combine semantic and lexical results with 70/30 weights.

        Handles deduplication and re-scoring when chunks appear in both.
        """
        # Normalize scores to [0, 1] range
        semantic_normalized = self._normalize_scores(semantic_results)
        lexical_normalized = self._normalize_scores(lexical_results)

        # Create dictionaries for efficient lookup
        semantic_dict = {r.chunk.id: r for r in semantic_normalized}
        lexical_dict = {r.chunk.id: r for r in lexical_normalized}

        # Combine results
        combined_dict: Dict[str, ScoredChunk] = {}

        # Process semantic results
        for chunk_id, result in semantic_dict.items():
            if chunk_id in lexical_dict:
                # Chunk appears in both - combine scores
                semantic_score = result.score * self.semantic_weight
                lexical_score = lexical_dict[chunk_id].score * self.lexical_weight
                combined_score = semantic_score + lexical_score

                combined_dict[chunk_id] = ScoredChunk(
                    chunk=result.chunk, score=combined_score, source="hybrid"
                )
            else:
                # Only in semantic
                combined_dict[chunk_id] = ScoredChunk(
                    chunk=result.chunk, score=result.score * self.semantic_weight, source="semantic"
                )

        # Process lexical-only results
        for chunk_id, result in lexical_dict.items():
            if chunk_id not in semantic_dict:
                combined_dict[chunk_id] = ScoredChunk(
                    chunk=result.chunk, score=result.score * self.lexical_weight, source="lexical"
                )

        return list(combined_dict.values())

    def _normalize_scores(self, results: List[ScoredChunk]) -> List[ScoredChunk]:
        """Normalize scores to [0, 1] range."""
        if not results:
            return results

        scores = [r.score for r in results]
        max_score = max(scores)
        min_score = min(scores)

        # If all scores are the same
        if max_score == min_score:
            return [ScoredChunk(chunk=r.chunk, score=1.0, source=r.source) for r in results]

        # Normalize to [0, 1]
        normalized = []
        for result in results:
            normalized_score = (result.score - min_score) / (max_score - min_score)
            normalized.append(
                ScoredChunk(chunk=result.chunk, score=normalized_score, source=result.source)
            )

        return normalized

    def _reconstruct_metadata(self, item: Dict[str, Any], collection_name: str) -> ChunkMetadata:
        """
        Reconstructs ChunkMetadata from a Weaviate result item,
        handling collection-specific properties.
        """
        # Common properties
        metadata = ChunkMetadata(
            file_path=item.get("file_path", ""),
            language=item.get("language", "unknown"),
            start_line=item.get("start_line", 1),
            end_line=item.get("end_line", 1),
            chunk_type=ChunkType(item.get("chunk_type", "UNKNOWN")),
            name=item.get("chunk_name") or item.get("title") or item.get("key_path"),
            last_modified=item.get("last_modified"),
        )

        # Collection-specific properties
        if collection_name == "DocChunk":
            metadata.document_type = item.get("document_type")
            # The 'name' field is already populated with 'title' as a fallback
        elif collection_name == "ConfigChunk":
            metadata.config_format = item.get("config_format")
            metadata.key_path = item.get("key_path")
            metadata.value = item.get("value")
            # chunk_type for config can be MODULE or CONSTANTS
            metadata.chunk_type = ChunkType(item.get("chunk_type", "MODULE"))
        elif collection_name == "TestChunk":
            # TestChunk has the same schema as CodeChunk, no special handling needed
            pass

        # Add git metadata if present
        git_metadata_dict = item.get("git_metadata")
        if git_metadata_dict and isinstance(git_metadata_dict, dict):
            metadata.git_metadata = GitMetadata(**git_metadata_dict)

        return metadata

    def invalidate_cache(self, pattern: Optional[str] = None):
        """
        Invalidate cache entries.

        Args:
            pattern: Optional pattern to match. If None or "*", invalidates all.
                    Otherwise, invalidates entries matching the pattern.
        """
        self.cache.invalidate_by_pattern(pattern or "*")
        logger.info("Invalidated cache entries", pattern=(pattern or "all"))

    def invalidate_cache_for_file(self, file_path: str):
        """
        Invalidate cache entries for a specific file.

        This is more precise than pattern-based invalidation.

        Args:
            file_path: Path of the modified file
        """
        self.cache.invalidate_by_file(file_path)
        logger.info("Invalidated cache entries for file", file_path=file_path)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring.

        Returns:
            Dict with cache statistics including size, hit rate, etc.
        """
        return self.cache.get_stats()

    async def search_with_graph_expansion(
        self,
        query: str,
        max_results: int = 10,
        expansion_depth: int = 2,
        filters: Optional[SearchFilters] = None,
        collection_names: Optional[List[str]] = None,
        graph: Any = None,  # Nuevo parámetro opcional
    ) -> List[Chunk]:
        """
        Hybrid search with neural graph expansion.

        THIS REPLACES search_with_clustering().

        Args:
            query: Search query
            max_results: Maximum results to return
            expansion_depth: Expansion depth in graph (default: 2 hops)
            filters: Optional filters
            collection_names: Optional list of collections to search in.
            graph: Optional pre-created neural graph instance to use

        Returns:
            Expanded and re-ranked chunks
        """
        # 1. Initial search to get "seeds"
        initial_results = await self.search(query, max_results // 3, filters, collection_names)

        if not initial_results:
            return []

        # 2. Expand via neural graph
        if graph is None:  # Usar el grafo proporcionado o crear uno nuevo
            from acolyte.rag.graph.neural_graph import NeuralGraph

            graph = NeuralGraph()

        expanded_chunks = []
        seen_paths = set()

        for scored_chunk in initial_results[:5]:  # Top 5 as seeds
            chunk = scored_chunk.chunk
            file_path = chunk.metadata.file_path

            # Find related files
            related_nodes = await graph.find_related(
                node=file_path, max_distance=expansion_depth, min_strength=0.3
            )

            # Load chunks from related files
            for node in related_nodes:
                if node['path'] not in seen_paths:
                    seen_paths.add(node['path'])
                    file_chunks = await self._load_chunks_from_file(node['path'], collection_names)
                    expanded_chunks.extend(file_chunks)

        # 3. Combine original results + expanded
        all_chunks = [r.chunk for r in initial_results] + expanded_chunks

        # 4. Re-rank all by relevance to query
        reranked = await self._rerank_by_relevance(query, all_chunks, max_results)

        logger.info(
            "Graph expansion results",
            seeds=len(initial_results),
            total_chunks=len(all_chunks),
            final_results=len(reranked),
        )

        return reranked

    async def _load_chunks_from_file(
        self, file_path: str, collection_names: Optional[List[str]] = None
    ) -> List[Chunk]:
        """
        Load all chunks from a specific file from Weaviate.

        Args:
            file_path: Path of the file to load chunks from
            collection_names: Optional list of collections to search in.

        Returns:
            List of chunks from the file
        """
        logger.info("[TRACE] _load_chunks_from_file method called")
        try:
            # Default to all chunk collections if not specified
            if not collection_names:
                from acolyte.rag.collections.collection_names import (
                    CODE_CHUNK,
                    DOC_CHUNK,
                    CONFIG_CHUNK,
                    TEST_CHUNK,
                )

                collection_names = [CODE_CHUNK, DOC_CHUNK, CONFIG_CHUNK, TEST_CHUNK]

            # Query Weaviate for all chunks from this file
            query_builder = (
                self.weaviate_client.query.get(
                    collection_names,
                    ALL_CHUNK_PROPERTIES,
                )
                .with_where({"path": ["file_path"], "operator": "Equal", "valueString": file_path})
                .with_limit(100)  # Reasonable limit per file
            )

            # Execute query
            results = query_builder.do()

            # Convert results to chunks
            chunks = []
            if results and results.get("data", {}).get("Get"):
                for collection_name, items in results["data"]["Get"].items():
                    if not items:
                        continue

                    for item in items:
                        # Reconstruct metadata intelligently
                        metadata = self._reconstruct_metadata(item, collection_name)
                        chunk = Chunk(content=item.get("content", ""), metadata=metadata)
                        chunks.append(chunk)

            logger.debug("Loaded chunks from file", file_path=file_path, chunks=len(chunks))
            return chunks

        except Exception as e:
            logger.error("Failed to load chunks from file", file_path=file_path, error=str(e))
            return []

    async def _rerank_by_relevance(
        self, query: str, chunks: List[Chunk], max_results: int
    ) -> List[Chunk]:
        """
        Re-rank chunks by relevance to query using embeddings.

        Args:
            query: User query
            chunks: Chunks to re-rank
            max_results: Maximum number of results to return

        Returns:
            Top max_results chunks ordered by relevance
        """
        try:
            # Get embeddings service
            from acolyte.embeddings import get_embeddings

            embedder = get_embeddings()

            # Get query embedding
            query_embedding = embedder.encode(query)

            # Score each chunk
            scored_chunks = []
            for chunk in chunks:
                # Get chunk embedding
                chunk_text = chunk.to_search_text()
                chunk_embedding = embedder.encode(chunk_text)

                # Calculate similarity
                similarity = query_embedding.cosine_similarity(chunk_embedding)

                scored_chunks.append(ScoredChunk(chunk=chunk, score=similarity, source="reranked"))

            # Sort by score and return top results
            scored_chunks.sort(key=lambda x: x.score, reverse=True)

            # Return just the chunks (not ScoredChunk)
            return [sc.chunk for sc in scored_chunks[:max_results]]

        except Exception as e:
            logger.info("[TRACE] Failed to re-rank chunks")
            logger.error("Failed to re-rank chunks", error=str(e))
            # Fallback: return original chunks truncated
            return chunks[:max_results]

    async def _search_with_editor_context(
        self,
        query: str,
        max_chunks: int,
        filters: Optional[SearchFilters],
        collection_names: Optional[List[str]],
        editor_context: 'EditorContext',
    ) -> List[ScoredChunk]:
        """
        Perform a search prioritizing files from the editor context.

        Args:
            query: Search query text
            max_chunks: Maximum number of results
            filters: Optional search filters
            collection_names: Optional list of collections
            editor_context: Editor context with current file, open tabs, etc.

        Returns:
            List of chunks sorted and prioritized based on editor context
        """
        # Extract current file path
        current_file = editor_context.current_file_path

        # NUEVA IMPLEMENTACIÓN: Intentar búsqueda basada en grafo primero
        if current_file is not None:
            try:
                # Importar aquí para evitar dependencias circulares
                import asyncio
                from acolyte.rag.graph.neural_graph import NeuralGraph

                # Crear una instancia del grafo neural
                graph = NeuralGraph()

                logger.info(
                    "Attempting graph-based search for editor context",
                    current_file=current_file,
                    query=query[:50],
                )

                # Usar timeout para garantizar responsividad
                graph_chunks = await asyncio.wait_for(
                    self.search_with_graph_expansion(
                        query=query,
                        max_results=max_chunks,
                        expansion_depth=2,  # Profundidad razonable
                        filters=SearchFilters(file_path=current_file),
                        graph=graph,  # Pasar la instancia creada
                    ),
                    timeout=0.5,  # 500ms es un timeout razonable
                )

                # Si tenemos resultados del grafo, convertirlos a ScoredChunks con boost
                if graph_chunks and len(graph_chunks) > 0:
                    logger.info(
                        "Graph-based search successful",
                        chunks_found=len(graph_chunks),
                        current_file=current_file,
                    )

                    # Convertir a ScoredChunk con boost alto (son muy relevantes)
                    graph_results = [
                        ScoredChunk(
                            chunk=chunk,
                            score=0.95,  # Score muy alto para resultados de grafo
                            source="graph",
                        )
                        for chunk in graph_chunks
                    ]

                    return graph_results[:max_chunks]

            except asyncio.TimeoutError:
                logger.warning(
                    "Graph-based search timed out, falling back to standard search", timeout_ms=500
                )
            except Exception as e:
                logger.warning(
                    "Graph-based search failed, falling back to standard search",
                    error=str(e),
                    error_type=type(e).__name__,
                )

        # BÚSQUEDA ESTÁNDAR (FALLBACK): Si llegamos aquí, la búsqueda basada en grafo
        # falló o no estaba disponible, continuamos con la implementación original
        # 1. Búsqueda específica en el archivo actual (40% de los chunks)
        current_file_limit = max(1, int(max_chunks * 0.4))
        current_file_filters = SearchFilters(
            file_path=current_file,
            file_types=filters.file_types if filters else None,
            date_from=filters.date_from if filters else None,
            date_to=filters.date_to if filters else None,
            chunk_types=filters.chunk_types if filters else None,
        )

        # Buscar en el archivo actual
        current_file_results = await self._perform_hybrid_search(
            query, current_file_limit, current_file_filters, collection_names
        )

        # 2. Búsqueda en archivos abiertos (30% de los chunks)
        open_tabs_limit = max(1, int(max_chunks * 0.3))
        open_tabs_results = []

        if editor_context.open_tabs:
            # Excluir el archivo actual de los open_tabs para evitar duplicados
            open_tabs = [tab for tab in editor_context.open_tabs if tab != current_file]

            if open_tabs:
                # Crear filtros para los archivos abiertos (usando OR de múltiples file_paths)
                # Como no podemos hacer OR directamente con SearchFilters, hacemos búsquedas individuales
                # y combinamos los resultados
                all_open_tabs_results = []

                for tab in open_tabs[:5]:  # Limitar a 5 tabs para evitar sobrecarga
                    tab_filters = SearchFilters(
                        file_path=tab,
                        file_types=filters.file_types if filters else None,
                        date_from=filters.date_from if filters else None,
                        date_to=filters.date_to if filters else None,
                        chunk_types=filters.chunk_types if filters else None,
                    )

                    tab_results = await self._perform_hybrid_search(
                        query, open_tabs_limit, tab_filters, collection_names
                    )
                    all_open_tabs_results.extend(tab_results)

                # Normalizar, ordenar y limitar
                all_open_tabs_results = self._normalize_scores(all_open_tabs_results)
                all_open_tabs_results.sort(key=lambda x: x.score, reverse=True)
                open_tabs_results = all_open_tabs_results[:open_tabs_limit]

        # 3. Búsqueda general para el resto (30% de los chunks)
        general_limit = max_chunks - len(current_file_results) - len(open_tabs_results)

        # Si hay resultados suficientes de las búsquedas anteriores, no necesitamos búsqueda general
        general_results = []
        if general_limit > 0:
            # Excluir archivos ya cubiertos
            excluded_files: List[str] = []
            if current_file is not None:
                excluded_files.append(current_file)
            if editor_context.open_tabs:
                for tab in editor_context.open_tabs:
                    if tab is not None:
                        excluded_files.append(tab)

            # Eliminar duplicados
            excluded_files = list(set(excluded_files))

            general_filters = SearchFilters(
                file_types=filters.file_types if filters else None,
                date_from=filters.date_from if filters else None,
                date_to=filters.date_to if filters else None,
                chunk_types=filters.chunk_types if filters else None,
                excluded_file_paths=excluded_files,
            )

            general_results = await self._perform_hybrid_search(
                query, general_limit, general_filters, collection_names
            )

        # 4. Combinar resultados con boost
        # Boost del archivo actual
        boosted_current_file = [
            ScoredChunk(
                chunk=r.chunk,
                score=min(1.0, r.score * 1.5),  # 50% boost
                source=f"{r.source}_current_file",
            )
            for r in current_file_results
        ]

        # Boost de archivos abiertos
        boosted_open_tabs = [
            ScoredChunk(
                chunk=r.chunk,
                score=min(1.0, r.score * 1.2),  # 20% boost
                source=f"{r.source}_open_tabs",
            )
            for r in open_tabs_results
        ]

        # Combinar todos los resultados
        all_results = boosted_current_file + boosted_open_tabs + general_results

        # Eliminar duplicados por chunk_id, manteniendo el score más alto
        unique_results = {}
        for result in all_results:
            chunk_id = result.chunk.id
            if chunk_id not in unique_results or result.score > unique_results[chunk_id].score:
                unique_results[chunk_id] = result

        combined_results = list(unique_results.values())

        # Ordenar por score y limitar a max_chunks
        combined_results.sort(key=lambda x: x.score, reverse=True)
        return combined_results[:max_chunks]

    async def _perform_hybrid_search(
        self,
        query: str,
        limit: int,
        filters: Optional[SearchFilters],
        collection_names: Optional[List[str]],
    ) -> List[ScoredChunk]:
        """Realiza búsqueda híbrida estándar."""
        # Obtener el doble para mejor combinación
        search_limit = limit * 2

        # Búsquedas paralelas
        semantic_results = await self._semantic_search(
            query, search_limit, filters, collection_names
        )
        lexical_results = await self._lexical_search(query, search_limit, filters, collection_names)

        # Combinar con pesos 70/30
        combined = self._combine_results(semantic_results, lexical_results)

        # Ordenar y limitar
        combined.sort(key=lambda x: x.score, reverse=True)
        return combined[:limit]

    async def _perform_hybrid_search_excluding_files(
        self,
        query: str,
        limit: int,
        filters: Optional[SearchFilters],
        collections: Optional[List[str]],
        excluded_files: List[str],
    ) -> List[ScoredChunk]:
        """Búsqueda híbrida excluyendo archivos específicos."""
        # Crear nuevo filtro o modificar existente
        if filters:
            modified_filters = SearchFilters(**filters.__dict__)
        else:
            modified_filters = SearchFilters()

        # Añadir exclusión (necesitaría implementar en SearchFilters)
        modified_filters.excluded_file_paths = excluded_files

        return await self._perform_hybrid_search(query, limit, modified_filters, collections)
