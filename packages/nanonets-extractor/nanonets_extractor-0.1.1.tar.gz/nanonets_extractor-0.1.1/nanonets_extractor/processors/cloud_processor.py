"""
Cloud processor using Nanonets API for document extraction.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base_processor import BaseProcessor
from ..utils import OutputType, FileType, format_specified_fields
from ..exceptions import APIError, ExtractionError


class CloudProcessor(BaseProcessor):
    """
    Processor that uses Nanonets cloud API for document extraction.
    """
    
    def __init__(self, api_key: str, base_url: str = None, **kwargs):
        """
        Initialize the cloud processor.
        
        Args:
            api_key: Nanonets API key
            base_url: Base URL for the API (deprecated, always uses extraction-api.nanonets.com)
            **kwargs: Additional configuration
        """
        super().__init__(**kwargs)
        self.api_key = api_key
        self.base_url = "https://extraction-api.nanonets.com"
        self.session = requests.Session()
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'Nanonets-Document-Extractor/0.1.0',
            'Authorization': f'Bearer {self.api_key}'
        })
    
    def is_available(self) -> bool:
        """Check if cloud processor is available."""
        return bool(self.api_key)
    
    def extract(
        self,
        file_path: str,
        file_type: FileType,
        output_type: OutputType,
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract data using cloud API.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the file
            output_type: Desired output format
            specified_fields: List of fields to extract
            json_schema: Custom JSON schema
            
        Returns:
            Dictionary containing extracted data
        """
        if not self.is_available():
            raise ExtractionError("Cloud processor not available - API key required")
        
        # Prepare the request
        url = "https://extraction-api.nanonets.com/extract"
        
        # Prepare files
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/octet-stream')}
        
        # Prepare data
        data = {'output_type': output_type.value}
        
        # Add mode-specific parameters
        if output_type == OutputType.SPECIFIED_FIELDS:
            if specified_fields:
                data['specified_fields'] = format_specified_fields(specified_fields)
        
        elif output_type == OutputType.SPECIFIED_JSON:
            if json_schema:
                data['json_schema'] = json.dumps(json_schema)
        
        # Make the request
        try:
            response = self.session.post(url, files=files, data=data, timeout=300)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, dict):
                return result
            else:
                return {"extracted_data": result}
                
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('detail', str(e))
                except:
                    error_message = f"HTTP {e.response.status_code}: {e.response.text}"
            else:
                error_message = str(e)
            
            raise APIError(f"Cloud API request failed: {error_message}")
        
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response from API: {e}")
        
        except Exception as e:
            raise ExtractionError(f"Extraction failed: {str(e)}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get cloud processor capabilities."""
        capabilities = super().get_capabilities()
        capabilities.update({
            "api_configured": bool(self.api_key),
            "base_url": self.base_url,
            "supports_all_formats": True,
            "high_accuracy": True,
            "requires_internet": True,
        })
        return capabilities 