"""
GitRepositoryManager - Singleton para compartir git.Repo entre workers.

FIXES RACE CONDITION: Múltiples EnrichmentService workers tratando de
crear git.Repo() simultáneamente en el mismo directorio .git

PATTERN: Similar al workaround de Weaviate shared client v3.26.7
"""

import asyncio
from typing import Optional, Dict
from pathlib import Path
import threading

import git
from git.exc import InvalidGitRepositoryError

from acolyte.core.logging import logger


class GitRepositoryManager:
    """
    Singleton manager para compartir git.Repo instances entre workers.

    FIXES: Race condition cuando múltiples workers crean git.Repo() al mismo tiempo
    PATTERN: Similar al shared Weaviate client workaround
    """

    _instances: Dict[str, 'GitRepositoryManager'] = {}
    _lock = threading.Lock()

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.repo: Optional[git.Repo] = None
        self.has_git = False
        self._initialized = False
        self._init_lock = asyncio.Lock()

    @classmethod
    def get_instance(cls, repo_path: str = ".") -> 'GitRepositoryManager':
        """
        Get singleton instance for a repository path.

        Args:
            repo_path: Path to Git repository

        Returns:
            GitRepositoryManager singleton instance
        """
        normalized_path = str(Path(repo_path).resolve())

        # Thread-safe singleton creation
        with cls._lock:
            if normalized_path not in cls._instances:
                cls._instances[normalized_path] = cls(repo_path)
                logger.info(
                    "Created GitRepositoryManager singleton",
                    repo_path=normalized_path,
                    instance_id=hex(id(cls._instances[normalized_path])),
                )

            return cls._instances[normalized_path]

    async def initialize(self) -> bool:
        """
        Initialize Git repository safely with async lock.

        Returns:
            bool: True if Git repository available, False otherwise
        """
        if self._initialized:
            return self.has_git

        async with self._init_lock:
            # Double-check pattern
            if self._initialized:
                return self.has_git

            try:
                logger.info("Initializing shared Git repository", repo_path=str(self.repo_path))
                self.repo = git.Repo(self.repo_path)
                self.has_git = True
                logger.info(
                    "Git repository loaded successfully",
                    git_dir=self.repo.git_dir,
                    instance_id=hex(id(self)),
                )

            except InvalidGitRepositoryError:
                logger.warning("No Git repository found", repo_path=str(self.repo_path))
                self.has_git = False

            except Exception as e:
                import traceback

                error_details = (
                    f"Error initializing Git repository\n"
                    f"  Type: {type(e).__name__}\n"
                    f"  Path: {str(self.repo_path)}\n"
                    f"  Error: {str(e)}\n"
                    f"  Traceback:\n{traceback.format_exc()}"
                )
                logger.error(error_details)
                self.has_git = False

            finally:
                self._initialized = True

        return self.has_git

    def get_repo(self) -> Optional[git.Repo]:
        """
        Get the shared Git repository instance.

        Returns:
            git.Repo instance if available, None otherwise
        """
        if not self._initialized:
            logger.warning("GitRepositoryManager not initialized - call initialize() first")
            return None

        return self.repo

    @classmethod
    def reset_instances(cls):
        """Reset all instances - mainly for testing."""
        with cls._lock:
            cls._instances.clear()
            logger.info("GitRepositoryManager instances reset")


# Convenience function for easy access
def get_git_manager(repo_path: str = ".") -> GitRepositoryManager:
    """
    Get GitRepositoryManager singleton instance.

    Args:
        repo_path: Path to Git repository

    Returns:
        GitRepositoryManager singleton instance
    """
    return GitRepositoryManager.get_instance(repo_path)
