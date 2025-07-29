"""
Chat Service - MAIN ORCHESTRATOR.

Coordinates the entire chat flow by integrating all components.
"""

import os
import asyncio
from acolyte.core.logging import logger
from acolyte.core.tracing import MetricsCollector
from acolyte.core.token_counter import TokenBudgetManager, SmartTokenCounter
from acolyte.core.ollama import OllamaClient
from acolyte.core.exceptions import AcolyteError, ExternalServiceError
from acolyte.core.secure_config import get_settings
from acolyte.core.id_generator import generate_id
from acolyte.core.utils.retry import retry_async
from acolyte.semantic import (
    Summarizer,
    TaskDetector,
    QueryAnalyzer,
    DecisionDetector,
)
from acolyte.semantic.utils import detect_language
from acolyte.rag.retrieval.hybrid_search import HybridSearch, SearchFilters
from acolyte.rag.compression import ContextualCompressor  # Decision #14
from acolyte.models.task_checkpoint import TaskCheckpoint, TaskType
from acolyte.models.technical_decision import TechnicalDecision, DecisionType
from acolyte.services.conversation_service import ConversationService
from acolyte.services.task_service import TaskService
from acolyte.services.git_service import GitService
from acolyte.dream.orchestrator import DreamTrigger
from acolyte.core.languages import get_prompt_labels

# Lazy import dream to avoid loading heavy modules
# from acolyte.dream import create_dream_orchestrator
# from acolyte.dream.orchestrator import DreamTrigger
from typing import Dict, Any, Optional, cast, List, Union, AsyncIterator
from acolyte.core.utils.datetime_utils import utc_now, parse_iso_datetime
from datetime import timedelta


class ChatService:
    """
    Orchestrates the entire chat flow.

    CRITICAL FLOW:
    1. Loads previous context automatically (Decision #7)
    2. Analyzes query with Semantic
    3. Searches with hybrid RAG
    4. Generates with Ollama
    5. Resumes with Semantic
    6. Persists with Services
    7. Detects decisions
    """

    def __init__(
        self,
        context_size: int,
        conversation_service=None,
        task_service=None,
        debug_mode: bool = False,
    ):
        """
        Initializes ChatService with optional dependency injection.

        Args:
            context_size: Size of the model context
            conversation_service: ConversationService instance (optional)
            task_service: TaskService instance (optional)
            debug_mode: Whether to include debug information in responses
        """
        self.metrics = MetricsCollector()
        self.token_manager = TokenBudgetManager(context_size)
        self.token_counter = SmartTokenCounter()  # Para conteo preciso
        self.ollama = OllamaClient()
        self.config = get_settings()
        self.debug_mode = debug_mode

        # Initialize Weaviate client for RAG and Dream
        try:
            import weaviate  # type: ignore

            # Check environment variable first (for Docker)
            weaviate_url = os.getenv("WEAVIATE_URL")
            if weaviate_url:
                self.weaviate_client = weaviate.Client(weaviate_url)
            else:
                # Fallback to config file
                weaviate_port = self.config.get("ports.weaviate", 42080)
                weaviate_url = f"http://localhost:{weaviate_port}"
                self.weaviate_client = weaviate.Client(weaviate_url)

            if not self.weaviate_client.is_ready():
                logger.warning("Weaviate not ready")
                self.weaviate_client = None
        except Exception as e:
            logger.warning("Weaviate not available", error=str(e))
            self.weaviate_client = None

        # Semantic components
        self.query_analyzer = QueryAnalyzer()
        self.task_detector = TaskDetector()
        self.summarizer = Summarizer()
        self.decision_detector = DecisionDetector()

        # Services - use injected or create new ones
        if conversation_service is None:
            self.conversation_service = ConversationService()
        else:
            self.conversation_service = conversation_service

        if task_service is None:
            self.task_service = TaskService()
        else:
            self.task_service = task_service

        # RAG
        try:
            if self.weaviate_client:
                self.hybrid_search = HybridSearch(weaviate_client=self.weaviate_client)
                self.compressor = ContextualCompressor(self.token_counter)  # For specific queries
            else:
                logger.warning("RAG components not available - Weaviate client missing")
                self.hybrid_search = None
                self.compressor = None
        except Exception as e:
            logger.warning("RAG components not available", error=str(e))
            self.hybrid_search = None
            self.compressor = None

        # Active session cache (mono-user)
        self._active_session_id: Optional[str] = None
        self._active_task: Optional[TaskCheckpoint] = None
        self._last_user_message: Optional[str] = None
        self.git_service: Optional[GitService] = None

        # Dream system integration
        self._dream_orchestrator = None  # Lazy load

        logger.info("ChatService initialized", context_size=context_size, debug_mode=debug_mode)

    @property
    def dream_orchestrator(self):
        """Lazy load dream orchestrator to avoid importing heavy modules."""
        if self._dream_orchestrator is None and self.weaviate_client:
            try:
                from acolyte.dream import create_dream_orchestrator

                self._dream_orchestrator = create_dream_orchestrator(
                    weaviate_client=self.weaviate_client
                )
            except Exception as e:
                logger.warning("Dream system not available", error=str(e))
                self._dream_orchestrator = None  # Mark as attempted
        return self._dream_orchestrator

    @dream_orchestrator.setter
    def dream_orchestrator(self, value):
        """Setter for dream_orchestrator to allow mocking in tests."""
        self._dream_orchestrator = value

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        debug: Optional[bool] = None,
        stream: bool = False,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], AsyncIterator[str]]:
        """
        Processes a complete message.

        DETAILED FLOW:
        1. If no session_id, detects if it's a new chat
        2. Analyzes intent for token distribution
        3. Detects if it's a new task or continuation
        4. Searches for relevant code with RAG
        5. Generates response with Ollama (prompt built in _generate_with_retry)
        6. Generates summary WITH chunks for context
        7. Detects technical decisions
        8. Persists everything
        9. Checks Dream fatigue and suggests if needed

        Args:
            message: User message
            session_id: Session ID (optional, created if not exists)
            debug: Override debug mode (optional)
            stream: Whether to stream the response (optional)
            request_metadata: Additional metadata from the request (optional)

        Returns:
            If stream=False: Dict with response, session_id, task_id, tokens_used, processing_time
            If stream=True: AsyncIterator[str] that yields response chunks

            If debug=True, includes additional debug_info

        Raises:
            AcolyteError: General system error
            ExternalServiceError: If Ollama or external services fail
            DatabaseError: If persistence fails
        """
        start_time = utc_now()

        # Override debug mode if specified
        include_debug = debug if debug is not None else self.debug_mode

        # Store last user message for Dream analysis check
        self._last_user_message = message

        try:
            # STEP 1: Session management
            if not session_id:
                session_id = await self._handle_new_chat()

            self._active_session_id = session_id

            # STEP 2: Query analysis
            # IMPORTANT: TokenDistribution is an object, use .type for string
            distribution = self.query_analyzer.analyze_query_intent(message)
            self.token_manager.allocate_for_query_type(distribution.type)  # ← .type

            logger.info(
                "Query analysis complete",
                query_type=distribution.type,
                response_ratio=distribution.response_ratio,
            )

            # STEP 3: Task detection
            task_detection = await self.task_detector.detect_task_context(
                message, self._active_task
            )

            # If new task is detected, create it
            if task_detection.is_new_task and task_detection.task_title:
                await self.task_service.create_task(
                    title=task_detection.task_title,
                    description=message,
                    task_type=self._infer_task_type(message),
                    initial_session_id=(
                        session_id
                        if session_id
                        else await self.conversation_service.create_session("New conversation")
                    ),
                )

                # Load the newly created task
                self._active_task = await self.task_service.find_active_task()
                logger.info("Created new task", title=task_detection.task_title)

            elif task_detection.continues_task and self._active_task:
                # Associate current session to existing task
                if session_id:
                    await self.task_service.associate_session_to_task(
                        self._active_task.id, session_id
                    )

            # STEP 4: RAG search
            chunks = []
            logger.info(
                "Starting RAG search", hybrid_search_available=self.hybrid_search is not None
            )
            if self.hybrid_search:
                try:
                    logger.info(
                        "Executing RAG search", query_type=distribution.type, query=message[:50]
                    )

                    # Create search filters for code-related queries
                    search_filters: Optional[SearchFilters] = None

                    # Extraer información del editor del request_metadata si existe
                    editor_context = None
                    if request_metadata and 'editor_context' in request_metadata:
                        editor_context = request_metadata.get('editor_context')
                        # Log para debugging
                        logger.info(
                            "Editor context received",
                            has_selection=bool(editor_context and 'selection' in editor_context),
                            current_file=(
                                editor_context.get('current_file_path') if editor_context else None
                            ),
                        )

                    # Combinar filtros básicos y contexto del editor
                    if self._is_code_related_query(message):
                        # Simple filter: if asking about Python, filter by Python
                        if "python" in message.lower():
                            search_filters = SearchFilters(file_types=["python"])
                            logger.info("Using Python filter for Python-specific query")

                        # Si hay un archivo actual en el contexto del editor, priorizarlo
                        if editor_context and editor_context.get('current_file_path'):
                            current_file = editor_context.get('current_file_path')
                            logger.info(f"Prioritizing current file in editor: {current_file}")
                            # Si ya hay search_filters, modificarlos; si no, crearlos
                            if not search_filters:
                                search_filters = SearchFilters()
                            search_filters.file_path = current_file

                    # NUEVO: Ajustar chunks según historial (Opción A - Reducción Dinámica)
                    has_conversation_history = (
                        hasattr(self, '_current_conversation_history')
                        and self._current_conversation_history
                        and len(self._current_conversation_history) > 1
                    )

                    max_chunks = 3 if has_conversation_history else 10  # ← CAMBIO CLAVE

                    logger.info(
                        "Executing RAG search",
                        query_type=distribution.type,
                        query=message[:50],
                        max_chunks=max_chunks,
                        has_history=has_conversation_history,
                        editor_context_available=editor_context is not None,
                    )

                    # If query is specific, use compression
                    if distribution.type in ["simple", "generation"] and self.compressor:
                        available_tokens = self.token_manager.get_remaining("rag")
                        logger.info("Using compressed search", available_tokens=available_tokens)
                        chunks = await self.hybrid_search.search_with_compression(
                            query=message,
                            max_chunks=max_chunks,  # ← Usar max_chunks dinámico
                            token_budget=available_tokens,
                            filters=search_filters,
                            editor_context=editor_context,  # Pasar el contexto del editor
                        )
                        self.metrics.increment("chat.compressed_searches")
                    else:
                        logger.info(
                            "Using normal search", max_chunks=max_chunks, filters=search_filters
                        )
                        chunks = await self.hybrid_search.search(
                            query=message,
                            max_chunks=max_chunks,
                            filters=search_filters,
                            editor_context=editor_context,  # Pasar el contexto del editor
                        )
                        # Convert ScoredChunk to Chunk
                        chunks = [scored_chunk.chunk for scored_chunk in chunks]

                    logger.info("RAG search completed", chunks_found=len(chunks))
                    self.metrics.gauge("chat.chunks_retrieved", len(chunks))

                except Exception as e:
                    logger.error("RAG search failed", error=str(e))
                    chunks = []
            else:
                logger.warning("RAG search skipped - hybrid_search not available")

            # STEP 5: Generate response WITH RETRY

            response_tokens = self.token_manager.get_remaining("response")

            # Ahora el método soporta streaming (stream=True/False)
            response_or_iterator = await self._generate_with_retry(
                user_message=message,
                context_chunks=chunks,
                max_tokens=response_tokens,
                stream=stream,  # Pasar el parámetro stream
            )

            # Manejar los casos de streaming y no-streaming
            if stream:
                # En modo streaming, envolvemos el iterador con post-procesamiento
                if session_id:
                    return self._stream_and_post_process(
                        stream_iterator=cast(AsyncIterator[str], response_or_iterator),
                        user_message=message,
                        session_id=session_id,
                        context_chunks=chunks,
                        task_id=self._active_task.id if self._active_task else None,
                    )
                else:
                    # Este caso no debería ocurrir, pero por seguridad devolvemos el iterador directamente
                    logger.warning("Streaming without session_id, skipping post-processing")
                    return cast(AsyncIterator[str], response_or_iterator)
            else:
                # NO-STREAMING: código existente
                # Garantizar que es un string
                response = cast(str, response_or_iterator)

                # Count tokens used with SmartTokenCounter
                tokens_used = self.token_counter.count_tokens(response)
                self.token_manager.use("response", tokens_used)

                # STEP 6-8: Post-procesamiento
                if session_id:
                    # Crear variable para usar después en debug_info
                    summary_result = await self.summarizer.generate_summary(
                        user_msg=message,
                        assistant_msg=response,
                        context_chunks=chunks,
                    )

                    await self._post_process_response(
                        user_message=message,
                        assistant_response=response,
                        session_id=session_id,
                        context_chunks=chunks,
                        task_id=self._active_task.id if self._active_task else None,
                        tokens_used=tokens_used,
                        summary_result=summary_result,
                    )
                else:
                    logger.warning("No session_id for post-processing")
                    # Crear variable para usar después en debug_info
                    summary_result = None

                # Calculate metrics
                processing_time = (utc_now() - start_time).total_seconds()
                self.metrics.record("chat.processing_time_seconds", processing_time)
                self.metrics.increment("chat.messages_processed")

                # Build response
                result = {
                    "response": response,
                    "session_id": session_id,
                    "task_id": self._active_task.id if self._active_task else None,
                    "tokens_used": {
                        "prompt": self.token_manager.used.get("system", 0),
                        "context": self.token_manager.used.get("rag", 0),
                        "response": tokens_used,
                        "total": sum(self.token_manager.used.values()),
                    },
                    "processing_time": processing_time,
                }

                # Add debug info if requested
                if include_debug:
                    # BUGFIX: The method is get_distribution(), not get_total_used()
                    distribution_map = self.token_manager.get_distribution()
                    # Sum tokens from all categories and subcategories
                    tokens_used = sum(distribution_map["used"].values())
                    processing_time = (utc_now() - start_time).total_seconds()
                    debug_info = {
                        "session_id": session_id,
                        "query_type": distribution.type,
                        "task_detected": task_detection.is_new_task,
                        "task_title": task_detection.task_title,
                        "chunks_retrieved": len(chunks),
                        "prompt": {
                            "user": message,
                        },
                        "timing": {
                            "total_processing_seconds": round(processing_time, 2),
                        },
                        "tokens": self.token_manager.get_distribution(),
                    }

                    # Añadir compresión de resumen solo si tenemos un resumen
                    if summary_result:
                        debug_info["summary_compression"] = summary_result.tokens_saved / max(
                            1, tokens_used
                        )

                    result["debug_info"] = debug_info

                # STEP 9: Check Dream fatigue and suggest if needed
                if not include_debug and self.dream_orchestrator:
                    dream_suggestion = await self._check_dream_suggestion()
                    if dream_suggestion:
                        result["suggestion"] = dream_suggestion

                return result

        except Exception as e:
            logger.error("Error processing message", error=str(e))
            self.metrics.increment("chat.processing_errors")
            raise AcolyteError(f"Failed to process message: {str(e)}") from e

    async def _post_process_response(
        self,
        user_message: str,
        assistant_response: str,
        session_id: str,
        context_chunks: List,
        task_id: Optional[str],
        tokens_used: int,
        summary_result=None,
    ):
        """Ejecuta todas las tareas posteriores a la generación de la respuesta."""
        logger.info("Starting post-processing for response.", session_id=session_id)

        # Verificación de session_id válido
        if not session_id:
            logger.error("Cannot post-process response: session_id is required")
            return

        try:
            # PASO 6: Generar resumen CON CHUNKS si no lo recibimos ya
            if not summary_result:
                summary_result = await self.summarizer.generate_summary(
                    user_msg=user_message,
                    assistant_msg=assistant_response,
                    context_chunks=context_chunks,
                )

            # PASO 7: Detectar decisiones
            detected_decision = self.decision_detector.detect_technical_decision(assistant_response)

            # PASO 8: Persistir
            await self.conversation_service.save_conversation_turn(
                session_id=session_id,
                user_message=user_message,
                assistant_response=assistant_response,
                summary=summary_result.summary,
                tokens_used=tokens_used,
                task_id=task_id,
            )

            if detected_decision and task_id:
                # Convert DetectedDecision to complete TechnicalDecision
                technical_decision = TechnicalDecision(
                    id=generate_id(),
                    created_at=utc_now(),
                    decision_type=DecisionType(detected_decision.decision_type),
                    title=detected_decision.title,
                    description=detected_decision.description,
                    rationale=detected_decision.rationale,
                    alternatives_considered=detected_decision.alternatives_considered,
                    impact_level=detected_decision.impact_level,
                    session_id=session_id,
                    task_id=task_id,
                )

                await self.task_service.save_technical_decision(technical_decision)

                logger.info(
                    "Technical decision saved",
                    type=detected_decision.decision_type,
                    impact=detected_decision.impact_level,
                )
        except Exception as e:
            # Capturar errores durante el post-procesamiento para no interrumpir
            # el flujo principal si estamos en modo streaming
            logger.error("Error during post-processing", error=str(e), session_id=session_id)
            # No relanzar la excepción, ya que esto es un proceso asíncrono en segundo plano

    async def _stream_and_post_process(
        self,
        stream_iterator: AsyncIterator[str],
        user_message: str,
        session_id: str,
        context_chunks: List,
        task_id: Optional[str],
    ) -> AsyncIterator[str]:
        """Hace yield de los chunks y llama al post-procesamiento al final."""
        full_response_parts = []
        try:
            async for chunk in stream_iterator:
                full_response_parts.append(chunk)
                yield chunk
        except Exception as e:
            # Capturar errores durante el streaming pero no interrumpir
            logger.error(
                "Error during streaming response generation", error=str(e), session_id=session_id
            )
            # No reenviar la excepción para mantener la conexión
        finally:  # Asegurar que el post-procesamiento se ejecute incluso si hay error
            if full_response_parts:
                full_response = "".join(full_response_parts)
                tokens_used = self.token_counter.count_tokens(full_response)

                # Verificar que la sesión existe
                if session_id:
                    # Usar create_task para no bloquear
                    asyncio.create_task(
                        self._post_process_response(
                            user_message=user_message,
                            assistant_response=full_response,
                            session_id=session_id,
                            context_chunks=context_chunks,
                            task_id=task_id,
                            tokens_used=tokens_used,
                        )
                    )
                else:
                    logger.warning(
                        "Cannot perform post-processing without valid session_id",
                        response_length=len(full_response),
                    )

    async def _handle_new_chat(self) -> str:
        """Handles the logic for starting a new chat session."""
        self._active_task = await self.task_service.find_active_task()

        # If there's an active task with an initial session, verify it exists
        if self._active_task and self._active_task.initial_session_id:
            # Verify the session actually exists in the database
            try:
                await self.conversation_service.get_session_context(
                    self._active_task.initial_session_id, include_related=False
                )
                logger.info(
                    "Continuing with active task",
                    task_title=self._active_task.title,
                )
                return self._active_task.initial_session_id
            except Exception as e:
                logger.warning(
                    "Task's initial session not found, creating new session",
                    session_id=self._active_task.initial_session_id,
                    error=str(e),
                )

        # If there's no active task, try to load the last session as context
        last_session = await self.conversation_service.get_last_session()
        if last_session:
            # Verify it exists before using it
            try:
                await self.conversation_service.get_session_context(
                    last_session["session_id"], include_related=False
                )
                logger.info("Continuing from last session", session_id=last_session["session_id"])
                return last_session["session_id"]
            except Exception as e:
                logger.warning(
                    "Last session not found, creating new session",
                    session_id=last_session["session_id"],
                    error=str(e),
                )

        # Otherwise, create a new session
        logger.info("Starting new conversation")
        new_session_id = await self.conversation_service.create_session("New conversation")
        return new_session_id

    def _infer_task_type(self, message: str) -> TaskType:
        """
        Infers the task type based on the message.

        Args:
            message: User message

        Returns:
            Inferred TaskType (default: RESEARCH)
        """
        message_lower = message.lower()

        # Check in order of specificity
        if any(kw in message_lower for kw in ["error", "bug", "fix", "arreglar", "problema"]):
            return TaskType.DEBUGGING
        if any(kw in message_lower for kw in ["refactor", "mejorar", "optimizar", "clean"]):
            return TaskType.REFACTORING
        if any(kw in message_lower for kw in ["document", "explicar", "readme", "docs"]):
            return TaskType.DOCUMENTATION
        if any(kw in message_lower for kw in ["review", "revisar", "check", "validar"]):
            return TaskType.REVIEW
        if any(
            kw in message_lower
            for kw in ["research", "investigar", "analizar", "explorar", "study"]
        ):
            return TaskType.RESEARCH
        if any(
            kw in message_lower
            for kw in ["implement", "crear", "añadir", "develop", "build", "feature"]
        ):
            return TaskType.IMPLEMENTATION

        # Default for generic queries
        return TaskType.RESEARCH

    async def process_message_with_history(
        self,
        messages: List[Dict[str, str]],
        current_message: str,
        session_id: Optional[str] = None,
        debug: Optional[bool] = None,
        stream: bool = False,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], AsyncIterator[str]]:
        """
        Processes a message with full conversation history using existing sliding window.

        Note:
            This method temporarily stores the provided message history in the
            instance variable `_current_conversation_history`. This variable is used
            by the internal `_generate_with_retry` method and is cleared in a `finally`
            block to ensure it does not persist beyond the scope of this call.

        Args:
            messages: Full conversation history [{role, content}, ...]
            current_message: The current user message to process
            session_id: Session ID (optional)
            debug: Override debug mode (optional)
            stream: Whether to stream the response (optional)
            request_metadata: Additional metadata from the request (optional)

        Returns:
            Same as process_message
        """
        # Get configuration for context window size
        max_messages = self.config.get("conversation.context_window_messages", 20)

        # Limit history to prevent token overflow
        limited_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        # Store the conversation history for use in generation
        self._current_conversation_history = limited_messages

        # Log memory usage for debugging
        logger.info(
            "Processing message with conversation history",
            total_messages=len(messages),
            limited_messages=len(limited_messages),
            max_window_size=max_messages,
            current_message_preview=(
                current_message[:50] + "..." if len(current_message) > 50 else current_message
            ),
        )

        try:
            # Call the original process_message with the current message
            # y pasar el parámetro stream
            result = await self.process_message(
                message=current_message,
                session_id=session_id,
                debug=debug,
                stream=stream,
                request_metadata=request_metadata,
            )

            # Add memory metrics to debug info if available
            if debug and isinstance(result, dict) and "debug_info" in result:
                result["debug_info"]["memory"] = {
                    "total_messages": len(messages),
                    "window_messages": len(limited_messages),
                    "window_size": max_messages,
                }

            return result

        finally:
            # Clear the temporary history
            self._current_conversation_history = None

    async def _generate_with_retry(
        self,
        user_message: str,
        context_chunks: list,
        max_tokens: int,
        stream: bool = False,
        max_attempts: int = 3,
    ) -> Union[str, AsyncIterator[str]]:
        """
        Generates response with Ollama using retry logic.

        IMPLEMENTS: is_retryable() for robustness.

        Args:
            user_message: User message
            context_chunks: Chunks of code for context
            max_tokens: Response token limit
            stream: Whether to stream the response
            max_attempts: Maximum number of attempts

        Returns:
            If stream=False: Response generated by Ollama as string
            If stream=True: AsyncIterator[str] that yields response chunks

        Raises:
            ExternalServiceError: If all attempts fail
        """
        # Track attempts for metrics
        attempt_count = 0

        # Custom exception to signal non-retryable errors
        class NonRetryableError(Exception):
            def __init__(self, original_error: Exception):
                self.original_error = original_error
                super().__init__(str(original_error))

        # Create wrapper that preserves is_retryable() logic
        async def retryable_ollama_operation():
            nonlocal attempt_count
            attempt_count += 1

            # Track retry attempts after the first one
            if attempt_count > 1:
                self.metrics.increment("chat.ollama_retries_attempted")
                logger.info(
                    "Retrying Ollama generation",
                    attempt=attempt_count,
                    max_attempts=max_attempts,
                    streaming=stream,
                )

            try:
                # Get conversation history if available (using existing sliding window)
                conversation_history = getattr(self, '_current_conversation_history', None)

                # Detect language and get appropriate labels
                lang = detect_language(user_message)
                labels = get_prompt_labels(lang)

                prompt_parts = []

                # Include conversation history FIRST (to establish context)
                if conversation_history and len(conversation_history) > 1:
                    # Add explicit instruction to use conversation history
                    prompt_parts.append("Historial de conversación:")
                    prompt_parts.append("")

                    # Add conversation history header
                    history_header = labels.get('conversation_history', 'Conversation History')
                    prompt_parts.append(f"{history_header}:")

                    # Include previous messages (excluding the current one)
                    for msg in conversation_history[:-1]:  # All except last
                        role_label = labels.get(msg['role'], msg['role'].capitalize())
                        prompt_parts.append(f"{role_label}: {msg['content']}")

                    prompt_parts.append("")  # Empty line separator

                # Add current user message AFTER history (to maintain AI identity)
                prompt_parts.append(f"{labels['user']}: {user_message}")

                # Add RAG context if available
                if context_chunks:
                    prompt_parts.append(f"\n{labels['context_header']}")

                    for i, chunk in enumerate(context_chunks[:5], 1):
                        # Format each chunk with clear metadata
                        prompt_parts.append(
                            f"\n### {labels['context_item'].format(i=i, file=chunk.metadata.file_path)}"
                        )

                        # Get localized label for chunk type (normalize to lowercase for lookup)
                        chunk_type_key = chunk.metadata.chunk_type.lower()
                        chunk_type_label = labels.get(chunk_type_key, chunk.metadata.chunk_type)
                        prompt_parts.append(f"{labels['type']}: {chunk_type_label}")

                        # Add line numbers if available
                        if hasattr(chunk.metadata, 'start_line') and chunk.metadata.start_line:
                            prompt_parts.append(
                                f"{labels['lines']}: {chunk.metadata.start_line}-{chunk.metadata.end_line}"
                            )

                        # Determine language for syntax highlighting
                        language = getattr(chunk.metadata, 'language', 'python')
                        prompt_parts.append(f"```{language}")

                        # Include chunk content (limited)
                        chunk_content = chunk.content[:500]
                        if len(chunk.content) > 500:
                            chunk_content += f"\n# {labels['content_truncated']}"
                        prompt_parts.append(chunk_content)
                        prompt_parts.append("```")

                full_prompt = "\n".join(prompt_parts)

                # Add detailed logging for memory debugging
                logger.info(
                    "About to call Ollama generate",
                    prompt_size=len(full_prompt),
                    max_tokens=max_tokens,
                    attempt=attempt_count,
                    has_conversation_history=conversation_history is not None,
                    history_length=len(conversation_history) if conversation_history else 0,
                    stream=stream,
                )

                # Llamar a Ollama con el parámetro stream
                return await self.ollama.generate(
                    prompt=full_prompt,
                    max_tokens=max_tokens,
                    stream=stream,
                )

            except (AcolyteError, ExternalServiceError) as e:
                # Check if the error is retryable
                if hasattr(e, 'is_retryable') and not e.is_retryable():
                    logger.error("Ollama generation failed permanently", error=str(e))
                    # Wrap in NonRetryableError to stop retries
                    raise NonRetryableError(e)
                # Re-raise to trigger retry
                raise
            except Exception as e:
                # Convert uncontrolled errors to ExternalServiceError (retryable by default)
                raise ExternalServiceError(f"Ollama error: {str(e)}", cause=e)

        # Para streaming, implementamos un manejo básico de reintentos
        if stream:
            max_streaming_attempts = 2  # Limitado para streaming por naturaleza del iterador
            current_attempt = 0

            # Clase interna para el stream de errores
            class ErrorStreamIterator:
                def __init__(self, error_message):
                    self.error_message = error_message
                    self.done = False

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    if self.done:
                        raise StopAsyncIteration
                    self.done = True
                    return self.error_message

            while current_attempt < max_streaming_attempts:
                current_attempt += 1
                try:
                    # Intentamos obtener un iterador streaming
                    response_iterator = await retryable_ollama_operation()

                    # Si llegamos aquí, el iterador se obtuvo correctamente
                    if current_attempt > 1:
                        logger.info("Streaming retry succeeded", attempts=current_attempt)

                    # Verificar que response_iterator sea realmente un AsyncIterator
                    if not hasattr(response_iterator, "__aiter__"):
                        logger.error(
                            "Invalid response from Ollama: not an AsyncIterator",
                            response_type=type(response_iterator).__name__,
                        )
                        return ErrorStreamIterator("Error interno: respuesta inválida del modelo")

                    # Wrapping iterator into a proper AsyncIterator
                    class ResilientStreamIterator:
                        def __init__(self, original_stream):
                            self.original_stream = original_stream
                            self.error_returned = False

                        def __aiter__(self):
                            return self

                        async def __anext__(self):
                            try:
                                # Si es un iterador, usamos anext directamente
                                if hasattr(self.original_stream, "__anext__"):
                                    return await self.original_stream.__anext__()

                                # Si es un AsyncIterator pero accedemos por __aiter__
                                if hasattr(self.original_stream, "__aiter__"):
                                    # Solo inicializamos una vez
                                    if not hasattr(self, "_iterator"):
                                        self._iterator = self.original_stream.__aiter__()
                                    return await self._iterator.__anext__()

                                # No debería ocurrir porque verificamos arriba
                                raise StopAsyncIteration
                            except StopAsyncIteration:
                                raise
                            except Exception as e:
                                if self.error_returned:
                                    raise StopAsyncIteration
                                self.error_returned = True
                                logger.error(
                                    "Error during streaming iteration",
                                    error=str(e),
                                    error_type=type(e).__name__,
                                )
                                return f"\n\nLo siento, ocurrió un error durante la generación de la respuesta: {str(e)}"

                    # Devolver nuestro wrapper alrededor del iterador
                    return ResilientStreamIterator(response_iterator)

                except NonRetryableError as e:
                    # Error no recuperable, relanzar el original
                    logger.error(
                        "Non-retryable streaming error",
                        error=str(e.original_error),
                        error_type=type(e.original_error).__name__,
                    )
                    raise e.original_error
                except Exception as e:
                    # Error potencialmente recuperable
                    if current_attempt < max_streaming_attempts:
                        logger.warning(
                            "Streaming error, retrying",
                            error=str(e),
                            attempt=current_attempt,
                            max_attempts=max_streaming_attempts,
                        )
                        await asyncio.sleep(0.5 * current_attempt)  # Backoff simple
                    else:
                        # Agotamos los intentos
                        logger.error(
                            "Streaming failed after all retries",
                            error=str(e),
                            attempts=current_attempt,
                        )
                        # Devolver un iterador de error
                        return ErrorStreamIterator(
                            f"Lo siento, no pude generar una respuesta después de {current_attempt} intentos. Error: {str(e)}"
                        )

            # Si llegamos aquí (no deberíamos, pero por si acaso), devolvemos un stream vacío
            return ErrorStreamIterator("Lo siento, ocurrió un error inesperado en la generación")
        else:
            # Para respuestas no-streaming, usamos retry_async como antes
            try:
                # Use retry_async with exponential backoff
                response = await retry_async(
                    retryable_ollama_operation,
                    max_attempts=max_attempts,
                    backoff="exponential",
                    initial_delay=1.0,  # 2^0 = 1s for first retry
                    retry_on=(AcolyteError, ExternalServiceError),  # NOT NonRetryableError
                    logger=logger,
                )

                # Success - handle metrics
                if attempt_count > 1:
                    logger.info("Ollama generation succeeded after retry", attempts=attempt_count)
                    self.metrics.increment("chat.ollama_retries_successful")

                return response

            except NonRetryableError as e:
                # Non-retryable error, re-raise the original
                raise e.original_error
            except Exception as e:
                # All attempts failed
                self.metrics.increment("chat.ollama_retries_exhausted")
                if isinstance(e, (AcolyteError, ExternalServiceError)):
                    raise
                # Wrap any other exception
                raise ExternalServiceError("Ollama generation failed after all retries") from e

    async def _get_project_info(self) -> Dict[str, Any]:
        """
        Gets project info using an instance of GitService.

        NOTA: Si Git falla (común en Docker/Windows), usa valores por defecto.
        """
        info = {
            "project_name": self.config.get("project.name", "Unknown Project"),
            "current_branch": "main",  # Default value
            "recent_files": [],  # Default value
        }

        try:
            if not self.git_service:
                from pathlib import Path

                # Use ACOLYTE_PROJECT_ROOT in Docker, fallback to cwd
                project_root_str = os.getenv("ACOLYTE_PROJECT_ROOT")
                if project_root_str:
                    project_root = Path(project_root_str)
                    logger.debug(f"Using ACOLYTE_PROJECT_ROOT: {project_root}")
                else:
                    # Fallback inteligente para Docker
                    if os.path.exists("/project/.git"):
                        project_root = Path("/project")
                        logger.debug("Detected Docker environment, using /project")
                    else:
                        project_root = Path.cwd()
                        logger.debug(f"Using cwd as project root: {project_root}")

                logger.info("Initializing GitService", project_root=str(project_root))

                # Verificar que el path existe antes de crear GitService
                if not project_root.exists():
                    logger.warning(f"Project root does not exist: {project_root}")
                    return info

                self.git_service = GitService(str(project_root))

            git = self.git_service

            # Intentar obtener branch actual
            try:
                info["current_branch"] = git.repo.active_branch.name
            except Exception as e:
                logger.debug(f"Could not get current branch: {e}")
                # Mantener el valor por defecto "main"

            # Intentar obtener archivos recientes
            try:
                info["recent_files"] = git.get_most_recent_files()
            except Exception as e:
                logger.debug(f"Could not get recent files: {e}")
                # Mantener lista vacía

        except Exception as e:
            # Este es el catch general - no es crítico si falla
            logger.debug(
                "Git info not available (non-critical)", error=str(e), error_type=type(e).__name__
            )
            # Retornar info con valores por defecto

        return info

    async def _check_dream_suggestion(self) -> Optional[Dict[str, Any]]:
        """
        Checks if a dream analysis should be suggested based on fatigue.
        """
        if not self.dream_orchestrator:
            return None

        try:
            # First and foremost, do not suggest if an analysis is already running
            if await self.dream_orchestrator.is_analysis_in_progress():
                logger.info("Dream suggestion skipped: analysis already in progress.")
                return None

            fatigue_info = await self.dream_orchestrator.check_fatigue_level()
            is_high = fatigue_info.get("is_high", False)
            is_emergency = fatigue_info.get("is_emergency", False)

            # If fatigue is emergency level, suggest immediately, ignoring other checks
            if is_emergency:
                logger.info("Emergency fatigue detected, forcing dream suggestion.")
                # Fall through to request analysis
                pass
            # Otherwise, perform standard checks
            elif not is_high:
                return None
            elif not self._last_user_message or not self._is_code_related_query(
                self._last_user_message
            ):
                logger.info("Dream suggestion skipped: not a code-related query.")
                return None
            else:
                last_optimization_iso = fatigue_info.get("last_optimization")
                if last_optimization_iso:
                    last_opt_time = parse_iso_datetime(last_optimization_iso)
                    if utc_now() - last_opt_time < timedelta(hours=2):
                        logger.info("Dream suggestion skipped: recent optimization.")
                        return None

            # If all checks passed or were bypassed by emergency, request analysis
            analysis_request = await self.dream_orchestrator.request_analysis(
                trigger=DreamTrigger("FATIGUE_SUGGESTION"),
                context={
                    "session_id": self._active_session_id,
                    "task_id": self._active_task.id if self._active_task else None,
                    "fatigue_level": fatigue_info.get("fatigue_level"),
                    "is_emergency": is_emergency,
                },
            )

            # Only return a suggestion if the orchestrator requires user permission
            if analysis_request.get("status") == "permission_required":
                return {
                    "type": "dream_analysis",
                    "request_id": analysis_request["request_id"],
                    "message": analysis_request["message"],
                    "fatigue_level": fatigue_info.get("fatigue_level"),
                    "benefits": analysis_request.get("benefits"),
                    "estimated_duration": analysis_request.get("estimated_duration_minutes"),
                }

        except Exception as e:
            logger.error("Failed to check dream suggestion", error=str(e))

        return None

    def _is_code_related_query(self, message: str) -> bool:
        """
        Check if user message is related to code/implementation.

        Args:
            message: User message to check

        Returns:
            True if message seems code-related
        """
        if not message:
            return False

        # Keywords that indicate code-related queries
        code_keywords = [
            # English
            "implement",
            "code",
            "function",
            "class",
            "method",
            "bug",
            "error",
            "fix",
            "test",
            "refactor",
            "optimize",
            "debug",
            "compile",
            "build",
            "import",
            "module",
            "package",
            "api",
            "endpoint",
            "query",
            "database",
            # Spanish
            "implementar",
            "código",
            "función",
            "clase",
            "método",
            "arreglar",
            "probar",
            "optimizar",
            "depurar",
            "compilar",
            "construir",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in code_keywords)

    async def request_dream_analysis(
        self, user_query: str, focus_areas: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Requests an analysis from the Dream system.
        """
        if not self.dream_orchestrator:
            raise AcolyteError("Dream system is not available")

        # The context is important for the analysis
        context = {
            "session_id": self._active_session_id,
            "task_id": self._active_task.id if self._active_task else None,
        }

        analysis_result = await self.dream_orchestrator.request_analysis(
            trigger=DreamTrigger("USER_REQUEST"),
            user_query=user_query,
            focus_areas=focus_areas,
            context=context,
        )
        return analysis_result

    async def get_active_session_info(self) -> Dict[str, Any]:
        """
        Gets active session information.

        Useful for dashboard or status checks.

        Returns:
            Dict with session_id, task info, token_usage, debug_mode
        """
        info = {
            "session_id": self._active_session_id,
            "task": {
                "id": self._active_task.id if self._active_task else None,
                "title": self._active_task.title if self._active_task else None,
            },
            "token_usage": self.token_manager.get_distribution(),
            "debug_mode": self.debug_mode,
        }

        # Add Dream status if available
        if self.dream_orchestrator:
            try:
                fatigue_data = await self.dream_orchestrator.check_fatigue_level()
                info["dream_status"] = {
                    "fatigue_level": fatigue_data["fatigue_level"],
                    "is_high": fatigue_data["is_high"],
                    "threshold": fatigue_data["threshold"],
                    "last_optimization": fatigue_data.get("last_optimization"),
                }
            except Exception as e:
                info["dream_status"] = None
                logger.debug("Could not get Dream status", error=str(e))
        else:
            info["dream_status"] = None

        return info

    async def cleanup(self) -> None:
        """
        Clean up resources to prevent memory leaks.

        This method should be called when the service is no longer needed,
        typically during application shutdown.
        """
        logger.info("Cleaning up ChatService resources")

        # Clean up OllamaClient session
        if hasattr(self, 'ollama') and self.ollama:
            try:
                await self.ollama.close()
                logger.info("OllamaClient session closed")
            except Exception as e:
                logger.warning("Failed to close OllamaClient session", error=str(e))

        # Clean up Weaviate client if available
        if hasattr(self, 'weaviate_client') and self.weaviate_client:
            try:
                # Weaviate client doesn't have a close method, but we can clear references
                self.weaviate_client = None
                logger.info("Weaviate client reference cleared")
            except Exception as e:
                logger.warning("Failed to clear Weaviate client", error=str(e))

        # Clear other references
        self._active_session_id = None
        self._active_task = None
        self._last_user_message = None
        self.git_service = None
        self._dream_orchestrator = None

        logger.info("ChatService cleanup completed")
