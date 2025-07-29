"""
Unit tests for the Nanonets Document Extractor.
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from nanonets_extractor import DocumentExtractor
from nanonets_extractor.exceptions import (
    ExtractionError, ConfigurationError, UnsupportedFileError
)
from nanonets_extractor.utils import OutputType, ProcessingMode, FileType


class TestDocumentExtractor(unittest.TestCase):
    """Test cases for DocumentExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        
        # Create a test file
        with open(self.test_file, 'w') as f:
            f.write("Test document content\nInvoice #12345\nAmount: $100.00")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_cloud_mode(self):
        """Test initialization with cloud mode."""
        extractor = DocumentExtractor(mode="cloud", api_key="test_key")
        self.assertEqual(extractor.mode, ProcessingMode.CLOUD)
        self.assertEqual(extractor.api_key, "test_key")
    
    def test_initialization_cpu_mode(self):
        """Test initialization with CPU mode."""
        extractor = DocumentExtractor(mode="cpu")
        self.assertEqual(extractor.mode, ProcessingMode.CPU)
    
    def test_initialization_gpu_mode(self):
        """Test initialization with GPU mode."""
        extractor = DocumentExtractor(mode="gpu")
        self.assertEqual(extractor.mode, ProcessingMode.GPU)
    
    def test_invalid_mode(self):
        """Test initialization with invalid mode."""
        with self.assertRaises(ValueError):
            DocumentExtractor(mode="invalid")
    
    def test_cloud_mode_without_api_key(self):
        """Test cloud mode initialization without API key."""
        with self.assertRaises(ConfigurationError):
            DocumentExtractor(mode="cloud")
    
    def test_get_supported_formats(self):
        """Test getting supported file formats."""
        extractor = DocumentExtractor(mode="cpu")
        formats = extractor.get_supported_formats()
        
        expected_formats = [
            ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif",
            ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".rtf"
        ]
        
        for fmt in expected_formats:
            self.assertIn(fmt, formats)
    
    def test_get_processing_info(self):
        """Test getting processing information."""
        extractor = DocumentExtractor(mode="cpu")
        info = extractor.get_processing_info()
        
        self.assertEqual(info["mode"], "cpu")
        self.assertIn("supported_formats", info)
        self.assertIn("output_types", info)
    
    def test_file_not_found(self):
        """Test extraction with non-existent file."""
        extractor = DocumentExtractor(mode="cpu")
        
        with self.assertRaises(FileNotFoundError):
            extractor.extract("non_existent_file.pdf")
    
    def test_unsupported_file_type(self):
        """Test extraction with unsupported file type."""
        extractor = DocumentExtractor(mode="cpu")
        
        # Create a file with unsupported extension
        unsupported_file = os.path.join(self.temp_dir, "test.xyz")
        with open(unsupported_file, 'w') as f:
            f.write("test content")
        
        with self.assertRaises(UnsupportedFileError):
            extractor.extract(unsupported_file)
    
    @patch('nanonets_extractor.processors.cpu_processor.CPUProcessor')
    def test_cpu_extraction(self, mock_cpu_processor):
        """Test CPU extraction."""
        # Mock the CPU processor
        mock_processor = Mock()
        mock_processor.extract.return_value = {"text": "extracted content"}
        mock_cpu_processor.return_value = mock_processor
        
        extractor = DocumentExtractor(mode="cpu")
        result = extractor.extract(self.test_file, output_type="flat-json")
        
        self.assertEqual(result, {"text": "extracted content"})
        mock_processor.extract.assert_called_once()
    
    @patch('nanonets_extractor.processors.cloud_processor.CloudProcessor')
    def test_cloud_extraction(self, mock_cloud_processor):
        """Test cloud extraction."""
        # Mock the cloud processor
        mock_processor = Mock()
        mock_processor.extract.return_value = {"text": "cloud extracted content"}
        mock_cloud_processor.return_value = mock_processor
        
        extractor = DocumentExtractor(mode="cloud", api_key="test_key")
        result = extractor.extract(self.test_file, output_type="flat-json")
        
        self.assertEqual(result, {"text": "cloud extracted content"})
        mock_processor.extract.assert_called_once()
    
    def test_invalid_output_type(self):
        """Test extraction with invalid output type."""
        extractor = DocumentExtractor(mode="cpu")
        
        with self.assertRaises(ValueError):
            extractor.extract(self.test_file, output_type="invalid")
    
    def test_specified_fields_without_fields(self):
        """Test specified-fields output type without fields."""
        extractor = DocumentExtractor(mode="cpu")
        
        with self.assertRaises(ValueError):
            extractor.extract(self.test_file, output_type="specified-fields")
    
    def test_specified_json_without_schema(self):
        """Test specified-json output type without schema."""
        extractor = DocumentExtractor(mode="cpu")
        
        with self.assertRaises(ValueError):
            extractor.extract(self.test_file, output_type="specified-json")
    
    def test_batch_extraction(self):
        """Test batch extraction."""
        # Create multiple test files
        test_files = []
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"test_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(test_file)
        
        with patch('nanonets_extractor.processors.cpu_processor.CPUProcessor') as mock_cpu_processor:
            # Mock the CPU processor
            mock_processor = Mock()
            mock_processor.extract.return_value = {"text": "extracted content"}
            mock_cpu_processor.return_value = mock_processor
            
            extractor = DocumentExtractor(mode="cpu")
            results = extractor.extract_batch(test_files, output_type="flat-json")
            
            self.assertEqual(len(results), 3)
            for result in results.values():
                self.assertEqual(result, {"text": "extracted content"})


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_validate_output_type(self):
        """Test output type validation."""
        from nanonets_extractor.utils import validate_output_type
        
        # Valid types
        self.assertEqual(validate_output_type("markdown"), OutputType.MARKDOWN)
        self.assertEqual(validate_output_type("flat-json"), OutputType.FLAT_JSON)
        self.assertEqual(validate_output_type("specified-fields"), OutputType.SPECIFIED_FIELDS)
        self.assertEqual(validate_output_type("specified-json"), OutputType.SPECIFIED_JSON)
        
        # Invalid type
        with self.assertRaises(ValueError):
            validate_output_type("invalid")
    
    def test_validate_processing_mode(self):
        """Test processing mode validation."""
        from nanonets_extractor.utils import validate_processing_mode
        
        # Valid modes
        self.assertEqual(validate_processing_mode("cloud"), ProcessingMode.CLOUD)
        self.assertEqual(validate_processing_mode("cpu"), ProcessingMode.CPU)
        self.assertEqual(validate_processing_mode("gpu"), ProcessingMode.GPU)
        
        # Invalid mode
        with self.assertRaises(ValueError):
            validate_processing_mode("invalid")
    
    def test_detect_file_type(self):
        """Test file type detection."""
        from nanonets_extractor.utils import detect_file_type
        
        # Test different file types
        self.assertEqual(detect_file_type("test.pdf"), FileType.PDF)
        self.assertEqual(detect_file_type("test.png"), FileType.IMAGE)
        self.assertEqual(detect_file_type("test.jpg"), FileType.IMAGE)
        self.assertEqual(detect_file_type("test.docx"), FileType.DOCUMENT)
        self.assertEqual(detect_file_type("test.xlsx"), FileType.SPREADSHEET)
        self.assertEqual(detect_file_type("test.txt"), FileType.TEXT)
        
        # Unsupported type
        with self.assertRaises(UnsupportedFileError):
            detect_file_type("test.xyz")
    
    def test_format_specified_fields(self):
        """Test specified fields formatting."""
        from nanonets_extractor.utils import format_specified_fields
        
        fields = ["field1", "field2", "field3"]
        result = format_specified_fields(fields)
        self.assertEqual(result, "field1,field2,field3")
        
        # Empty list
        result = format_specified_fields([])
        self.assertEqual(result, "")
    
    def test_parse_specified_fields(self):
        """Test specified fields parsing."""
        from nanonets_extractor.utils import parse_specified_fields
        
        fields_str = "field1,field2,field3"
        result = parse_specified_fields(fields_str)
        self.assertEqual(result, ["field1", "field2", "field3"])
        
        # With spaces
        fields_str = "field1, field2 , field3"
        result = parse_specified_fields(fields_str)
        self.assertEqual(result, ["field1", "field2", "field3"])
        
        # Empty string
        result = parse_specified_fields("")
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main() 