"""
Custom exceptions for the Nanonets Document Extractor package.
"""


class ExtractionError(Exception):
    """Raised when document extraction fails."""
    pass


class ConfigurationError(Exception):
    """Raised when there's an issue with configuration or initialization."""
    pass


class UnsupportedFileError(Exception):
    """Raised when the file type is not supported."""
    pass


class APIError(Exception):
    """Raised when there's an issue with the cloud API."""
    pass


class ModelError(Exception):
    """Raised when there's an issue with local models."""
    pass 