"""
Semantic Copycat Minner (CopycatM)

A semantic analysis tool for detecting AI-generated code derived from copyrighted sources.
"""

__version__ = "1.0.1"
__author__ = "Oscar Valenzuela B."
__email__ = "oscar.valenzuela.b@gmail.com"

from .core.analyzer import CopycatAnalyzer
from .core.config import AnalysisConfig
from .core.exceptions import (
    CopycatError,
    UnsupportedLanguageError,
    ParseError,
    AnalysisError,
    ConfigurationError,
)

__all__ = [
    "CopycatAnalyzer",
    "AnalysisConfig",
    "CopycatError",
    "UnsupportedLanguageError",
    "ParseError",
    "AnalysisError",
    "ConfigurationError",
] 