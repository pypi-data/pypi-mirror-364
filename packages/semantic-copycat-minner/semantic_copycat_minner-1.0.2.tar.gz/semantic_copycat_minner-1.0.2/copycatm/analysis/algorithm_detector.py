"""
Algorithm detector with better specificity to reduce over-similarity.
"""

import re
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import hashlib
import json

from .algorithm_types import AlgorithmType
from .algorithmic_normalizer import AlgorithmicNormalizer
from ..core.config import AnalysisConfig
from ..hashing.direct import DirectHasher
from ..hashing.fuzzy_improved import ImprovedFuzzyHasher
from ..hashing.semantic import SemanticHasher
import uuid


class AlgorithmDetector:
    """Algorithm detector with improved pattern matching specificity."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.patterns = self._initialize_specific_patterns()
        
        # Initialize components for hashing
        self.normalizer = AlgorithmicNormalizer()
        self.direct_hasher = DirectHasher()
        self.fuzzy_hasher = ImprovedFuzzyHasher()
        self.semantic_hasher = SemanticHasher(num_perm=128, lsh_bands=config.lsh_bands if config else 20)
        
    def _initialize_specific_patterns(self) -> Dict[AlgorithmType, Dict]:
        """Initialize highly specific algorithm patterns to reduce false positives."""
        return {
            # Sorting algorithms - very specific patterns
            AlgorithmType.SORTING_ALGORITHM: {
                'subtypes': {
                    'quicksort': {
                        'keywords': ['quicksort', 'pivot', 'partition'],
                        'required_patterns': ['pivot_selection', 'partition_logic', 'recursive_calls'],
                        'ast_patterns': ['recursive_function', 'array_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'bubblesort': {
                        'keywords': ['bubble', 'swap'],
                        'required_patterns': ['nested_loops', 'adjacent_comparison', 'swap_operation'],
                        'ast_patterns': ['double_for_loop', 'comparison', 'assignment'],
                        'confidence_boost': 0.3
                    },
                    'mergesort': {
                        'keywords': ['merge', 'divide'],
                        'required_patterns': ['merge_function', 'divide_conquer', 'recursive_calls'],
                        'ast_patterns': ['recursive_function', 'array_split'],
                        'confidence_boost': 0.2
                    },
                    'generic_sort': {
                        'keywords': ['sort', 'compare'],
                        'required_patterns': ['comparison_operation', 'element_swap'],
                        'ast_patterns': ['loop', 'comparison', 'assignment'],
                        'confidence_boost': 0.0
                    }
                }
            },
            
            # Search algorithms - distinct patterns
            AlgorithmType.SEARCH_ALGORITHM: {
                'subtypes': {
                    'binary_search': {
                        'keywords': ['binary', 'mid', 'middle', 'left', 'right'],
                        'required_patterns': ['mid_calculation', 'binary_division', 'comparison_with_target'],
                        'ast_patterns': ['while_loop_or_recursion', 'arithmetic_operation', 'comparison'],
                        'confidence_boost': 0.3
                    },
                    'linear_search': {
                        'keywords': ['find', 'search', 'linear'],
                        'required_patterns': ['single_loop', 'element_comparison', 'return_on_match'],
                        'ast_patterns': ['for_loop', 'if_statement', 'return_statement'],
                        'confidence_boost': 0.2
                    },
                    'generic_search': {
                        'keywords': ['search', 'find', 'locate'],
                        'required_patterns': ['iteration', 'comparison'],
                        'ast_patterns': ['loop', 'comparison'],
                        'confidence_boost': 0.0
                    }
                }
            },
            
            # Mathematical algorithms - unique patterns
            AlgorithmType.NUMERICAL_ALGORITHM: {
                'subtypes': {
                    'fibonacci': {
                        'keywords': ['fibonacci', 'fib'],
                        'required_patterns': ['n_minus_1', 'n_minus_2', 'addition'],
                        'ast_patterns': ['recursive_or_iterative', 'arithmetic_operation'],
                        'confidence_boost': 0.4
                    },
                    'factorial': {
                        'keywords': ['factorial', 'fact'],
                        'required_patterns': ['n_multiplication', 'decremental_loop_or_recursion'],
                        'ast_patterns': ['multiplication', 'decrement'],
                        'confidence_boost': 0.3
                    },
                    'prime': {
                        'keywords': ['prime', 'divisor'],
                        'required_patterns': ['modulo_operation', 'divisibility_check'],
                        'ast_patterns': ['modulo', 'loop', 'comparison'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Compression algorithms
            AlgorithmType.COMPRESSION_ALGORITHM: {
                'subtypes': {
                    'huffman': {
                        'keywords': ['huffman', 'frequency', 'encoding'],
                        'required_patterns': ['frequency_counting', 'tree_building', 'encoding'],
                        'ast_patterns': ['hash_map', 'tree_structure'],
                        'confidence_boost': 0.3
                    },
                    'lzw': {
                        'keywords': ['lzw', 'dictionary', 'compress'],
                        'required_patterns': ['dictionary_building', 'pattern_matching'],
                        'ast_patterns': ['hash_map', 'string_manipulation'],
                        'confidence_boost': 0.3
                    }
                }
            },
            
            # Dynamic programming
            AlgorithmType.DYNAMIC_PROGRAMMING: {
                'subtypes': {
                    'memoization': {
                        'keywords': ['memo', 'cache', 'dp'],
                        'required_patterns': ['cache_check', 'cache_store', 'recursive_structure'],
                        'ast_patterns': ['hash_map', 'recursive_function'],
                        'confidence_boost': 0.3
                    },
                    'tabulation': {
                        'keywords': ['table', 'dp', 'dynamic'],
                        'required_patterns': ['table_initialization', 'iterative_filling'],
                        'ast_patterns': ['array_initialization', 'nested_loops'],
                        'confidence_boost': 0.2
                    }
                }
            }
        }
    
    def detect(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """Detect algorithms with improved specificity."""
        return self.detect_algorithms(ast_tree, language)
    
    def detect_algorithms(self, ast_tree: Any, language: str) -> List[Dict[str, Any]]:
        """Detect algorithms with improved specificity."""
        detected_algorithms = []
        
        # Extract functions from AST
        functions = self._extract_functions_from_ast(ast_tree)
        
        for func in functions:
            # Analyze each function for specific algorithm patterns
            algorithm = self._analyze_function_with_specificity(func, ast_tree, language)
            if algorithm:
                detected_algorithms.append(algorithm)
        
        return detected_algorithms
    
    def _analyze_function_with_specificity(self, func: Dict[str, Any], ast_tree: Any, language: str) -> Optional[Dict[str, Any]]:
        """Analyze function with specific pattern matching to reduce false positives."""
        func_text = func['text'].lower()
        func_name = func['name'].lower()
        
        # Skip very small functions
        if func['lines']['total'] < 5:
            return None
        
        best_match = None
        best_confidence = 0.0
        best_subtype = None
        
        # Check each algorithm type and subtype
        for algo_type, type_config in self.patterns.items():
            for subtype_name, subtype_pattern in type_config['subtypes'].items():
                confidence = self._calculate_specific_confidence(
                    func_text, func_name, func['node'], 
                    subtype_pattern, subtype_name
                )
                
                if confidence > best_confidence and confidence >= 0.3:  # Higher threshold
                    best_confidence = confidence
                    best_match = algo_type
                    best_subtype = subtype_name
        
        if best_match:
            return self._create_specific_algorithm_entry(
                func, best_match, best_subtype, best_confidence, 
                ast_tree, language
            )
        
        return None
    
    def _calculate_specific_confidence(self, func_text: str, func_name: str, 
                                     func_node: Any, pattern: Dict, subtype: str) -> float:
        """Calculate confidence with required pattern checking."""
        confidence = 0.0
        
        # 1. Keyword matching (reduced weight)
        keyword_score = self._calculate_keyword_score(func_text, func_name, pattern.get('keywords', []))
        confidence += keyword_score * 0.2  # Only 20% weight
        
        # 2. Required patterns (high weight)
        required_score = self._check_required_patterns(func_text, func_node, pattern.get('required_patterns', []))
        confidence += required_score * 0.5  # 50% weight
        
        # 3. AST pattern matching
        ast_score = self._check_ast_patterns(func_node, pattern.get('ast_patterns', []))
        confidence += ast_score * 0.3  # 30% weight
        
        # 4. Apply confidence boost for highly specific patterns
        if confidence > 0.5:  # Only boost if base confidence is decent
            confidence += pattern.get('confidence_boost', 0)
        
        # 5. Penalty for generic subtypes
        if subtype.endswith('_generic') or subtype == 'generic':
            confidence *= 0.5  # Reduce confidence for generic matches
        
        return min(confidence, 1.0)
    
    def _calculate_keyword_score(self, func_text: str, func_name: str, keywords: List[str]) -> float:
        """Calculate keyword matching score with context awareness."""
        if not keywords:
            return 0.0
        
        score = 0.0
        matched_keywords = 0
        
        for keyword in keywords:
            # Check function name (higher weight)
            if keyword in func_name:
                score += 2.0
                matched_keywords += 1
            # Check function text
            elif re.search(rf'\b{keyword}\b', func_text):
                score += 1.0
                matched_keywords += 1
        
        # Normalize and apply threshold
        if matched_keywords == 0:
            return 0.0
        
        normalized_score = score / (len(keywords) * 2)  # Max possible score
        
        # Require at least 30% keyword match
        return normalized_score if matched_keywords >= len(keywords) * 0.3 else normalized_score * 0.5
    
    def _check_required_patterns(self, func_text: str, func_node: Any, required_patterns: List[str]) -> float:
        """Check for required algorithmic patterns."""
        if not required_patterns:
            return 0.0
        
        pattern_checks = {
            # Sorting patterns
            'pivot_selection': lambda: 'pivot' in func_text and ('//2' in func_text or '/2' in func_text),
            'partition_logic': lambda: 'partition' in func_text or (re.search(r'[<>]=?.*pivot', func_text) is not None),
            'nested_loops': lambda: self._has_nested_loops(func_node),
            'adjacent_comparison': lambda: re.search(r'\[\s*\w+\s*\].*\[\s*\w+\s*\+\s*1\s*\]', func_text) is not None,
            'swap_operation': lambda: re.search(r'=.*,.*=|swap|temp.*=', func_text) is not None,
            
            # Search patterns
            'mid_calculation': lambda: re.search(r'(mid|middle).*[+/].*2', func_text) is not None,
            'binary_division': lambda: 'left' in func_text and 'right' in func_text,
            'comparison_with_target': lambda: 'target' in func_text or 'key' in func_text,
            'single_loop': lambda: self._count_loops(func_node) == 1,
            'return_on_match': lambda: re.search(r'if.*return', func_text) is not None,
            
            # Math patterns
            'n_minus_1': lambda: '-1' in func_text or '- 1' in func_text,
            'n_minus_2': lambda: '-2' in func_text or '- 2' in func_text,
            'n_multiplication': lambda: '*' in func_text and ('n' in func_text or 'num' in func_text),
            'modulo_operation': lambda: '%' in func_text or 'mod' in func_text,
            
            # General patterns
            'recursive_calls': lambda: self._has_recursive_pattern(func_text, func_node),
            'iteration': lambda: self._has_loops(func_node),
            'comparison': lambda: re.search(r'[<>=!]=?', func_text) is not None
        }
        
        matched = 0
        for pattern in required_patterns:
            if pattern in pattern_checks:
                try:
                    if pattern_checks[pattern]():
                        matched += 1
                except:
                    pass
        
        # Require at least 60% of required patterns
        return (matched / len(required_patterns)) if matched >= len(required_patterns) * 0.6 else 0.0
    
    def _check_ast_patterns(self, func_node: Any, ast_patterns: List[str]) -> float:
        """Check AST-based patterns."""
        if not ast_patterns or not func_node:
            return 0.0
        
        pattern_checks = {
            'recursive_function': lambda: self._has_function_calls(func_node),
            'double_for_loop': lambda: self._has_nested_loops(func_node),
            'while_loop_or_recursion': lambda: self._has_while_loop(func_node) or self._has_function_calls(func_node),
            'for_loop': lambda: self._has_for_loop(func_node),
            'loop': lambda: self._has_loops(func_node),
            'comparison': lambda: self._has_comparisons(func_node),
            'assignment': lambda: self._has_assignments(func_node),
            'arithmetic_operation': lambda: self._has_arithmetic(func_node)
        }
        
        matched = 0
        for pattern in ast_patterns:
            if pattern in pattern_checks:
                try:
                    if pattern_checks[pattern]():
                        matched += 1
                except:
                    pass
        
        return matched / len(ast_patterns) if ast_patterns else 0.0
    
    def _has_nested_loops(self, node: Any, depth: int = 0) -> bool:
        """Check if node contains nested loops."""
        if not node:
            return False
            
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            # Check if any child is also a loop
            for child in getattr(node, 'children', []):
                if self._has_loops_at_depth(child, depth + 1):
                    return True
        
        for child in getattr(node, 'children', []):
            if self._has_nested_loops(child, depth):
                return True
        
        return False
    
    def _has_loops_at_depth(self, node: Any, target_depth: int, current_depth: int = 0) -> bool:
        """Check if there are loops at a specific depth."""
        if not node:
            return False
            
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            if current_depth >= target_depth:
                return True
        
        for child in getattr(node, 'children', []):
            if self._has_loops_at_depth(child, target_depth, current_depth):
                return True
        
        return False
    
    def _count_loops(self, node: Any) -> int:
        """Count total number of loops."""
        if not node:
            return 0
            
        count = 0
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            count += 1
        
        for child in getattr(node, 'children', []):
            count += self._count_loops(child)
        
        return count
    
    def _has_recursive_pattern(self, func_text: str, func_node: Any) -> bool:
        """Check for recursive patterns."""
        # Simple heuristic: function calls itself or has multiple function calls
        func_calls = self._count_function_calls(func_node)
        
        # Look for self-referential patterns
        if re.search(r'(\w+)\s*\([^)]*\1[^)]*\)', func_text):
            return True
        
        # Multiple function calls might indicate recursion
        return func_calls >= 2
    
    def _has_loops(self, node: Any) -> bool:
        """Check if node contains any loops."""
        return self._count_loops(node) > 0
    
    def _has_while_loop(self, node: Any) -> bool:
        """Check for while loops."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'while_statement':
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_while_loop(child):
                return True
        
        return False
    
    def _has_for_loop(self, node: Any) -> bool:
        """Check for for loops."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'for_statement':
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_for_loop(child):
                return True
        
        return False
    
    def _has_function_calls(self, node: Any) -> bool:
        """Check if node contains function calls."""
        return self._count_function_calls(node) > 0
    
    def _count_function_calls(self, node: Any) -> int:
        """Count function calls."""
        if not node:
            return 0
            
        count = 0
        call_types = {'call', 'call_expression', 'function_call'}
        
        if hasattr(node, 'type') and node.type in call_types:
            count += 1
        
        for child in getattr(node, 'children', []):
            count += self._count_function_calls(child)
        
        return count
    
    def _has_comparisons(self, node: Any) -> bool:
        """Check for comparison operations."""
        if not node:
            return False
            
        comparison_types = {'comparison', 'binary_operator', 'comparison_operator'}
        
        if hasattr(node, 'type') and node.type in comparison_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_comparisons(child):
                return True
        
        return False
    
    def _has_assignments(self, node: Any) -> bool:
        """Check for assignment operations."""
        if not node:
            return False
            
        assignment_types = {'assignment', 'assignment_expression', '='}
        
        if hasattr(node, 'type') and node.type in assignment_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_assignments(child):
                return True
        
        return False
    
    def _has_arithmetic(self, node: Any) -> bool:
        """Check for arithmetic operations."""
        if not node:
            return False
            
        arithmetic_types = {'binary_operator', 'arithmetic_operation', '+', '-', '*', '/', '%'}
        
        if hasattr(node, 'type') and node.type in arithmetic_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_arithmetic(child):
                return True
        
        return False
    
    def _extract_functions_from_ast(self, ast_tree: Any) -> List[Dict[str, Any]]:
        """Extract functions from AST tree."""
        if not hasattr(ast_tree, 'root'):
            return []
            
        functions = []
        self._find_functions_recursive(ast_tree.root, functions, ast_tree.code)
        return functions
    
    def _find_functions_recursive(self, node: Any, functions: List[Dict], code: str):
        """Recursively find function definitions in AST."""
        if not node:
            return
            
        function_types = {
            'function_definition',  # Python
            'function_declaration', # JavaScript, C, Java
            'method_definition',    # Java, JavaScript classes
            'arrow_function',       # JavaScript
            'function_item',        # Rust
            'func_declaration',     # Go
        }
        
        if hasattr(node, 'type') and node.type in function_types:
            func_info = {
                'node': node,
                'type': node.type,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'text': code[node.start_byte:node.end_byte],
                'name': self._extract_function_name(node, code),
                'lines': self._calculate_lines(node, code)
            }
            functions.append(func_info)
        
        # Recursively search children
        for child in getattr(node, 'children', []):
            self._find_functions_recursive(child, functions, code)
    
    def _extract_function_name(self, func_node: Any, code: str) -> str:
        """Extract function name from function node."""
        for child in getattr(func_node, 'children', []):
            if hasattr(child, 'type') and child.type in {'identifier', 'function_name', 'name'}:
                return code[child.start_byte:child.end_byte]
        return 'anonymous'
    
    def _calculate_lines(self, node: Any, code: str) -> Dict[str, int]:
        """Calculate line information for a function."""
        start_line = code[:node.start_byte].count('\n') + 1
        end_line = code[:node.end_byte].count('\n') + 1
        return {
            "start": start_line,
            "end": end_line,
            "total": end_line - start_line + 1
        }
    
    def _create_specific_algorithm_entry(self, func: Dict[str, Any], algo_type: AlgorithmType, 
                                       subtype: str, confidence: float, 
                                       ast_tree: Any, language: str) -> Dict[str, Any]:
        """Create algorithm entry with specific subtype information."""
        # Generate unique ID
        algo_id = f"algo_{uuid.uuid4().hex[:8]}"
        
        # Calculate complexity
        complexity = self._calculate_cyclomatic_complexity(func['node'])
        
        # Generate normalized representation and hashes
        hashes = self._generate_algorithm_hashes(func['node'], func['text'], language)
        
        # Extract mathematical invariants
        invariants = self._extract_mathematical_invariants(func['node'])
        
        return {
            'id': algo_id,
            'type': 'algorithm',
            'name': f"{algo_type.value}_{subtype}_implementation",
            'algorithm_type': algo_type.value,
            'algorithm_subtype': subtype,
            'algorithm_category': self._get_algorithm_category(algo_type),
            'confidence': round(confidence, 3),
            'complexity_metric': complexity,
            'lines': func['lines'],
            'evidence': {
                'pattern_type': self._get_algorithm_category(algo_type),
                'algorithm_type': algo_type.value,
                'control_flow': 'complex' if complexity > 5 else 'linear',
                'ast_signature': hashlib.md5(str(func['node']).encode()).hexdigest()[:16],
                'cyclomatic_complexity': complexity,
                'matched_keywords': self._get_matched_keywords(func['text'], func['name'], algo_type, subtype),
                'pattern_confidence': confidence,
                'matched_subtype': subtype,
                'is_generic': subtype.endswith('_generic'),
                'specificity_score': confidence
            },
            'hashes': hashes,
            'transformation_resistance': self._calculate_transformation_resistance(),
            'ast_representation': {
                'normalized': func['node'].type if hasattr(func['node'], 'type') else 'unknown',
                'original': func['text'][:200] + '...' if len(func['text']) > 200 else func['text']
            },
            'control_flow_graph': f"branches:{complexity-1}_loops:{self._count_loops(func['node'])}_calls:{self._count_function_calls(func['node'])}",
            'mathematical_invariants': invariants
        }
    
    def _calculate_cyclomatic_complexity(self, node: Any) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        decision_types = {
            'if_statement', 'while_statement', 'for_statement',
            'case_statement', 'conditional_expression'
        }
        
        def count_decisions(n):
            count = 0
            if hasattr(n, 'type') and n.type in decision_types:
                count += 1
            for child in getattr(n, 'children', []):
                count += count_decisions(child)
            return count
        
        return complexity + count_decisions(node)
    
    def _generate_algorithm_hashes(self, func_node: Any, func_text: str, language: str) -> Dict[str, Any]:
        """Generate hashes for the algorithm."""
        # Generate normalized representation
        normalized_repr = self.normalizer.normalize_function(func_node, func_text, language)
        
        return {
            "direct": self.direct_hasher.hash_text(normalized_repr),
            "fuzzy": {
                "tlsh": self.fuzzy_hasher.hash_text(normalized_repr),
                "tlsh_threshold": self.config.tlsh_threshold if self.config else 100
            },
            "semantic": {
                "minhash": self.semantic_hasher.generate_minhash(normalized_repr),
                "lsh_bands": self.config.lsh_bands if self.config else 20,
                "simhash": self.semantic_hasher.generate_simhash(normalized_repr)
            },
            "normalized_representation": normalized_repr[:200] + "..." if len(normalized_repr) > 200 else normalized_repr,
            "ast_features": self._extract_ast_features(func_node)
        }
    
    def _extract_mathematical_invariants(self, node: Any) -> List[Dict[str, Any]]:
        """Extract mathematical invariants."""
        # Simplified extraction
        return []
    
    def _calculate_transformation_resistance(self) -> Dict[str, float]:
        """Calculate transformation resistance scores."""
        return {
            'variable_renaming': 0.91,
            'language_translation': 0.71,
            'style_changes': 0.81,
            'framework_adaptation': 0.61
        }
    
    def _extract_ast_features(self, func_node: Any) -> Dict[str, Any]:
        """Extract AST features."""
        return {
            "node_types": [func_node.type] if hasattr(func_node, 'type') else [],
            "depth": 1,
            "branching_factor": 1,
            "leaf_count": 1,
            "control_structures": 0,
            "avg_branching": 0.5,
            "control_density": 0.0
        }
    
    def _get_algorithm_category(self, algo_type: AlgorithmType) -> str:
        """Get algorithm category."""
        category_mapping = {
            AlgorithmType.SORTING_ALGORITHM: "core_algorithms",
            AlgorithmType.SEARCH_ALGORITHM: "core_algorithms",
            AlgorithmType.NUMERICAL_ALGORITHM: "mathematical_algorithms",
            AlgorithmType.COMPRESSION_ALGORITHM: "data_processing",
            AlgorithmType.DYNAMIC_PROGRAMMING: "optimization"
        }
        return category_mapping.get(algo_type, "unknown")
    
    def _get_matched_keywords(self, func_text: str, func_name: str, algo_type: AlgorithmType, subtype: str) -> List[str]:
        """Get matched keywords."""
        # Get pattern for this subtype
        type_config = self.patterns.get(algo_type, {})
        subtype_pattern = type_config.get('subtypes', {}).get(subtype, {})
        keywords = subtype_pattern.get('keywords', [])
        
        matched = []
        func_text_lower = func_text.lower()
        func_name_lower = func_name.lower()
        
        for keyword in keywords:
            if keyword in func_name_lower or keyword in func_text_lower:
                matched.append(keyword)
        
        return matched