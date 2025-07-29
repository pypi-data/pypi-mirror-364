from enum import Enum, auto
from pathlib import Path
from typing import Dict, Set


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
    _initialized: bool = False
    _category_map: Dict[str, FileCategory] = {}
    _language_map: Dict[str, str] = {}
    _supported_extensions: Set[str] = set()

    _extension_languages: Dict[str, str] = {
        ".py": "python",
        ".pyi": "python",
        ".js": "javascript",
        ".mjs": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".kt": "kotlin",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",  # Often used with C
        ".hpp": "cpp",
        ".cs": "csharp",
        ".swift": "swift",
        ".rb": "ruby",
        ".php": "php",
        ".scala": "scala",
        ".r": "r",
        ".pl": "perl",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".lua": "lua",
        ".sql": "sql",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "css",
        ".less": "css",
        ".vue": "vue",
        ".svelte": "svelte",
        ".xml": "xml",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
        ".cfg": "ini",  # Often INI-like
        ".conf": "ini",  # Often INI-like
        ".md": "markdown",
        ".markdown": "markdown",
        ".rst": "rst",
        ".txt": "text",
        "dockerfile": "dockerfile",
        "makefile": "makefile",
    }

    _extension_categories: Dict[str, FileCategory] = {
        # Code
        ".py": FileCategory.CODE,
        ".pyi": FileCategory.CODE,
        ".js": FileCategory.CODE,
        ".mjs": FileCategory.CODE,
        ".ts": FileCategory.CODE,
        ".tsx": FileCategory.CODE,
        ".java": FileCategory.CODE,
        ".kt": FileCategory.CODE,
        ".kts": FileCategory.CODE,
        ".go": FileCategory.CODE,
        ".rs": FileCategory.CODE,
        ".c": FileCategory.CODE,
        ".cpp": FileCategory.CODE,
        ".h": FileCategory.CODE,
        ".hpp": FileCategory.CODE,
        ".cs": FileCategory.CODE,
        ".swift": FileCategory.CODE,
        ".rb": FileCategory.CODE,
        ".php": FileCategory.CODE,
        ".scala": FileCategory.CODE,
        ".r": FileCategory.CODE,
        ".pl": FileCategory.CODE,
        ".pm": FileCategory.CODE,
        ".sh": FileCategory.CODE,
        ".bash": FileCategory.CODE,
        ".zsh": FileCategory.CODE,
        ".lua": FileCategory.CODE,
        ".sql": FileCategory.CODE,
        ".html": FileCategory.CODE,
        ".htm": FileCategory.CODE,
        ".css": FileCategory.CODE,
        ".scss": FileCategory.CODE,
        ".less": FileCategory.CODE,
        ".vue": FileCategory.CODE,
        ".svelte": FileCategory.CODE,
        ".xml": FileCategory.CODE,
        ".xaml": FileCategory.CODE,
        ".el": FileCategory.CODE,
        ".vim": FileCategory.CODE,
        # Documentation
        ".md": FileCategory.DOCUMENTATION,
        ".markdown": FileCategory.DOCUMENTATION,
        ".rst": FileCategory.DOCUMENTATION,
        ".txt": FileCategory.DOCUMENTATION,
        ".tex": FileCategory.DOCUMENTATION,
        ".adoc": FileCategory.DOCUMENTATION,
        ".asciidoc": FileCategory.DOCUMENTATION,
        ".rtf": FileCategory.DOCUMENTATION,
        # Configuration
        ".json": FileCategory.CONFIGURATION,
        ".yaml": FileCategory.CONFIGURATION,
        ".yml": FileCategory.CONFIGURATION,
        ".toml": FileCategory.CONFIGURATION,
        ".ini": FileCategory.CONFIGURATION,
        ".cfg": FileCategory.CONFIGURATION,
        ".conf": FileCategory.CONFIGURATION,
        ".properties": FileCategory.CONFIGURATION,
        ".env": FileCategory.CONFIGURATION,
        # Data
        ".csv": FileCategory.DATA,
        ".jsonl": FileCategory.DATA,
        ".parquet": FileCategory.DATA,
        ".xls": FileCategory.DATA,
        ".xlsx": FileCategory.DATA,
        ".db": FileCategory.DATA,
        ".sqlite": FileCategory.DATA,
        ".sqlite3": FileCategory.DATA,
        # Build & Packaging
        ".dockerfile": FileCategory.BUILD,
        "dockerfile": FileCategory.BUILD,
        ".makefile": FileCategory.BUILD,
        "makefile": FileCategory.BUILD,
        "gemfile": FileCategory.BUILD,
        "procfile": FileCategory.BUILD,
        ".csproj": FileCategory.BUILD,
        ".sln": FileCategory.BUILD,
        ".vbproj": FileCategory.BUILD,
        "pom.xml": FileCategory.BUILD,
        "build.gradle": FileCategory.BUILD,
        "package.json": FileCategory.BUILD,
        "package-lock.json": FileCategory.BUILD,
        "yarn.lock": FileCategory.BUILD,
        "pnpm-lock.yaml": FileCategory.BUILD,
        "requirements.txt": FileCategory.BUILD,
        "pyproject.toml": FileCategory.BUILD,
        "setup.py": FileCategory.BUILD,
        "setup.cfg": FileCategory.BUILD,
        ".lock": FileCategory.BUILD,
        # Binary (to be ignored but categorized)
        ".png": FileCategory.BINARY,
        ".jpg": FileCategory.BINARY,
        ".jpeg": FileCategory.BINARY,
        ".gif": FileCategory.BINARY,
        ".bmp": FileCategory.BINARY,
        ".ico": FileCategory.BINARY,
        ".svg": FileCategory.BINARY,
        ".pdf": FileCategory.BINARY,
        ".doc": FileCategory.BINARY,
        ".docx": FileCategory.BINARY,
        ".ppt": FileCategory.BINARY,
        ".pptx": FileCategory.BINARY,
        ".zip": FileCategory.BINARY,
        ".tar": FileCategory.BINARY,
        ".gz": FileCategory.BINARY,
        ".rar": FileCategory.BINARY,
        ".7z": FileCategory.BINARY,
        ".jar": FileCategory.BINARY,
        ".war": FileCategory.BINARY,
        ".ear": FileCategory.BINARY,
        ".exe": FileCategory.BINARY,
        ".dll": FileCategory.BINARY,
        ".so": FileCategory.BINARY,
        ".a": FileCategory.BINARY,
        ".lib": FileCategory.BINARY,
        ".o": FileCategory.BINARY,
        ".obj": FileCategory.BINARY,
        ".class": FileCategory.BINARY,
        ".pyc": FileCategory.BINARY,
        ".pyd": FileCategory.BINARY,
    }

    _name_categories: Dict[str, FileCategory] = {
        "readme": FileCategory.DOCUMENTATION,
        "license": FileCategory.DOCUMENTATION,
        "contributing": FileCategory.DOCUMENTATION,
        "changelog": FileCategory.DOCUMENTATION,
        "dockerfile": FileCategory.BUILD,
        "makefile": FileCategory.BUILD,
        "gemfile": FileCategory.BUILD,
        "procfile": FileCategory.BUILD,
        "requirements.txt": FileCategory.BUILD,
        "pyproject.toml": FileCategory.BUILD,
        "package.json": FileCategory.BUILD,
        "package-lock.json": FileCategory.BUILD,
        "yarn.lock": FileCategory.BUILD,
        "pnpm-lock.yaml": FileCategory.BUILD,
    }

    @classmethod
    def _initialize(cls):
        if cls._initialized:
            return
        cls._category_map = {ext: cat for ext, cat in cls._extension_categories.items()}
        cls._language_map = {ext: lang for ext, lang in cls._extension_languages.items()}
        cls._supported_extensions = {
            ext for ext, cat in cls._category_map.items() if cat != FileCategory.BINARY and ext
        }
        cls._initialized = True

    @classmethod
    def get_category(cls, path: Path) -> FileCategory:
        cls._initialize()

        # --- Test File Detection (Highest Priority) ---
        path_str = str(path).lower().replace("\\\\", "/")
        if "tests/" in path_str or "test/" in path_str:
            return FileCategory.TEST

        name_lower = path.name.lower()
        if name_lower.startswith("test_") or name_lower.endswith("_test.py"):
            return FileCategory.TEST
        if ".spec." in name_lower or ".test." in name_lower:
            return FileCategory.TEST

        # --- Name-based Detection (e.g., README, LICENSE without extension) ---
        stem_lower = path.stem.lower()
        if stem_lower in cls._name_categories:
            return cls._name_categories[stem_lower]

        # Check full name for files like 'requirements.txt'
        if name_lower in cls._name_categories:
            return cls._name_categories[name_lower]

        # --- Extension-based Detection (Most Common) ---
        extension = path.suffix.lower()
        return cls._category_map.get(extension, FileCategory.OTHER)

    @classmethod
    def get_language(cls, path: Path) -> str:
        """Detect language from file path. Fallback to 'unknown'."""
        cls._initialize()
        extension = path.suffix.lower()
        if extension in cls._language_map:
            return cls._language_map[extension]

        name_lower = path.name.lower()
        if name_lower in cls._language_map:
            return cls._language_map[name_lower]

        return "unknown"

    @classmethod
    def get_all_supported_extensions(cls) -> Set[str]:
        """Returns a set of all non-binary file extensions."""
        cls._initialize()
        return cls._supported_extensions

    @classmethod
    def is_supported(cls, path: Path) -> bool:
        """
        Check if a file is supported for indexing based on its category.
        Binary files are categorized but not supported for content indexing.
        """
        category = cls.get_category(path)
        return category != FileCategory.BINARY and category != FileCategory.OTHER


# Initialize the detector on module load
FileTypeDetector._initialize()
