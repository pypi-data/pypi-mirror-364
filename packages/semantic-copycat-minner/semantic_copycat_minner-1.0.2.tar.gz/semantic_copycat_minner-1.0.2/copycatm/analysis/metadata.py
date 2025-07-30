"""
File metadata extraction for CopycatM.
"""

import os
import hashlib
import time
from pathlib import Path
from typing import Dict, Any

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


class MetadataExtractor:
    """Extract file metadata for analysis."""
    
    def __init__(self):
        if MAGIC_AVAILABLE:
            self.mime = magic.Magic(mime=True)
        else:
            self.mime = None
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a file."""
        path = Path(file_path)
        
        # Basic file info
        stat = path.stat()
        
        # Read file content for checksums
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Determine language from extension
        language = self._detect_language(path.suffix)
        
        # Get MIME type
        if self.mime:
            try:
                mime_type = self.mime.from_file(file_path)
            except Exception:
                mime_type = f"text/x-{language}"
        else:
            mime_type = f"text/x-{language}"
        
        # Calculate checksums
        sha256_hash = hashlib.sha256(content).hexdigest()
        md5_hash = hashlib.md5(content).hexdigest()
        
        # Count lines
        line_count = len(content.decode('utf-8', errors='ignore').splitlines())
        
        return {
            "file_name": path.name,
            "relative_path": str(path),
            "absolute_path": str(path.absolute()),
            "file_size": stat.st_size,
            "content_checksum": f"sha256:{sha256_hash}",
            "file_hash": f"md5:{md5_hash}",
            "mime_type": mime_type,
            "language": language,
            "encoding": "utf-8",
            "line_count": line_count,
            "is_source_code": self._is_source_code(language),
            "analysis_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            # Python
            ".py": "python",
            ".pyx": "python",
            ".pyi": "python",
            
            # JavaScript/TypeScript
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            
            # Java
            ".java": "java",
            
            # C/C++
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            
            # Go
            ".go": "go",
            
            # Rust
            ".rs": "rust",
        }
        
        return language_map.get(extension.lower(), "unknown")
    
    def _is_source_code(self, language: str) -> bool:
        """Check if the detected language is a supported source code language."""
        supported_languages = {
            "python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"
        }
        return language in supported_languages 