"""
Utility classes and enums for the Nanonets Document Extractor package.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path


class OutputType(Enum):
    """Supported output types for document extraction."""
    MARKDOWN = "markdown"
    FLAT_JSON = "flat-json"
    SPECIFIED_FIELDS = "specified-fields"
    SPECIFIED_JSON = "specified-json"


class ProcessingMode(Enum):
    """Supported processing modes."""
    CLOUD = "cloud"
    CPU = "cpu"
    GPU = "gpu"


class FileType(Enum):
    """Supported file types."""
    PDF = "pdf"
    IMAGE = "image"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    TEXT = "text"


class ConfigManager:
    """Manages configuration for the document extractor."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".nanonets"
        self.config_file = self.config_dir / "config.json"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)


def detect_file_type(file_path: str) -> FileType:
    """Detect the type of file based on extension."""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return FileType.PDF
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
        return FileType.IMAGE
    elif ext in ['.docx', '.doc']:
        return FileType.DOCUMENT
    elif ext in ['.xlsx', '.xls', '.csv']:
        return FileType.SPREADSHEET
    elif ext in ['.txt', '.rtf']:
        return FileType.TEXT
    else:
        raise UnsupportedFileError(f"Unsupported file type: {ext}")


def validate_output_type(output_type: str) -> OutputType:
    """Validate and return output type enum."""
    try:
        return OutputType(output_type)
    except ValueError:
        raise ValueError(f"Invalid output type: {output_type}. "
                        f"Supported types: {[t.value for t in OutputType]}")


def validate_processing_mode(mode: str) -> ProcessingMode:
    """Validate and return processing mode enum."""
    try:
        return ProcessingMode(mode)
    except ValueError:
        raise ValueError(f"Invalid processing mode: {mode}. "
                        f"Supported modes: {[m.value for m in ProcessingMode]}")


def get_api_key() -> Optional[str]:
    """Get API key from environment variable or config file."""
    # Check environment variable first
    api_key = os.getenv("NANONETS_API_KEY")
    if api_key:
        return api_key
    
    # Check config file
    config = ConfigManager()
    return config.get("api_key")


def format_specified_fields(fields: List[str]) -> str:
    """Format specified fields list as comma-separated string."""
    if not fields:
        return ""
    return ",".join(fields)


def parse_specified_fields(fields_str: str) -> List[str]:
    """Parse comma-separated fields string to list."""
    if not fields_str:
        return []
    return [field.strip() for field in fields_str.split(",") if field.strip()] 