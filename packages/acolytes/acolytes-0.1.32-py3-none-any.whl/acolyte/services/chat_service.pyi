from typing import Dict, Any, Optional, List, Union, AsyncIterator
from acolyte.services.conversation_service import ConversationService
from acolyte.services.task_service import TaskService
from acolyte.services.git_service import GitService
from acolyte.core.tracing import MetricsCollector
from acolyte.core.token_counter import TokenBudgetManager, SmartTokenCounter
from acolyte.core.ollama import OllamaClient
from acolyte.core.secure_config import Settings
from acolyte.semantic import (
    Summarizer,
    TaskDetector,
    QueryAnalyzer,
    DecisionDetector,
)
from acolyte.rag.retrieval.hybrid_search import HybridSearch
from acolyte.rag.compression import ContextualCompressor
from acolyte.models.task_checkpoint import TaskCheckpoint, TaskType
from acolyte.dream import DreamOrchestrator

class ChatService:
    metrics: MetricsCollector
    token_manager: TokenBudgetManager
    token_counter: SmartTokenCounter
    ollama: OllamaClient
    config: Settings
    debug_mode: bool
    weaviate_client: Optional[Any]
    query_analyzer: QueryAnalyzer
    task_detector: TaskDetector
    summarizer: Summarizer
    decision_detector: DecisionDetector
    conversation_service: ConversationService
    task_service: TaskService
    hybrid_search: Optional[HybridSearch]
    compressor: Optional[ContextualCompressor]
    git_service: Optional[GitService]
    dream_orchestrator: Optional[DreamOrchestrator]
    _active_session_id: Optional[str]
    _active_task: Optional[TaskCheckpoint]
    _last_user_message: Optional[str]

    def __init__(
        self,
        context_size: int,
        conversation_service: Optional[ConversationService] = None,
        task_service: Optional[TaskService] = None,
        debug_mode: bool = False,
    ) -> None: ...
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        debug: Optional[bool] = None,
        stream: bool = False,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], AsyncIterator[str]]: ...
    async def process_message_with_history(
        self,
        messages: List[Dict[str, str]],
        current_message: str,
        session_id: Optional[str] = None,
        debug: Optional[bool] = None,
        stream: bool = False,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], AsyncIterator[str]]: ...
    async def _post_process_response(
        self,
        user_message: str,
        assistant_response: str,
        session_id: str,
        context_chunks: List,
        task_id: Optional[str],
        tokens_used: int,
        summary_result=None,
    ) -> None: ...
    async def _stream_and_post_process(
        self,
        stream_iterator: AsyncIterator[str],
        user_message: str,
        session_id: str,
        context_chunks: List,
        task_id: Optional[str],
    ) -> AsyncIterator[str]: ...
    async def _handle_new_chat(self) -> str: ...
    def _infer_task_type(self, message: str) -> TaskType: ...
    async def _generate_with_retry(
        self,
        user_message: str,
        context_chunks: list,
        max_tokens: int,
        stream: bool = False,
        max_attempts: int = 3,
    ) -> Union[str, AsyncIterator[str]]: ...
    async def _get_project_info(self) -> Dict[str, Any]: ...
    async def _check_dream_suggestion(self) -> Optional[Dict[str, Any]]: ...
    def _is_code_related_query(self, message: str) -> bool: ...
    async def request_dream_analysis(
        self, user_query: str, focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]: ...
    async def get_active_session_info(self) -> Dict[str, Any]: ...
    async def cleanup(self) -> None: ...
