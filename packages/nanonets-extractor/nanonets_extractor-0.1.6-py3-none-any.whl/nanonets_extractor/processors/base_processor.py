"""
Base processor class defining the interface for all document processors.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ..utils import OutputType, FileType


class BaseProcessor(ABC):
    """
    Abstract base class for document processors.
    
    All processors (cloud, CPU, GPU) must implement this interface.
    """
    
    def __init__(self, **kwargs):
        """Initialize the processor with configuration."""
        self.config = kwargs
    
    @abstractmethod
    def extract(
        self,
        file_path: str,
        file_type: FileType,
        output_type: OutputType,
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract data from a document.
        
        Args:
            file_path: Path to the document file
            file_type: Type of the file
            output_type: Desired output format
            specified_fields: List of fields to extract (for specified-fields output)
            json_schema: Custom JSON schema (for specified-json output)
            
        Returns:
            Dictionary containing extracted data
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this processor is available and properly configured.
        
        Returns:
            True if the processor can be used
        """
        pass
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get information about what this processor can do.
        
        Returns:
            Dictionary with capability information
        """
        return {
            "processor_type": self.__class__.__name__,
            "available": self.is_available(),
        } 