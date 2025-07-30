from typing import List, Dict, Any
from . import readers

class LLMTextSplitter:
    """
    A rule-based text splitter that recursively splits text to respect semantic
    boundaries and enriches chunks with metadata. It can process text directly or
    from various file types via its modular reader system.

    Attributes:
        max_chunk_chars (int): The target maximum number of characters for a single chunk.
        overlap_chars (int): The number of characters to overlap between chunks.
    """

    def __init__(self, max_chunk_chars: int = 2000, overlap_chars: int = 100):
        if not isinstance(max_chunk_chars, int) or max_chunk_chars <= 0:
            raise ValueError("max_chunk_chars must be a positive integer.")
        if not isinstance(overlap_chars, int) or overlap_chars < 0:
            raise ValueError("overlap_chars must be a non-negative integer.")
        if overlap_chars >= max_chunk_chars:
            raise ValueError("overlap_chars must be less than max_chunk_chars.")

        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars
        # More robust, ordered list of separators for recursive splitting
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_recursively(self, text: str, separators: List[str]) -> List[str]:
        """Recursively splits text by a list of separators."""
        if len(text) <= self.max_chunk_chars:
            return [text] if text.strip() else []

        if not separators:
            # If no more separators, perform a hard split
            return self._split_arbitrary_chunk(text)

        main_separator = separators[0]
        remaining_separators = separators[1:]
        
        # Split by the main separator. Filter out empty strings that can result from consecutive separators.
        parts = [p for p in text.split(main_separator) if p]
        
        final_chunks = []
        current_chunk_buffer = ""
        for part in parts:
            # If a single part is too long, recursively split it further
            if len(part) > self.max_chunk_chars:
                if current_chunk_buffer:
                    final_chunks.append(current_chunk_buffer.strip())
                    current_chunk_buffer = ""
                final_chunks.extend(self._split_recursively(part, remaining_separators))
                continue

            # Check if adding the next part exceeds the limit
            if len(current_chunk_buffer) + len(part) + len(main_separator) > self.max_chunk_chars:
                final_chunks.append(current_chunk_buffer.strip())
                current_chunk_buffer = part
            else:
                if current_chunk_buffer:
                    current_chunk_buffer += main_separator + part
                else:
                    current_chunk_buffer = part
        
        if current_chunk_buffer:
            final_chunks.append(current_chunk_buffer.strip())

        return [chunk for chunk in final_chunks if chunk]

    def _split_arbitrary_chunk(self, text: str) -> List[str]:
        """Fallback for hard character splitting with overlap."""
        if len(text) <= self.max_chunk_chars:
            return [text]
        
        chunks = []
        step = self.max_chunk_chars - self.overlap_chars
        for i in range(0, len(text), step):
            chunks.append(text[i : i + self.max_chunk_chars])
        return chunks

    def split_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Splits a text string into chunks and attaches metadata.

        Args:
            text (str): The input text to split.
            base_metadata (Dict[str, Any], optional): Initial metadata for all chunks.

        Returns:
            A list of dictionaries, where each dict has 'content' and 'metadata'.
        """
        if not isinstance(text, str):
            raise TypeError("Input 'text' must be a string.")
        
        if not text.strip():
            return []
        
        if base_metadata is None:
            base_metadata = {}

        string_chunks = self._split_recursively(text, self.separators)

        final_chunks = []
        for i, chunk_content in enumerate(string_chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_index"] = i
            final_chunks.append({"content": chunk_content, "metadata": chunk_metadata})
            
        return final_chunks

    def split_file(self, file_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Reads a supported file, extracts its text, and splits it into chunks with metadata.

        Args:
            file_path (str): The path to the file (.txt, .md, .pdf, .docx, .html).
            **kwargs: Additional arguments for the file reader (e.g., file_type, encoding).

        Returns:
            A list of chunk dictionaries with 'content' and 'metadata'.
        """
        document = readers.read_file(file_path, **kwargs)
        return self.split_text(document["content"], base_metadata=document["metadata"])