import pytest
import os
from unittest.mock import patch, MagicMock
from llm_text_splitter import LLMTextSplitter

# Fixture for a standard splitter instance
@pytest.fixture
def splitter():
    return LLMTextSplitter(max_chunk_chars=80, overlap_chars=20)

# Fixture to create a temporary text file
@pytest.fixture
def sample_text_file(tmp_path):
    content = "This is the first sentence.\nThis is the second sentence.\n\nThis is a new paragraph that is quite a bit longer."
    file_path = tmp_path / "sample.txt"
    file_path.write_text(content, encoding="utf-8")
    return file_path

# --- Initialization Tests ---

def test_initialization():
    """Tests basic initialization and parameter validation."""
    s = LLMTextSplitter(max_chunk_chars=100, overlap_chars=10)
    assert s.max_chunk_chars == 100
    assert s.overlap_chars == 10

    with pytest.raises(ValueError, match="max_chunk_chars must be a positive integer."):
        LLMTextSplitter(max_chunk_chars=0)
    with pytest.raises(ValueError, match="overlap_chars must be a non-negative integer."):
        LLMTextSplitter(overlap_chars=-1)
    with pytest.raises(ValueError, match="overlap_chars must be less than max_chunk_chars"):
        LLMTextSplitter(max_chunk_chars=10, overlap_chars=10)

# --- split_text Method Tests ---

def test_split_text_empty_and_non_string_input(splitter):
    """Tests empty, whitespace, and invalid type inputs."""
    assert splitter.split_text("") == []
    assert splitter.split_text("   \n\t") == []
    with pytest.raises(TypeError, match="Input 'text' must be a string."):
        splitter.split_text(12345)

def test_split_text_short_text(splitter):
    """Tests text that is smaller than the chunk size."""
    text = "This is a short text."
    chunks = splitter.split_text(text)
    
    assert len(chunks) == 1
    assert chunks[0]['content'] == text
    assert chunks[0]['metadata']['chunk_index'] == 0

def test_recursive_splitting_logic(splitter):
    """Tests the recursive splitting on multiple separators."""
    # This text will be split by \n\n first, then by \n, then by ". "
    text = "First paragraph.\nIt has two lines.\n\nSecond paragraph. It's longer and will also be split. The goal is to test separators."
    chunks = splitter.split_text(text)

    # Expected chunks based on recursive logic (max_chunk_chars=80):
    # 1. "First paragraph.\nIt has two lines." (len=38, fits)
    # 2. "Second paragraph. It's longer and will also be split." (len=55, fits)
    # 3. "The goal is to test separators." (len=32, fits)
    
    assert len(chunks) == 3
    assert chunks[0]['content'] == "First paragraph.\nIt has two lines."
    assert chunks[1]['content'] == "Second paragraph. It's longer and will also be split."
    assert chunks[2]['content'] == "The goal is to test separators."

def test_arbitrary_splitting_with_overlap():
    """Tests the final fallback to arbitrary character splitting."""
    splitter = LLMTextSplitter(max_chunk_chars=20, overlap_chars=5)
    text = "Thisisonesinglelongwordthatcannotbesplitbyanymeaningfulseparator." # len=68
    chunks = splitter.split_text(text)

    # Expected logic: step = 20-5=15
    # chunk 1: text[0:20]
    # chunk 2: text[15:35]
    # chunk 3: text[30:50]
    # chunk 4: text[45:65]
    # chunk 5: text[60:68]
    assert len(chunks) == 5
    assert chunks[0]['content'] == "Thisisonesinglelongw"
    assert chunks[1]['content'] == "elongwordthatcannotb"
    assert chunks[4]['content'] == "eparator."
    assert chunks[0]['metadata']['chunk_index'] == 0
    assert chunks[4]['metadata']['chunk_index'] == 4

# --- split_file Method Tests ---

def test_split_file_txt_and_metadata(splitter, sample_text_file):
    """Tests splitting a .txt file and verifies the metadata output."""
    chunks = splitter.split_file(str(sample_text_file))
    
    # Expected chunks (max_chunk_chars=80):
    # 1. "This is the first sentence.\nThis is the second sentence." (len=54, fits)
    # 2. "This is a new paragraph that is quite a bit longer." (len=51, fits)
    assert len(chunks) == 2
    assert chunks[0]['content'] == "This is the first sentence.\nThis is the second sentence."
    assert chunks[1]['content'] == "This is a new paragraph that is quite a bit longer."

    # Verify metadata
    for i, chunk in enumerate(chunks):
        assert chunk['metadata']['source'] == "sample.txt"
        assert chunk['metadata']['path'] == str(sample_text_file)
        assert chunk['metadata']['file_type'] == 'txt'
        assert chunk['metadata']['chunk_index'] == i

def test_split_file_not_found(splitter):
    """Tests error handling for a non-existent file."""
    with pytest.raises(FileNotFoundError):
        splitter.split_file("non_existent_file.xyz")

def test_split_file_unsupported_type(splitter, tmp_path):
    """Tests error handling for an unsupported file extension."""
    file_path = tmp_path / "document.zip"
    file_path.touch()
    with pytest.raises(ValueError, match="Unsupported file type: 'zip'"):
        splitter.split_file(str(file_path))

# --- Mocked File Reader Tests ---

# Correct patch target is now in the `readers` module
@patch('llm_text_splitter.readers._read_pdf')
def test_split_file_pdf_mocked(mock_read_pdf, splitter, tmp_path):
    """Tests the dispatcher calls the correct PDF reader."""
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.touch()
    
    # Mock the return value of the reader function
    mock_read_pdf.return_value = "This is PDF content from page 1. And page 2."
    
    chunks = splitter.split_file(str(pdf_path))

    mock_read_pdf.assert_called_once_with(str(pdf_path), encoding='utf-8')
    assert len(chunks) == 1
    assert chunks[0]['content'] == "This is PDF content from page 1. And page 2."
    assert chunks[0]['metadata']['source'] == "dummy.pdf"
    assert chunks[0]['metadata']['file_type'] == 'pdf'

@patch('llm_text_splitter.readers._read_docx')
def test_split_file_docx_mocked(mock_read_docx, splitter, tmp_path):
    """Tests the dispatcher calls the correct DOCX reader."""
    docx_path = tmp_path / "dummy.docx"
    docx_path.touch()
    
    mock_read_docx.return_value = "This is DOCX content."
    
    chunks = splitter.split_file(str(docx_path))

    mock_read_docx.assert_called_once_with(str(docx_path), encoding='utf-8')
    assert len(chunks) == 1
    assert chunks[0]['content'] == "This is DOCX content."
    assert chunks[0]['metadata']['file_type'] == 'docx'

def test_reader_import_error(splitter, tmp_path):
    """
    Tests that a helpful ImportError is raised if an optional dependency is missing.
    """
    # Create a dummy file
    pdf_path = tmp_path / "real.pdf"
    pdf_path.touch()
    
    # Simulate `pypdf` not being installed by patching `sys.modules`
    with patch.dict('sys.modules', {'pypdf': None}):
        with pytest.raises(ImportError, match="PDF processing requires pypdf"):
            splitter.split_file(str(pdf_path))