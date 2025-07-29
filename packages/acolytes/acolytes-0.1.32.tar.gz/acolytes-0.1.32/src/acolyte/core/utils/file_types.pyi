from enum import Enum, auto
from pathlib import Path
from typing import Dict, Set, ClassVar

class FileCategory(Enum):
    CODE = auto()
    TEST = auto()
    DOCUMENTATION = auto()
    CONFIGURATION = auto()
    DATA = auto()
    BUILD = auto()
    BINARY = auto()
    OTHER = auto()

class FileTypeDetector:
    _initialized: ClassVar[bool]
    _category_map: ClassVar[Dict[str, FileCategory]]
    _language_map: ClassVar[Dict[str, str]]
    _supported_extensions: ClassVar[Set[str]]
    _extension_languages: ClassVar[Dict[str, str]]
    _extension_categories: ClassVar[Dict[str, FileCategory]]
    _name_categories: ClassVar[Dict[str, FileCategory]]

    @classmethod
    def _initialize(cls) -> None: ...
    @classmethod
    def get_category(cls, path: Path) -> FileCategory: ...
    @classmethod
    def get_language(cls, path: Path) -> str: ...
    @classmethod
    def get_all_supported_extensions(cls) -> Set[str]: ...
    @classmethod
    def is_supported(cls, path: Path) -> bool: ...
