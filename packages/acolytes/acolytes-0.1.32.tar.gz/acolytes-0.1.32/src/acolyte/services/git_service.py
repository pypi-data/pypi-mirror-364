"""
Git Service - Operaciones Git internas REACTIVAS.

IMPORTANTE:
- NO hace fetch automático (Decisión #11)
- Reacciona cuando usuario hace cambios
- Usa GitPython, NUNCA comandos shell
- Solo detecta y notifica
"""

from acolyte.core.logging import logger
from acolyte.core.tracing import MetricsCollector
from acolyte.core.exceptions import ExternalServiceError
from acolyte.core.events import EventBus, CacheInvalidateEvent, event_bus as global_event_bus
from git import Repo  # type: ignore
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import time
from acolyte.core.utils.datetime_utils import utc_now
from datetime import timedelta
from configparser import NoOptionError, NoSectionError
from acolyte.core.utils.retry import retry_async
import asyncio


class GitService:
    """
    Operaciones Git internas REACTIVAS.

    IMPORTANTE:
    - NO hace fetch automático (Decisión #11)
    - Reacciona cuando usuario hace cambios
    - Usa GitPython, NUNCA comandos shell
    - Solo detecta y notifica
    """

    def __init__(self, repo_path: str, event_bus: Optional[EventBus] = None):
        self.metrics = MetricsCollector()
        self.repo_path = Path(repo_path).resolve()

        # Cache con TTL
        self._repo_cache = None
        self._repo_cache_time = None
        self._repo_cache_ttl = timedelta(minutes=5)  # TTL de 5 minutos

        self.event_bus = event_bus or global_event_bus  # Usar global si no se pasa

        # Validar que es un repo Git
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            logger.warning(
                f"No Git repository found at {repo_path}. Git features will be disabled.",
                repo_path=str(self.repo_path),
            )
            # NO lanzar excepción, permitir que el servicio funcione sin Git
            self._git_available = False
        else:
            self._git_available = True

        logger.info(
            "GitService initialized",
            repo_path=str(self.repo_path),
            git_available=self._git_available,
        )

    @property
    def repo(self) -> Repo:
        """
        Lazy loading del repo con cache y TTL.

        Raises:
            ExternalServiceError: Si Git no está disponible
        """
        if not self._git_available:
            raise ExternalServiceError("Git repository not available")

        now = utc_now()

        # Verificar si el cache es válido
        if (
            self._repo_cache
            and self._repo_cache_time
            and now - self._repo_cache_time < self._repo_cache_ttl
        ):
            return self._repo_cache

        # Cache expirado o no existe, recargar
        try:
            self._repo_cache = Repo(self.repo_path)
            self._repo_cache_time = now
            return self._repo_cache
        except Exception as e:
            logger.error("Failed to load Git repository", error=str(e))
            self._git_available = False  # Marcar como no disponible
            raise ExternalServiceError(f"Failed to load Git repository: {str(e)}") from e

    def invalidate_repo_cache(self):
        """
        Invalida manualmente el cache del repo.

        Útil cuando se sabe que hubo cambios externos.
        """
        self._repo_cache = None
        self._repo_cache_time = None

    async def detect_changes_from_others(self) -> List[Dict[str, Any]]:
        """
        Detecta cambios de otros desarrolladores.

        SE LLAMA: Después que el usuario hace pull/fetch
        NO hace fetch automático

        Raises:
            ExternalServiceError: Si no se puede acceder al repositorio Git

        Returns:
            Lista de cambios detectados con commit info
        """
        start_time = time.time()
        try:
            changes = []
            since = utc_now() - timedelta(days=1)
            current_identities = set()
            try:
                config = await retry_async(
                    lambda: asyncio.get_running_loop().run_in_executor(
                        None, self.repo.config_reader
                    ),
                    max_attempts=3,
                    retry_on=(ExternalServiceError, Exception),
                    logger=logger,
                )
                try:
                    email = config.get_value("user", "email")
                    if email:
                        current_identities.add(str(email).lower())
                except (NoOptionError, NoSectionError):
                    logger.warning("[TRACE] No git user email configured")
                    pass
                try:
                    name = config.get_value("user", "name")
                    if name:
                        current_identities.add(name)
                except (NoOptionError, NoSectionError):
                    logger.warning("[TRACE] No git user name configured")
                    pass
            except Exception as e:
                logger.warning("Could not read git config", error=str(e))
            if not current_identities:
                logger.warning("Git user not configured. Showing all recent commits.")
            # iter_commits es operación de disco pesada
            commits = await retry_async(
                lambda: asyncio.get_running_loop().run_in_executor(
                    None, lambda: list(self.repo.iter_commits(since=since))
                ),
                max_attempts=3,
                retry_on=(ExternalServiceError, Exception),
                logger=logger,
            )
            for commit in commits:
                if current_identities:
                    commit_email = commit.author.email.lower() if commit.author.email else ""
                    commit_name = commit.author.name
                    if commit_email in current_identities or commit_name in current_identities:
                        continue
                modified_files = list(commit.stats.files.keys())
                changes.append(
                    {
                        "commit": commit.hexsha[:8],
                        "author": commit.author.name,
                        "email": commit.author.email,
                        "message": commit.message.strip(),
                        "files": modified_files,
                        "timestamp": utc_now(),  # Using current time as commit time is not critical
                        "is_merge": len(commit.parents) > 1,
                    }
                )
            self.metrics.gauge("services.git_service.changes_detected", len(changes))
            if changes and self.event_bus:
                await self._publish_cache_invalidation(
                    reason="Changes from other developers detected",
                    files=[f for change in changes for f in change["files"]],
                )
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record(
                "services.git_service.detect_changes_from_others_time_ms", elapsed_ms
            )
            return changes
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record(
                "services.git_service.detect_changes_from_others_time_ms", elapsed_ms
            )
            logger.error("Error detecting changes", error=str(e))
            raise ExternalServiceError(f"Failed to detect changes: {str(e)}") from e

    async def analyze_potential_conflicts(self, files_to_modify: List[str]) -> Dict[str, Any]:
        """
        Analiza conflictos potenciales.

        Args:
            files_to_modify: Lista de archivos a verificar

        Returns:
            Dict con:
            - files_with_conflicts: Lista de archivos
            - severity: 0-10
            - suggestions: Qué hacer

        Raises:
            ExternalServiceError: Si no se puede analizar el repositorio
        """
        start_time = time.time()
        try:
            conflicts = []
            total_severity = 0
            # Verificar estado del repo (is_dirty es sync)
            is_dirty = await retry_async(
                lambda: asyncio.get_running_loop().run_in_executor(
                    None, lambda: self.repo.is_dirty(untracked_files=False)
                ),
                max_attempts=3,
                retry_on=(ExternalServiceError, Exception),
                logger=logger,
            )
            if is_dirty:
                logger.warning("Repository has uncommitted changes")
            for file_path in files_to_modify:
                path = Path(file_path)
                if not path.is_absolute():
                    path = self.repo_path / path
                if not path.exists():
                    logger.warning("[TRACE] File does not exist during conflict analysis")
                    continue
                relative_path = str(path.relative_to(self.repo_path))
                try:
                    # iter_commits es sync
                    commits = await retry_async(
                        lambda: asyncio.get_running_loop().run_in_executor(
                            None,
                            lambda: list(self.repo.iter_commits(paths=relative_path, max_count=5)),
                        ),
                        max_attempts=3,
                        retry_on=(ExternalServiceError, Exception),
                        logger=logger,
                    )
                    if len(commits) > 1:
                        authors = {c.author.email for c in commits[:3]}
                        if len(authors) > 1:
                            severity = min(10, 5 + (2 * len(authors)))
                            conflicts.append(
                                {
                                    "file": relative_path,
                                    "reason": "Multiple recent authors",
                                    "authors": list(authors),
                                    "severity": severity,
                                }
                            )
                            total_severity += severity
                    # index.diff es sync
                    staged = await retry_async(
                        lambda: asyncio.get_running_loop().run_in_executor(
                            None, lambda: [item.a_path for item in self.repo.index.diff("HEAD")]
                        ),
                        max_attempts=3,
                        retry_on=(ExternalServiceError, Exception),
                        logger=logger,
                    )
                    if relative_path in staged:
                        conflicts.append(
                            {
                                "file": relative_path,
                                "reason": "File has staged changes",
                                "severity": 5,
                            }
                        )
                        total_severity += 5
                except Exception as e:
                    logger.warning(
                        "[TRACE] Could not analyze history",
                        file=relative_path,
                        error=str(e),
                    )
                    logger.warning("Could not analyze history", file=relative_path, error=str(e))
            avg_severity = min(10, total_severity / max(1, len(files_to_modify)))
            suggestions = []
            if avg_severity > 7:
                suggestions.append("Consider coordinating with team before modifying")
                suggestions.append("Review recent changes with 'git log -p <file>'")
            elif avg_severity > 4:
                suggestions.append("Check for recent changes before proceeding")
                suggestions.append("Consider creating a feature branch")
            else:
                suggestions.append("Low conflict risk, proceed normally")
            result = {
                "files_with_conflicts": [c["file"] for c in conflicts],
                "severity": round(avg_severity, 1),
                "suggestions": suggestions,
                "details": conflicts,
            }
            self.metrics.gauge("services.git_service.conflict_severity", avg_severity)
            self.metrics.increment("services.git_service.conflicts_analyzed", len(conflicts))
            if conflicts and avg_severity > 4 and self.event_bus:
                await self._publish_cache_invalidation(
                    reason=f"Potential conflicts detected (severity: {avg_severity})",
                    files=[c["file"] for c in conflicts],
                )
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.analyze_conflicts_time_ms", elapsed_ms)
            return result
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.analyze_conflicts_time_ms", elapsed_ms)
            logger.error("Error analyzing conflicts", error=str(e))
            raise ExternalServiceError(f"Failed to analyze conflicts: {str(e)}") from e

    async def get_co_modification_patterns(
        self, file_path: str, days_back: int = 30
    ) -> List[Tuple[str, float]]:
        """
        Archivos que cambian junto a este.

        Usado por: Grafo neuronal

        Args:
            file_path: Archivo a analizar
            days_back: Días hacia atrás para analizar

        Returns:
            Lista de tuplas (archivo, frecuencia) ordenadas por frecuencia

        Raises:
            ExternalServiceError: Si falla el análisis de co-modificaciones
        """
        start_time = time.time()
        try:
            # Normalizar path
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.repo_path / target_path
            relative_path = str(target_path.relative_to(self.repo_path))

            # Recopilar commits que modificaron el archivo objetivo
            since = utc_now() - timedelta(days=days_back)
            target_commits = set()

            for commit in self.repo.iter_commits(paths=relative_path, since=since):
                target_commits.add(commit.hexsha)

            if not target_commits:
                return []

            # Contar co-modificaciones
            co_modifications = {}

            for commit_sha in target_commits:
                commit = self.repo.commit(commit_sha)
                # Obtener todos los archivos modificados en este commit
                for file in commit.stats.files.keys():
                    if file != relative_path:  # Excluir el archivo objetivo
                        co_modifications[file] = co_modifications.get(file, 0) + 1

            # Calcular frecuencias (0-1)
            total_commits = len(target_commits)
            patterns = [(file, count / total_commits) for file, count in co_modifications.items()]

            # Ordenar por frecuencia descendente
            patterns.sort(key=lambda x: x[1], reverse=True)

            # Tomar top 10
            patterns = patterns[:10]

            self.metrics.gauge("services.git_service.co_modification_patterns", len(patterns))

            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.co_modification_analysis_time_ms", elapsed_ms)
            return patterns

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.co_modification_analysis_time_ms", elapsed_ms)
            logger.error("Error analyzing co-modifications", error=str(e))
            raise ExternalServiceError(f"Failed to analyze co-modifications: {str(e)}") from e

    async def notify_in_chat(self, notification_type: str, data: Dict[str, Any]) -> str:
        """
        Genera notificación para mostrar en chat.

        IMPORTANTE: Este método NO lanza excepciones. En caso de error,
        retorna string vacío. Esto es por diseño ya que las notificaciones
        son opcionales y no deben interrumpir el flujo principal.

        Ejemplo: "Veo que actualizaste auth.py. ¿Quieres que revise los cambios?"

        Args:
            notification_type: Tipo de notificación (file_updated, conflicts_detected, etc.)
            data: Datos específicos para la notificación

        Returns:
            Mensaje de notificación o string vacío si hay error
        """
        start_time = time.time()
        try:
            notifications = {
                "file_updated": self._notify_file_updated,
                "conflicts_detected": self._notify_conflicts,
                "branch_changed": self._notify_branch_change,
                "changes_from_others": self._notify_others_changes,
            }

            handler = notifications.get(notification_type)
            if not handler:
                logger.warning("Unknown notification type", type=notification_type)
                return ""

            message = handler(data)
            self.metrics.increment(f"services.git_service.notifications.{notification_type}")

            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.generate_notification_time_ms", elapsed_ms)
            return message

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.generate_notification_time_ms", elapsed_ms)
            logger.warning("[TRACE] notify_in_chat error handling")
            logger.error("Error generating notification", error=str(e))
            # Para notificaciones, retornar string vacío es aceptable
            # ya que no son críticas para el flujo principal
            return ""

    def _notify_file_updated(self, data: Dict[str, Any]) -> str:
        """Notificación de archivo actualizado."""
        files = data.get("files", [])
        if not files:
            return ""

        if len(files) == 1:
            return f"Veo que actualizaste {files[0]}. ¿Quieres que revise los cambios?"
        else:
            return (
                f"Veo que actualizaste {len(files)} archivos "
                f"({', '.join(files[:3])}{', ...' if len(files) > 3 else ''}). "
                "¿Quieres que revise los cambios?"
            )

    def _notify_conflicts(self, data: Dict[str, Any]) -> str:
        """Notificación de conflictos potenciales."""
        severity = data.get("severity", 0)
        files = data.get("files_with_conflicts", [])

        if severity > 7:
            return (
                f"⚠️ Detecté posibles conflictos en {', '.join(files[:2])}. "
                "Otros desarrolladores han estado trabajando en estos archivos. "
                "¿Revisamos los cambios recientes primero?"
            )
        elif severity > 4:
            return (
                f"Hay algunos cambios recientes en {files[0]}. "
                "Podría ser buena idea revisar antes de modificar."
            )
        else:
            return ""

    def _notify_branch_change(self, data: Dict[str, Any]) -> str:
        """Notificación de cambio de branch."""
        old_branch = data.get("old_branch", "unknown")
        new_branch = data.get("new_branch", "unknown")

        return (
            f"Cambiaste de la rama '{old_branch}' a '{new_branch}'. "
            "¿Necesitas contexto sobre lo que estábamos haciendo aquí?"
        )

    def _notify_others_changes(self, data: Dict[str, Any]) -> str:
        """Notificación de cambios de otros."""
        changes = data.get("changes", [])
        if not changes:
            return ""

        authors = {c.get("author") for c in changes[:3]}
        files_count = sum(len(c.get("files", [])) for c in changes)

        return (
            f"Hay {len(changes)} commits nuevos de {', '.join(authors)} "
            f"que modificaron {files_count} archivos. "
            "¿Quieres que revise qué cambió?"
        )

    async def _publish_cache_invalidation(
        self,
        reason: str,
        files: Optional[List[str]] = None,
        target_services: Optional[List[str]] = None,
    ):
        """
        Publica evento de invalidación de cache.

        Args:
            reason: Razón de la invalidación
            files: Archivos afectados (opcional)
            target_services: Servicios específicos a invalidar (por defecto todos)
        """
        if not self.event_bus:
            return

        # Si no se especifican servicios, invalidar los principales
        if target_services is None:
            target_services = ["conversation", "indexing", "enrichment"]

        try:
            for service in target_services:
                # Crear patrón de key basado en archivos si están disponibles
                if files:
                    # Para cada archivo, invalidar cache relacionado
                    for file in files[:10]:  # Limitar a 10 archivos
                        event = CacheInvalidateEvent(
                            source="git_service",
                            target_service=service,
                            key_pattern=f"*{file}*",
                            reason=f"{reason}: {file}",
                        )
                        await self.event_bus.publish(event)
                else:
                    # Invalidación general
                    event = CacheInvalidateEvent(
                        source="git_service", target_service=service, key_pattern="*", reason=reason
                    )
                    await self.event_bus.publish(event)

            logger.info(
                "Published cache invalidation events",
                reason=reason,
                services=target_services,
                files_count=len(files) if files else 0,
            )

        except Exception as e:
            # No fallar si la publicación de eventos falla
            logger.warning("[TRACE] Failed to publish cache invalidation event")
            logger.warning("Failed to publish cache invalidation", error=str(e))

    def _fix_git_ownership_issue(self) -> bool:
        """
        Intenta arreglar el problema de 'dubious ownership' en Git.

        Returns:
            True si se pudo arreglar, False si no
        """
        try:
            import subprocess

            # Comando para hacer el directorio seguro
            cmd = ["git", "config", "--global", "--add", "safe.directory", str(self.repo_path)]

            logger.info("Attempting to fix Git ownership issue", repo_path=str(self.repo_path))

            # Ejecutar el comando
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10, cwd=str(self.repo_path)
            )

            if result.returncode == 0:
                logger.info("Git ownership issue fixed successfully")
                # Invalidar cache para recargar con nueva configuración
                self.invalidate_repo_cache()
                return True
            else:
                logger.warning(
                    "Failed to fix Git ownership issue",
                    stderr=result.stderr,
                    returncode=result.returncode,
                )
                return False

        except Exception as e:
            logger.warning("Error while fixing Git ownership issue", error=str(e))
            return False

    def get_most_recent_files(self, max_files: int = 10, days_back: int = 7) -> List[str]:
        """
        Returns a list of files modified in the last `days_back` days, up to `max_files` unique files.

        NOTA: En caso de error (común en Docker/Windows), retorna lista vacía sin fallar.

        Args:
            max_files: Maximum number of unique files to return.
            days_back: Number of days to look back for modified files.

        Returns:
            List of file paths (str) modified in the given period, up to max_files.
        """
        start_time = time.time()
        try:
            # Verificar que el repo es accesible
            if not self._git_available:
                logger.debug("Git repository not available, returning empty list")
                return []

            since = utc_now() - timedelta(days=days_back)
            recent_files = []
            seen = set()

            # Intentar obtener commits
            commits = list(self.repo.iter_commits(since=since))

            for commit in commits:
                for file in commit.stats.files.keys():
                    if file not in seen:
                        recent_files.append(file)
                        seen.add(file)
                    if len(recent_files) >= max_files:
                        elapsed_ms = (time.time() - start_time) * 1000
                        self.metrics.record(
                            "services.git_service.get_most_recent_files_time_ms", elapsed_ms
                        )
                        self.metrics.gauge(
                            "services.git_service.most_recent_files_count", len(recent_files)
                        )
                        return recent_files

            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.get_most_recent_files_time_ms", elapsed_ms)
            self.metrics.gauge("services.git_service.most_recent_files_count", len(recent_files))
            return recent_files

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.metrics.record("services.git_service.get_most_recent_files_time_ms", elapsed_ms)

            # Verificar si es el error específico de "dubious ownership"
            error_str = str(e).lower()
            if "dubious ownership" in error_str or "sha is empty" in error_str:
                logger.info("Detected Git ownership issue, attempting to fix...")

                # Intentar arreglar el problema
                if self._fix_git_ownership_issue():
                    # Reintentar la operación
                    try:
                        logger.info("Retrying Git operation after ownership fix")
                        commits = list(self.repo.iter_commits(since=since))

                        for commit in commits:
                            for file in commit.stats.files.keys():
                                if file not in seen:
                                    recent_files.append(file)
                                    seen.add(file)
                                if len(recent_files) >= max_files:
                                    elapsed_ms = (time.time() - start_time) * 1000
                                    self.metrics.record(
                                        "services.git_service.get_most_recent_files_time_ms",
                                        elapsed_ms,
                                    )
                                    self.metrics.gauge(
                                        "services.git_service.most_recent_files_count",
                                        len(recent_files),
                                    )
                                    return recent_files

                        elapsed_ms = (time.time() - start_time) * 1000
                        self.metrics.record(
                            "services.git_service.get_most_recent_files_time_ms", elapsed_ms
                        )
                        self.metrics.gauge(
                            "services.git_service.most_recent_files_count", len(recent_files)
                        )
                        return recent_files

                    except Exception as retry_error:
                        logger.warning(
                            "Git operation still failed after ownership fix", error=str(retry_error)
                        )

            # Log como warning en lugar de error (no es crítico)
            logger.warning(
                "Git operations unavailable (common in Docker/Windows)",
                error=str(e),
                error_type=type(e).__name__,
            )

            # Retornar lista vacía para no interrumpir el flujo
            return []
