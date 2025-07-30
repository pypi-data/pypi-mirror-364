"""
Core analysis components for CopycatM.
"""

from .analyzer import CopycatAnalyzer
from .config import AnalysisConfig
from .exceptions import (
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