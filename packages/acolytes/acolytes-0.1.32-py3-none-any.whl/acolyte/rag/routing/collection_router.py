from pathlib import Path
from acolyte.core.utils.file_types import FileTypeDetector, FileCategory


class CollectionRouter:
    """
    Centralizes the logic for routing files to the correct Weaviate collection.
    This is a key component of the multi-collection architecture.
    """

    _MAPPING = {
        FileCategory.CODE: "CodeChunk",
        FileCategory.DOCUMENTATION: "DocChunk",
        FileCategory.CONFIGURATION: "ConfigChunk",
        FileCategory.TEST: "TestChunk",
        FileCategory.DATA: "ConfigChunk",  # Route data files like JSON, XML to ConfigChunk
        FileCategory.BUILD: "ConfigChunk",  # Route build files like lock files to ConfigChunk
        # DATA, BUILD, and OTHER files are not routed to a specific chunk collection for now.
        # They might be handled differently or ignored during the indexing pipeline.
    }

    def get_collection_for_file(self, file_path: Path) -> str | None:
        """
        Determines the correct Weaviate collection for a given file path.

        Args:
            file_path: The Path object of the file to categorize.

        Returns:
            The name of the target Weaviate collection as a string, or None
            if the file category is not meant to be indexed into a chunk collection.
        """
        category = FileTypeDetector.get_category(file_path)
        return self._MAPPING.get(category)
