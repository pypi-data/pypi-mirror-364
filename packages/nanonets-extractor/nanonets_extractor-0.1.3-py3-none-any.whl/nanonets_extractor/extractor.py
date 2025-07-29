"""
Main DocumentExtractor class providing unified interface for document extraction.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .exceptions import (
    ExtractionError, ConfigurationError, UnsupportedFileError, APIError, ModelError
)
from .utils import (
    OutputType, ProcessingMode, FileType, validate_output_type, 
    validate_processing_mode, detect_file_type, get_api_key, format_specified_fields
)
from .processors.cloud_processor import CloudProcessor
from .processors import CPUProcessor, GPUProcessor


class DocumentExtractor:
    """
    Main class for document extraction with support for cloud, CPU, and GPU processing.
    
    Provides a unified interface regardless of the processing mode chosen.
    """
    
    def __init__(
        self,
        mode: str = "cloud",
        api_key: Optional[str] = None,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the DocumentExtractor.
        
        Args:
            mode: Processing mode ("cloud", "cpu", or "gpu")
            api_key: API key for cloud processing (required for cloud mode)
            model_path: Path to custom models for local processing
            device: Device specification for GPU processing (e.g., "cuda:0")
            **kwargs: Additional arguments passed to the processor
        """
        self.mode = validate_processing_mode(mode)
        self.api_key = api_key
        self.model_path = model_path
        self.device = device
        self.kwargs = kwargs
        
        # Initialize the appropriate processor
        self._processor = self._initialize_processor()
    
    def _initialize_processor(self):
        """Initialize the appropriate processor based on mode."""
        if self.mode == ProcessingMode.CLOUD:
            if not self.api_key:
                self.api_key = get_api_key()
            if not self.api_key:
                raise ConfigurationError(
                    "API key is required for cloud mode. "
                    "Set NANONETS_API_KEY environment variable or pass api_key parameter. "
                    "Get your FREE API key from: https://app.nanonets.com/#/keys"
                )
            return CloudProcessor(api_key=self.api_key, **self.kwargs)
        
        elif self.mode == ProcessingMode.CPU:
            if CPUProcessor is None:
                raise ConfigurationError(
                    "CPU processing dependencies not available. "
                    "Install with: pip install nanonets-extractor[cpu] or pip install easyocr pytesseract"
                )
            return CPUProcessor(model_path=self.model_path, **self.kwargs)
        
        elif self.mode == ProcessingMode.GPU:
            if GPUProcessor is None:
                raise ConfigurationError(
                    "GPU processing dependencies not available. "
                    "Install with: pip install nanonets-extractor[gpu] or pip install torch torchvision transformers"
                )
            return GPUProcessor(
                model_path=self.model_path, 
                device=self.device, 
                **self.kwargs
            )
        
        else:
            raise ConfigurationError(f"Unsupported processing mode: {self.mode}")
    
    def extract(
        self,
        file_path: str,
        output_type: str = "flat-json",
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract data from a document.
        
        Args:
            file_path: Path to the document file
            output_type: Type of output ("markdown", "flat-json", "specified-fields", "specified-json")
            specified_fields: List of field names to extract (for "specified-fields" output)
            json_schema: Custom JSON schema (for "specified-json" output)
            
        Returns:
            Dictionary containing extracted data
            
        Raises:
            ExtractionError: If extraction fails
            UnsupportedFileError: If file type is not supported
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        output_type_enum = validate_output_type(output_type)
        
        # Detect file type
        try:
            file_type = detect_file_type(file_path)
        except UnsupportedFileError as e:
            raise UnsupportedFileError(
                f"Unsupported file type for {file_path}. "
                f"Supported types: PDF, images (PNG, JPG, TIFF, BMP), "
                f"documents (DOCX, DOC), spreadsheets (XLSX, XLS, CSV), "
                f"text files (TXT, RTF). Error: {e}"
            )
        
        # Prepare extraction parameters
        extraction_params = {
            "file_path": file_path,
            "file_type": file_type,
            "output_type": output_type_enum,
        }
        
        # Add mode-specific parameters
        if output_type_enum == OutputType.SPECIFIED_FIELDS:
            if not specified_fields:
                raise ValueError("specified_fields is required for 'specified-fields' output type")
            extraction_params["specified_fields"] = specified_fields
        
        elif output_type_enum == OutputType.SPECIFIED_JSON:
            if not json_schema:
                raise ValueError("json_schema is required for 'specified-json' output type")
            extraction_params["json_schema"] = json_schema
        
        # Perform extraction
        try:
            result = self._processor.extract(**extraction_params)
            return result
        except Exception as e:
            if isinstance(e, (ExtractionError, APIError, ModelError)):
                raise
            else:
                raise ExtractionError(f"Extraction failed: {str(e)}")
    
    def extract_batch(
        self,
        file_paths: List[str],
        output_type: str = "flat-json",
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract data from multiple documents.
        
        Args:
            file_paths: List of file paths to process
            output_type: Type of output
            specified_fields: List of field names to extract
            json_schema: Custom JSON schema
            
        Returns:
            Dictionary mapping file paths to extraction results
        """
        results = {}
        
        for file_path in file_paths:
            try:
                result = self.extract(
                    file_path=file_path,
                    output_type=output_type,
                    specified_fields=specified_fields,
                    json_schema=json_schema
                )
                results[file_path] = result
            except Exception as e:
                results[file_path] = {"error": str(e)}
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return [
            ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif",
            ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".rtf"
        ]
    
    def get_processing_info(self) -> Dict[str, Any]:
        """Get information about the current processing setup."""
        info = {
            "mode": self.mode.value,
            "supported_formats": self.get_supported_formats(),
            "output_types": [ot.value for ot in OutputType],
        }
        
        if self.mode == ProcessingMode.CLOUD:
            info["api_key_configured"] = bool(self.api_key)
        elif self.mode == ProcessingMode.GPU:
            info["device"] = self.device or "auto"
        
        return info 