"""
Tests for the document parser module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.parser import DocumentParser, ParseResult, parse_document


class TestDocumentParser:
    """Test cases for DocumentParser class."""
    
    def test_init(self):
        """Test parser initialization."""
        parser = DocumentParser()
        assert parser.supported_extensions == [".pdf", ".docx", ".txt", ".html"]
        assert parser.max_file_size > 0
    
    def test_validate_file_success(self, sample_txt_file):
        """Test successful file validation."""
        parser = DocumentParser()
        result = parser._validate_file(sample_txt_file)
        assert result["valid"] is True
        assert result["error"] is None
    
    def test_validate_file_not_exists(self, temp_dir):
        """Test validation of non-existent file."""
        parser = DocumentParser()
        non_existent = temp_dir / "nonexistent.pdf"
        result = parser._validate_file(non_existent)
        assert result["valid"] is False
        assert "does not exist" in result["error"]
    
    def test_validate_file_unsupported_extension(self, temp_dir):
        """Test validation of unsupported file type."""
        parser = DocumentParser()
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("test content")
        
        result = parser._validate_file(unsupported_file)
        assert result["valid"] is False
        assert "Unsupported file type" in result["error"]
    
    def test_validate_file_empty(self, temp_dir):
        """Test validation of empty file."""
        parser = DocumentParser()
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()
        
        result = parser._validate_file(empty_file)
        assert result["valid"] is False
        assert "empty" in result["error"]
    
    def test_generate_doc_id(self, sample_txt_file):
        """Test document ID generation."""
        parser = DocumentParser()
        doc_id1 = parser._generate_doc_id(sample_txt_file)
        doc_id2 = parser._generate_doc_id(sample_txt_file)
        
        assert doc_id1 == doc_id2  # Same file should generate same ID
        assert len(doc_id1) == 32  # Should be 32 characters
        assert doc_id1.isalnum()  # Should be alphanumeric
    
    def test_get_file_metadata(self, sample_txt_file):
        """Test file metadata extraction."""
        parser = DocumentParser()
        metadata = parser._get_file_metadata(sample_txt_file)
        
        assert metadata["filename"] == sample_txt_file.name
        assert metadata["file_path"] == str(sample_txt_file)
        assert metadata["file_size"] > 0
        assert metadata["file_type"] == ".txt"
        assert "created_time" in metadata
        assert "modified_time" in metadata
    
    def test_parse_txt_file(self, sample_txt_file):
        """Test parsing text file."""
        parser = DocumentParser()
        text = parser._parse_txt(sample_txt_file)
        
        assert "CONFIDENTIALITY AGREEMENT" in text
        assert "GOVERNING LAW" in text
        assert len(text) > 0
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        parser = DocumentParser()
        
        # Test with messy text
        messy_text = "  Line 1  \n\n\n  Line 2  \n\n\n\n  Line 3  "
        cleaned = parser._clean_text(messy_text)
        
        # Updated expected output with single line breaks
        assert cleaned == "Line 1\nLine 2\nLine 3"
        assert not cleaned.startswith(" ")
        assert not cleaned.endswith(" ")
    
    def test_parse_file_success(self, sample_txt_file):
        """Test successful file parsing."""
        parser = DocumentParser()
        result = parser.parse_file(str(sample_txt_file))
        
        assert isinstance(result, ParseResult)
        assert result.success is True
        assert len(result.text) > 0
        assert result.doc_id
        assert result.metadata["filename"] == sample_txt_file.name
        assert result.processing_time > 0
        assert result.error_message is None
    
    def test_parse_file_invalid(self, temp_dir):
        """Test parsing invalid file."""
        parser = DocumentParser()
        invalid_file = temp_dir / "nonexistent.txt"
        result = parser.parse_file(str(invalid_file))
        
        assert isinstance(result, ParseResult)
        assert result.success is False
        assert result.text == ""
        assert result.error_message is not None
        assert result.processing_time > 0
    
    @patch('src.core.parser.fitz')
    def test_parse_pdf_success(self, mock_fitz, temp_dir):
        """Test PDF parsing with mocked PyMuPDF."""
        # Mock PyMuPDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample PDF content"
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz.open.return_value = mock_doc
        
        parser = DocumentParser()
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4")  # Dummy PDF
        
        text = parser._parse_pdf(pdf_file)
        assert text == "Sample PDF content"
        mock_fitz.open.assert_called_once()
        mock_doc.close.assert_called_once()
    
    @patch('src.core.parser.docx')
    def test_parse_docx_success(self, mock_docx, temp_dir):
        """Test DOCX parsing with mocked python-docx."""
        # Mock python-docx
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Sample DOCX content"
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        mock_docx.Document.return_value = mock_doc
        
        parser = DocumentParser()
        docx_file = temp_dir / "test.docx"
        docx_file.write_bytes(b"PK")  # Dummy DOCX
        
        text = parser._parse_docx(docx_file)
        assert text == "Sample DOCX content"
        mock_docx.Document.assert_called_once()
    
    def test_parse_html_file(self, temp_dir):
        """Test HTML file parsing."""
        parser = DocumentParser()
        html_file = temp_dir / "test.html"
        html_content = """
        <html>
        <head><title>Test</title></head>
        <body>
            <h1>Contract Title</h1>
            <p>This is a test contract.</p>
            <script>alert('test');</script>
        </body>
        </html>
        """
        html_file.write_text(html_content)
        
        text = parser._parse_html(html_file)
        assert "Contract Title" in text
        assert "test contract" in text
        assert "alert" not in text  # Script should be removed


class TestParseDocument:
    """Test cases for the parse_document convenience function."""
    
    def test_parse_document_function(self, sample_txt_file):
        """Test the parse_document convenience function."""
        result = parse_document(str(sample_txt_file))
        
        assert isinstance(result, ParseResult)
        assert result.success is True
        assert len(result.text) > 0


class TestParseResult:
    """Test cases for ParseResult dataclass."""
    
    def test_parse_result_creation(self):
        """Test ParseResult creation."""
        result = ParseResult(
            success=True,
            text="Sample text",
            doc_id="test123",
            metadata={"test": "value"},
            processing_time=1.0
        )
        
        assert result.success is True
        assert result.text == "Sample text"
        assert result.doc_id == "test123"
        assert result.metadata == {"test": "value"}
        assert result.processing_time == 1.0
        assert result.error_message is None  # Default value
    
    def test_parse_result_with_error(self):
        """Test ParseResult with error."""
        result = ParseResult(
            success=False,
            text="",
            doc_id="",
            metadata={},
            error_message="Test error",
            processing_time=0.5
        )
        
        assert result.success is False
        assert result.error_message == "Test error"
