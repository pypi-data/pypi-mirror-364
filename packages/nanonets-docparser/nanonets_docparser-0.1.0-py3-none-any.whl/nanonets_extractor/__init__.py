"""
Nanonets Document Extractor

A unified Python library for extracting data from any type of document
with support for local CPU, GPU, and cloud processing.
"""

from .extractor import DocumentExtractor
from .exceptions import ExtractionError, ConfigurationError, UnsupportedFileError
from .utils import OutputType, ProcessingMode

__version__ = "0.1.0"
__author__ = "Nanonets"
__email__ = "support@nanonets.com"

__all__ = [
    "DocumentExtractor",
    "ExtractionError", 
    "ConfigurationError",
    "UnsupportedFileError",
    "OutputType",
    "ProcessingMode",
] 