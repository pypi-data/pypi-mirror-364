"""
Endpoints OpenAI-compatible - TODOS los endpoints /v1/*
Implementa: /v1/chat/completions, /v1/models, /v1/embeddings
Interfaz principal para Cursor, Continue y otras herramientas.
"""

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, cast, AsyncIterator, Dict, Any, Tuple
import time
import hashlib
import json

# Core imports
from acolyte.core.logging import logger
from acolyte.core.id_generator import generate_id
from acolyte.core.exceptions import (
    ValidationError,
    ExternalServiceError,
    from_exception,
    external_service_error,
    internal_error,
    ConfigurationError,
)

# Embeddings import
from acolyte.embeddings import get_embeddings
from acolyte.models.chunk import Chunk

router = APIRouter()
logger.info("OpenAI API initializing...", module="openai")


# ============================================================================
# MODELOS DE REQUEST/RESPONSE
# ============================================================================


class ChatMessage(BaseModel):
    """Chat message compatible with OpenAI."""

    role: str = Field(..., description="Role: system, user, assistant")
    content: str = Field(..., description="Message content")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        allowed_roles = {"system", "user", "assistant"}
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {allowed_roles}")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class EditorSelection(BaseModel):
    """Represents text selection in the editor."""

    file: str = Field(..., description="File path of the selection")
    content: str = Field(..., description="Selected text content")
    range: Tuple[int, int] = Field(..., description="Start and end line numbers")

    @field_validator("range")
    @classmethod
    def validate_range(cls, v):
        if len(v) != 2:
            raise ValueError("Range must have exactly 2 elements")
        if v[0] > v[1]:
            raise ValueError("Start line must be <= end line")
        return v


class EditorContext(BaseModel):
    """Context information from the editor."""

    selection: Optional[EditorSelection] = Field(None, description="Current text selection if any")
    current_file_path: Optional[str] = Field(None, description="Currently active file in editor")
    open_tabs: Optional[List[str]] = Field(None, description="List of open file paths")


class ChatCompletionRequest(BaseModel):
    """Request for chat completions compatible with OpenAI."""

    model: str = Field("gpt-3.5-turbo", description="Model (ignored, always uses acolyte:latest)")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for sampling")
    max_tokens: Optional[int] = Field(None, gt=0, le=32000, description="Maximum response tokens")
    stream: bool = Field(False, description="Stream response (not supported)")

    # Common OpenAI fields that we'll ignore but accept
    n: Optional[int] = Field(1, description="Number of completions (ignored)")
    presence_penalty: Optional[float] = Field(0.0, description="Presence penalty (ignored)")
    frequency_penalty: Optional[float] = Field(0.0, description="Frequency penalty (ignored)")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences (ignored)")
    top_p: Optional[float] = Field(1.0, description="Top-p sampling (ignored)")
    user: Optional[str] = Field(None, description="User ID (ignored)")

    # Campos específicos de ACOLYTE (opcionales)
    debug: bool = Field(False, description="Include debug information")
    explain_rag: bool = Field(False, description="Explain RAG search process")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")

    # Contexto del editor para mejora de RAG
    editor_context: Optional[EditorContext] = Field(
        None, description="Editor context for enhanced RAG"
    )

    class Config:
        extra = "allow"  # Allow extra fields that we don't recognize

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v):
        if not v:
            raise ValueError("At least one message is required")
        if len(v) > 100:
            raise ValueError("Too many messages (max 100)")
        return v

    @field_validator("stream")
    @classmethod
    def validate_stream(cls, v):
        # PERMITIR streaming - NO convertir a False
        return v


class EmbeddingsRequest(BaseModel):
    """Request for embeddings compatible with OpenAI."""

    input: Union[str, List[str]] = Field(..., description="Text(s) to generate embeddings")
    model: str = Field("text-embedding-ada-002", description="Model (ignored, uses UniXcoder)")
    encoding_format: str = Field("float", description="Format (only float supported)")

    @field_validator("input")
    @classmethod
    def validate_input(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Input text cannot be empty")
            if len(v) > 50000:  # Reasonable limit
                raise ValueError("Input text too long (max 50k chars)")
        elif isinstance(v, list):
            if not v:
                raise ValueError("Input list cannot be empty")
            if len(v) > 100:  # Limit for batch
                raise ValueError("Too many inputs (max 100)")
            for text in v:
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("All inputs must be non-empty strings")
        return v

    @field_validator("encoding_format")
    @classmethod
    def validate_encoding_format(cls, v):
        if v != "float":
            raise ValueError("Only 'float' encoding is supported")
        return v


# ============================================================================
# FUNCIONES DE STREAMING SSE
# ============================================================================


async def _stream_response_adapter(
    stream_iterator: AsyncIterator[str], request_model: str, request_id: str
) -> AsyncIterator[str]:
    """Adapta el stream del ChatService al formato SSE de OpenAI."""
    completion_id = f"chatcmpl-{generate_id()[:8]}"
    created_timestamp = int(time.time())
    chunk_count = 0
    start_time = time.time()
    first_chunk_time = None

    # Primer chunk con role
    first_chunk = {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created_timestamp,
        "model": request_model,
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant"},  # Importante incluir role en el primer chunk
                "finish_reason": None,
            }
        ],
    }
    yield f"data: {json.dumps(first_chunk)}\n\n"

    # Chunks de contenido
    try:
        async for chunk in stream_iterator:
            if first_chunk_time is None:
                first_chunk_time = time.time()
                logger.info(
                    "🔄 [COPILOT-STREAM] First chunk sent",
                    request_id=request_id,
                    time_to_first_chunk_ms=(first_chunk_time - start_time) * 1000,
                )

            chunk_count += 1
            chunk_data = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created_timestamp,
                "model": request_model,
                "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
    except Exception as e:
        logger.error("Streaming error", error=str(e), request_id=request_id)
        # No reenviar la excepción para mantener la conexión
    finally:
        # Enviar chunk final y señal [DONE]
        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created_timestamp,
            "model": request_model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"

        # Registrar fin del streaming
        logger.info(
            "✅ [COPILOT-STREAM] Streaming completed",
            request_id=request_id,
            total_chunks=chunk_count,
            total_duration_ms=(time.time() - start_time) * 1000,
        )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest, x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
):
    """Chat completions endpoint compatible with OpenAI.

    Uses shared services from app.state to prevent memory leaks.
    """
    # Generar o usar el request ID
    request_id = x_request_id or generate_id()
    start_time = time.time()

    # Log the incoming request for debugging
    logger.info(
        "🤖 [COPILOT-IN] Request received",
        endpoint="/v1/chat/completions",
        request_id=request_id,
        model=request.model,
        stream=request.stream,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        debug=request.debug,
        explain_rag=request.explain_rag,
        session_id=request.session_id,
        has_editor_context=request.editor_context is not None,
        user_question=request.messages[-1].content if request.messages else "NO_MESSAGE",
        messages_count=len(request.messages),
        current_file=(
            request.editor_context.current_file_path
            if request.editor_context and hasattr(request.editor_context, 'current_file_path')
            else None
        ),
    )

    # Log first few characters of each message for debugging
    for i, msg in enumerate(request.messages[:3]):  # Log first 3 messages
        logger.info(
            f"Message {i}",
            role=msg.role,
            content_preview=msg.content[:50] + "..." if len(msg.content) > 50 else msg.content,
        )

    try:
        # Use shared services from app.state (Singleton pattern)
        from acolyte.api import app

        chat_service = app.state.chat_service
        conversation_service = app.state.conversation_service

        # Extract messages for processing
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise ValidationError(
                message="At least one user message is required",
                context={"messages_count": len(request.messages)},
            )

        last_message = user_messages[-1].content

        # Convert all messages to simple format for ChatService
        conversation_history = []
        for msg in request.messages:
            conversation_history.append({"role": msg.role, "content": msg.content})

        # Search related context if there are previous messages
        related_context = []
        if len(request.messages) > 1:
            try:
                # Create request for search
                from acolyte.models.conversation import ConversationSearchRequest

                search_request = ConversationSearchRequest(
                    query=last_message,
                    limit=5,
                    include_completed=True,
                    task_id=None,
                    date_from=None,
                    date_to=None,
                )
                search_result = await conversation_service.search_conversations(search_request)
                related_context = search_result[:3]  # Top 3

                if request.debug:
                    logger.debug(
                        "Related context found",
                        sessions_count=len(related_context),
                        query_preview_hash=hashlib.sha256(last_message.encode('utf-8')).hexdigest()[
                            :12
                        ],
                    )
            except Exception as e:
                logger.warning("Context search failed", error=str(e))
                # Continue without related context

        # Preparar metadatos de la petición (editor_context)
        request_metadata = None
        if request.editor_context is not None:
            try:
                # Usar dict() solo si sabemos que el objeto lo soporta
                if hasattr(request.editor_context, "dict"):
                    request_metadata = {'editor_context': request.editor_context.dict()}
                # Fallback para objetos sin método dict()
                else:
                    request_metadata = {
                        'editor_context': {
                            'current_file_path': getattr(
                                request.editor_context, 'current_file_path', None
                            ),
                            'open_tabs': getattr(request.editor_context, 'open_tabs', None),
                        }
                    }
                # Evitar posible error con len() sobre None
                open_tabs = request_metadata['editor_context'].get('open_tabs')
                open_tabs_count = len(open_tabs) if open_tabs is not None else 0

                logger.info(
                    "🔍 [COPILOT-CONTEXT] Editor context extracted",
                    request_id=request_id,
                    has_current_file=bool(
                        request_metadata['editor_context'].get('current_file_path')
                    ),
                    open_tabs_count=open_tabs_count,
                )
            except Exception as e:
                logger.warning(
                    "Failed to extract editor_context", error=str(e), error_type=type(e).__name__
                )

        logger.info(
            "🔍 [COPILOT-RAG] Starting RAG search",
            request_id=request_id,
            stream=request.stream,
            has_editor_context=request_metadata is not None,
        )

        # Process chat with full history using existing sliding window
        # IMPORTANTE: Ahora pasamos stream=True/False al ChatService
        result_or_iterator = await chat_service.process_message_with_history(
            messages=conversation_history,
            current_message=last_message,
            session_id=request.session_id,  # Pasar session_id directamente
            debug=request.debug,
            stream=request.stream,  # IMPORTANTE: pasar el parámetro stream
            request_metadata=request_metadata,
        )

        # Handle streaming response
        if request.stream:
            logger.info(
                "Streaming chat completion returning stream",
                request_id=request_id,
                model=request.model,
            )

            # Adaptar la respuesta al formato SSE de OpenAI
            return StreamingResponse(
                _stream_response_adapter(
                    cast(AsyncIterator[str], result_or_iterator), request.model, request_id
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Request-ID": request_id,
                },
            )

        # Handle non-streaming response
        chat_response = cast(Dict[str, Any], result_or_iterator)
        session_id = chat_response.get("session_id")

        # Log RAG results after completion
        logger.info(
            "📚 [COPILOT-RAG] RAG search completed",
            request_id=request_id,
            chunks_found=chat_response.get("debug_info", {}).get("chunks_found", 0),
            query_type=chat_response.get("debug_info", {}).get("query_type", "unknown"),
            session_id=session_id,
        )

        # Build OpenAI-compatible response
        response = {
            "id": f"chatcmpl-{generate_id()[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,  # Echo of requested model
            "usage": {
                "prompt_tokens": chat_response.get("tokens_used", {}).get("prompt", 0),
                "completion_tokens": chat_response.get("tokens_used", {}).get("response", 0),
                "total_tokens": chat_response.get("tokens_used", {}).get("total", 0),
            },
            "choices": [
                {
                    "message": {"role": "assistant", "content": chat_response["response"]},
                    "finish_reason": "stop",
                    "index": 0,
                }
            ],
        }

        # Add ACOLYTE-specific fields only when debug is requested
        if request.debug:
            response["acolyte_metadata"] = {
                "session_id": session_id,
                "task_id": chat_response.get("task_id"),
            }

            if "debug_info" in chat_response:
                response["debug_info"] = {
                    "session_id": session_id,
                    "task_id": chat_response.get("task_id"),
                    "timing": {
                        "total_ms": int((time.time() - start_time) * 1000),
                        "processing_time": chat_response.get("processing_time", 0),
                    },
                    "related_sessions": [ctx.session_id for ctx in related_context],
                    "chunks_found": chat_response["debug_info"].get("chunks_found", 0),
                    "query_type": chat_response["debug_info"].get("query_type"),
                    "compression_used": chat_response["debug_info"].get("compression_used", False),
                    "dream_fatigue": chat_response["debug_info"].get("dream_fatigue"),
                }

            if request.explain_rag:
                response["rag_explanation"] = {
                    "query_original": last_message,
                    "search_strategy": "hybrid",  # semantic + lexical
                    "chunks_retrieved": (
                        chat_response["debug_info"].get("chunks_found", 0)
                        if "debug_info" in chat_response
                        else 0
                    ),
                }

            # Add Dream suggestion if present
            if "dream_suggestion" in chat_response:
                response["dream_suggestion"] = chat_response["dream_suggestion"]

        # Log completion
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "✅ [COPILOT-OUT] Response sent",
            request_id=request_id,
            duration_ms=processing_time_ms,
            streaming=False,
            response_preview=chat_response["response"][:200] + "...",
            tokens_used=response["usage"]["total_tokens"],
            rag_chunks_found=chat_response.get("debug_info", {}).get("chunks_found", 0),
            query_type=chat_response.get("debug_info", {}).get("query_type", "unknown"),
        )

        return response

    except ValidationError as e:
        logger.warning(
            "Chat validation failed", validation_message=e.message, request_id=request_id
        )
        raise HTTPException(status_code=400, detail=from_exception(e).model_dump())

    except ConfigurationError as e:
        logger.error(
            "Chat configuration error",
            config_error_message=e.message,
            request_id=request_id,
        )
        raise HTTPException(status_code=400, detail=from_exception(e).model_dump())

    except ExternalServiceError as e:
        logger.error(
            "Chat external service error",
            external_service_error_message=e.message,
            request_id=request_id,
        )
        raise HTTPException(status_code=503, detail=from_exception(e).model_dump())

    except Exception as e:
        logger.error(
            "❌ [COPILOT-ERROR] Request failed",
            error=str(e),
            error_type=type(e).__name__,
            request_id=request_id,
            phase="streaming" if request.stream else "sync",
            exc_info=True,
        )
        error_response = internal_error(
            message="Failed to process chat request",
            error_id=request_id,
            context={"error_type": type(e).__name__},
        )
        raise HTTPException(status_code=500, detail=error_response.model_dump())


@router.get("/models")
async def list_models():
    """
    List available models.
    Always returns acolyte:latest but with ID compatible for OpenAI clients.
    """
    logger.debug("Models request received")

    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-3.5-turbo",  # Fake ID for compatibility
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",  # Fake but expected by clients
                "permission": [
                    {
                        "id": "modelperm-acolyte",
                        "object": "model_permission",
                        "created": 1677610602,
                        "allow_create_engine": False,
                        "allow_sampling": True,
                        "allow_logprobs": True,
                        "allow_search_indices": False,
                        "allow_view": True,
                        "allow_fine_tuning": False,
                        "organization": "*",
                        "group": None,
                        "is_blocking": False,
                    }
                ],
                "root": "gpt-3.5-turbo",
                "parent": None,
            },
            # Additional model for compatibility
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "openai",
                "permission": [
                    {
                        "id": "modelperm-acolyte-gpt4",
                        "object": "model_permission",
                        "created": 1687882411,
                        "allow_create_engine": False,
                        "allow_sampling": True,
                        "allow_logprobs": True,
                        "allow_search_indices": False,
                        "allow_view": True,
                        "allow_fine_tuning": False,
                        "organization": "*",
                        "group": None,
                        "is_blocking": False,
                    }
                ],
                "root": "gpt-4",
                "parent": None,
            },
        ],
    }


@router.post("/embeddings")
async def create_embeddings(
    request: EmbeddingsRequest, x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
):
    """
    Generates `embeddings` using UniXcoder from the embeddings module.
    Compatible with OpenAI embeddings endpoint.
    """
    # Handle FastAPI Header(None) case - MUST be before try block
    request_id = x_request_id if x_request_id is not None else generate_id()
    start_time = time.time()

    # Normalize input to list with correct type for encode_batch
    texts: List[Union[str, Chunk]] = (
        cast(List[Union[str, Chunk]], list(request.input))
        if isinstance(request.input, list)
        else [request.input]
    )

    logger.info(
        "Embeddings request received",
        texts_count=len(texts),
        model=request.model,
        request_id=request_id,
    )

    try:
        # Get embeddings service (singleton)
        embeddings_service = get_embeddings()

        # Generate embeddings
        if len(texts) == 1:
            # Single embedding
            embedding_vector = embeddings_service.encode(texts[0])
            embeddings = [embedding_vector]
        else:
            # Batch embeddings
            embeddings = embeddings_service.encode_batch(texts)

        # Build response compatible with OpenAI
        data = []
        total_tokens = 0

        for i, embedding in enumerate(embeddings):
            # Convert to list for OpenAI compatibility
            if embedding is None:
                raise ValueError("Embedding generation failed: received None")
            embedding_list = embedding.to_weaviate()  # Already float64 list

            data.append(
                {
                    "object": "embedding",
                    "embedding": embedding_list,
                    "index": i,
                }
            )

            # Estimate tokens (approx 1 token = 4 chars)
            text_item = texts[i]
            if isinstance(text_item, str):
                total_tokens += len(text_item) // 4
            elif hasattr(text_item, 'content'):
                total_tokens += len(text_item.content) // 4

        processing_time = int((time.time() - start_time) * 1000)

        response = {
            "object": "list",
            "data": data,
            "model": "text-embedding-ada-002",  # Fake for compatibility
            "usage": {
                "prompt_tokens": total_tokens,
                "total_tokens": total_tokens,
            },
        }

        logger.info(
            "Embeddings generated",
            vectors_count=len(embeddings),
            dimensions=768,
            processing_time_ms=processing_time,
            request_id=request_id,
        )

        return response

    except Exception as e:
        logger.error("Embeddings failed", error=str(e), request_id=request_id, exc_info=True)

        # Determine error type
        if "CUDA" in str(e) or "device" in str(e).lower():
            error_response = external_service_error(
                service="embeddings_gpu",
                message="GPU embedding service unavailable, falling back to CPU",
            )
            status_code = 503
        else:
            error_response = internal_error(
                message="Failed to generate embeddings",
                error_id=request_id,
                context={"error_type": type(e).__name__, "texts_count": len(texts)},
            )
            status_code = 500

        raise HTTPException(status_code=status_code, detail=error_response.model_dump())


# ============================================================================
# FUNCIONES HELPER
# ============================================================================


def _generate_unique_session_id() -> str:
    """
    Generates a unique session_id using the centralized ID system.

    With 128 bits of entropy from hex32 generator, the probability of
    collision is negligible (1 in 3.4 × 10^38) for a mono-user system.

    Returns:
        unique session_id with format sess_{hex32}
    """
    # Use ACOLYTE's centralized ID generator (128 bits of entropy)
    return f"sess_{generate_id()}"
