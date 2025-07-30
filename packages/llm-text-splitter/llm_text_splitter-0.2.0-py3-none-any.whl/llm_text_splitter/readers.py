import os
from typing import Dict, Any

def read_file(file_path: str, file_type: str = None, encoding: str = "utf-8", **kwargs) -> Dict[str, Any]:
    """
    Detects file type and uses the appropriate reader to extract text and metadata.

    Args:
        file_path (str): Path to the file.
        file_type (str, optional): Explicitly specify file type. If None, it's inferred.
        encoding (str, optional): File encoding for text-based files.

    Returns:
        A dictionary with 'content' (the extracted text) and 'metadata' (source file info).
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")

    if file_type is None:
        _, ext = os.path.splitext(file_path)
        file_type = ext.lower().lstrip('.')

    metadata = {"source": os.path.basename(file_path), "path": file_path, "file_type": file_type}
    
    reader_map = {
        'pdf': _read_pdf,
        'docx': _read_docx,
        'html': _read_html,
        'htm': _read_html,
        'txt': _read_text,
        'md': _read_text,
        'py': _read_text,
        'json': _read_text,
        'csv': _read_text,
    }

    reader_func = reader_map.get(file_type)
    if reader_func is None:
        raise ValueError(f"Unsupported file type: '{file_type}'.")

    content = reader_func(file_path, encoding=encoding)
    
    return {"content": content, "metadata": metadata}

def _read_text(file_path: str, encoding: str) -> str:
    """Reads plain text files."""
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()

def _read_pdf(file_path: str, **kwargs) -> str:
    """Reads text from a PDF file."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError(
            "PDF processing requires pypdf. Please install it with: pip install 'llm-text-splitter[pdf]'"
        )
    
    reader = PdfReader(file_path)
    return "\n\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def _read_docx(file_path: str, **kwargs) -> str:
    """Reads text from a .docx file."""
    try:
        import docx
    except ImportError:
        raise ImportError(
            "DOCX processing requires python-docx. Please install it with: pip install 'llm-text-splitter[docx]'"
        )
    
    document = docx.Document(file_path)
    return "\n\n".join(para.text for para in document.paragraphs if para.text.strip())

def _read_html(file_path: str, encoding: str) -> str:
    """Reads and cleans text from an HTML file."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "HTML processing requires beautifulsoup4. Please install it with: pip install 'llm-text-splitter[html]'"
        )

    with open(file_path, "r", encoding=encoding) as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Get text and use a space as a separator to avoid mashing words together
    text = soup.get_text(separator=' ', strip=True)
    return text