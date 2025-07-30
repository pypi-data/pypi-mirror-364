"""
Language-specific configurations for CopycatM.
"""

from typing import Dict, Any


def get_language_config(language: str) -> Dict[str, Any]:
    """Get configuration for a specific language."""
    configs = {
        "python": {
            "extensions": [".py", ".pyx", ".pyi"],
            "mime_type": "text/x-python",
            "parser": "tree_sitter_python",
            "fallback_parser": "ast",
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "def", "class", "if", "else", "elif", "for", "while", "try", "except",
                "finally", "with", "import", "from", "as", "return", "yield", "lambda"
            ],
            "operators": [
                "+", "-", "*", "/", "//", "%", "**", "==", "!=", "<", ">", "<=", ">=",
                "and", "or", "not", "in", "is", "&", "|", "^", "~", "<<", ">>"
            ]
        },
        "javascript": {
            "extensions": [".js", ".jsx"],
            "mime_type": "text/javascript",
            "parser": "tree_sitter_javascript",
            "fallback_parser": "esprima",
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "function", "var", "let", "const", "if", "else", "for", "while", "do",
                "switch", "case", "default", "try", "catch", "finally", "throw", "return",
                "class", "extends", "super", "new", "delete", "typeof", "instanceof"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "**", "==", "===", "!=", "!==", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", ">>>"
            ]
        },
        "typescript": {
            "extensions": [".ts", ".tsx"],
            "mime_type": "text/typescript",
            "parser": "tree_sitter_typescript",
            "fallback_parser": "esprima",
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "function", "var", "let", "const", "if", "else", "for", "while", "do",
                "switch", "case", "default", "try", "catch", "finally", "throw", "return",
                "class", "extends", "super", "new", "delete", "typeof", "instanceof",
                "interface", "type", "enum", "namespace", "module", "export", "import"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "**", "==", "===", "!=", "!==", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", ">>>"
            ]
        },
        "java": {
            "extensions": [".java"],
            "mime_type": "text/x-java-source",
            "parser": "tree_sitter_java",
            "fallback_parser": "javalang",
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "public", "private", "protected", "static", "final", "abstract", "class",
                "interface", "extends", "implements", "if", "else", "for", "while", "do",
                "switch", "case", "default", "try", "catch", "finally", "throw", "return",
                "new", "this", "super", "import", "package"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", ">>>"
            ]
        },
        "c": {
            "extensions": [".c", ".h"],
            "mime_type": "text/x-csrc",
            "parser": "tree_sitter_c",
            "fallback_parser": "pycparser",
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "auto", "break", "case", "char", "const", "continue", "default", "do",
                "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
                "long", "register", "return", "short", "signed", "sizeof", "static",
                "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"
            ]
        },
        "cpp": {
            "extensions": [".cpp", ".cc", ".cxx", ".hpp"],
            "mime_type": "text/x-c++src",
            "parser": "tree_sitter_cpp",
            "fallback_parser": "pycparser",
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "auto", "break", "case", "char", "const", "continue", "default", "do",
                "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
                "long", "register", "return", "short", "signed", "sizeof", "static",
                "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
                "class", "namespace", "template", "typename", "virtual", "public", "private",
                "protected", "friend", "inline", "explicit", "mutable", "operator", "new", "delete"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", "::", "->", "."
            ]
        },
        "go": {
            "extensions": [".go"],
            "mime_type": "text/x-go",
            "parser": "tree_sitter_go",
            "fallback_parser": None,
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "break", "case", "chan", "const", "continue", "default", "defer", "else",
                "fallthrough", "for", "func", "go", "goto", "if", "import", "interface",
                "map", "package", "range", "return", "select", "struct", "switch", "type", "var"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>", "&^"
            ]
        },
        "rust": {
            "extensions": [".rs"],
            "mime_type": "text/x-rust",
            "parser": "tree_sitter_rust",
            "fallback_parser": None,
            "complexity_threshold": 3,
            "min_lines": 20,
            "keywords": [
                "as", "break", "const", "continue", "crate", "else", "enum", "extern",
                "false", "fn", "for", "if", "impl", "in", "let", "loop", "match", "mod",
                "move", "mut", "pub", "ref", "return", "self", "Self", "static", "struct",
                "super", "trait", "true", "type", "unsafe", "use", "where", "while"
            ],
            "operators": [
                "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                "&&", "||", "!", "&", "|", "^", "~", "<<", ">>"
            ]
        }
    }
    
    return configs.get(language, {})


def get_supported_languages() -> list[str]:
    """Get list of all supported languages."""
    return [
        "python", "javascript", "typescript", "java", "c", "cpp", "go", "rust"
    ]


def get_language_extensions() -> Dict[str, list[str]]:
    """Get file extensions for each supported language."""
    extensions = {}
    for language in get_supported_languages():
        config = get_language_config(language)
        extensions[language] = config.get("extensions", [])
    return extensions 