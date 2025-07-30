"""
Main analyzer class for CopycatM.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import threading
from functools import partial

from .config import AnalysisConfig
from .exceptions import AnalysisError, UnsupportedLanguageError
from ..analysis.metadata import MetadataExtractor
from ..analysis.complexity import ComplexityAnalyzer
from ..analysis.algorithm_detector import AlgorithmDetector
from ..analysis.invariant_extractor import InvariantExtractor
from ..hashing.direct import DirectHasher
from ..hashing.fuzzy import FuzzyHasher
from ..hashing.semantic import SemanticHasher
from ..parsers.base import BaseParser
from ..parsers.tree_sitter_parser import TreeSitterParser
from ..utils.file_utils import get_file_extension, is_supported_language, is_supported_file
from ..utils.json_utils import format_output
from ..gnn.similarity_detector import GNNSimilarityDetector


class CopycatAnalyzer:
    """Main analyzer for detecting AI-generated code derived from copyrighted sources."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """Initialize the analyzer with configuration."""
        self.config = config or AnalysisConfig.load_default()
        
        # Initialize components
        self.metadata_extractor = MetadataExtractor()
        self.complexity_analyzer = ComplexityAnalyzer()
        # Use algorithm detector for better specificity
        self.algorithm_detector = AlgorithmDetector(self.config)
        self.invariant_extractor = InvariantExtractor()
        
        # Initialize hashers
        self.direct_hasher = DirectHasher()
        self.fuzzy_hasher = FuzzyHasher(self.config.tlsh_threshold)
        # Use semantic hasher for better algorithm differentiation
        self.semantic_hasher = SemanticHasher(num_perm=128, lsh_bands=self.config.lsh_bands)
        
        # Initialize parser
        self.parser = TreeSitterParser()
        
        # Initialize GNN similarity detector
        self.gnn_detector = GNNSimilarityDetector(use_pytorch=self.config.use_gnn_pytorch)
        
        # Performance tracking
        self.analysis_times: Dict[str, float] = {}
        self._lock = threading.Lock()  # For thread-safe operations
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze single file and return results."""
        start_time = time.time()
        
        try:
            # Stage 0: Metadata extraction
            metadata = self.metadata_extractor.extract(file_path)
            
            # Check if file is supported
            if not is_supported_language(metadata["language"]):
                raise UnsupportedLanguageError(f"Language {metadata['language']} not supported")
            
            # Stage 1: Parse code
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ast_tree = self.parser.parse(code, metadata["language"])
            
            # Stage 2: Complexity analysis
            complexity_results = self.complexity_analyzer.analyze(ast_tree, metadata["language"])
            
            # Stage 3: Algorithm detection
            algorithms = []
            if metadata["line_count"] >= self.config.min_lines:
                algorithms = self.algorithm_detector.detect(ast_tree, metadata["language"])
            
            # Stage 4: Invariant extraction (for small files)
            invariants = []
            if metadata["line_count"] < self.config.min_lines:
                invariants = self.invariant_extractor.extract(ast_tree, metadata["language"])
            
            # Stage 5: Hash generation
            hashes = self._generate_hashes(code, ast_tree)
            
            # Stage 6: GNN analysis
            gnn_analysis = self._perform_gnn_analysis(ast_tree, metadata["language"])
            
            # Stage 7: Build output
            result = self._build_output(
                metadata, complexity_results, algorithms, invariants, hashes, gnn_analysis
            )
            
            self.analysis_times[file_path] = time.time() - start_time
            return result
            
        except Exception as e:
            raise AnalysisError(f"Failed to analyze {file_path}: {str(e)}") from e
    
    def analyze_directory(self, directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """Analyze all supported files in directory."""
        directory = Path(directory_path)
        
        if recursive:
            files = directory.rglob("*")
        else:
            files = directory.glob("*")
        
        supported_files = [
            f for f in files 
            if f.is_file() and is_supported_file(f.name)
        ]
        
        # Use parallel processing if configured
        if hasattr(self.config, 'parallel_workers') and self.config.parallel_workers and len(supported_files) > 1:
            return self._analyze_files_parallel(supported_files)
        else:
            return self._analyze_files_sequential(supported_files)
    
    def _analyze_files_sequential(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Analyze files sequentially."""
        results = []
        
        for file_path in file_paths:
            try:
                result = self.analyze_file(str(file_path))
                results.append(result)
            except Exception as e:
                # Log error but continue with other files
                print(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def _analyze_files_parallel(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Analyze files in parallel using thread or process pools."""
        results = []
        max_workers = min(self.config.parallel_workers or cpu_count(), len(file_paths))
        
        # Use ThreadPoolExecutor for I/O bound operations
        # ProcessPoolExecutor would be better for CPU-bound work but requires more setup
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file analysis tasks
            future_to_file = {
                executor.submit(self._analyze_single_file_safe, str(file_path)): file_path 
                for file_path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:  # Only add successful results
                        results.append(result)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def _analyze_single_file_safe(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Thread-safe wrapper for analyze_file."""
        try:
            return self.analyze_file(file_path)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def analyze_batch(self, file_paths: List[str], chunk_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Analyze a batch of files with optional chunking for memory management."""
        if not file_paths:
            return []
        
        chunk_size = chunk_size or getattr(self.config, 'chunk_size', 100)
        all_results = []
        
        # Process files in chunks to manage memory
        for i in range(0, len(file_paths), chunk_size):
            chunk = file_paths[i:i + chunk_size]
            print(f"Processing chunk {i//chunk_size + 1}/{(len(file_paths) + chunk_size - 1)//chunk_size} ({len(chunk)} files)")
            
            # Convert strings to Path objects
            chunk_paths = [Path(fp) for fp in chunk]
            
            # Analyze chunk
            if hasattr(self.config, 'parallel_workers') and self.config.parallel_workers and len(chunk) > 1:
                chunk_results = self._analyze_files_parallel(chunk_paths)
            else:
                chunk_results = self._analyze_files_sequential(chunk_paths)
            
            all_results.extend(chunk_results)
            
            # Optional: Force garbage collection between chunks
            if i + chunk_size < len(file_paths):  # Not the last chunk
                import gc
                gc.collect()
        
        return all_results
    
    def analyze_code(self, code: str, language: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze code string directly."""
        # Create temporary metadata
        metadata = {
            "file_name": file_path or "input_code",
            "relative_path": file_path or "input_code",
            "absolute_path": file_path or "input_code",
            "file_size": len(code.encode('utf-8')),
            "content_checksum": self.direct_hasher.sha256(code),
            "file_hash": self.direct_hasher.md5(code),
            "mime_type": f"text/x-{language}",
            "language": language,
            "encoding": "utf-8",
            "line_count": len(code.splitlines()),
            "is_source_code": True,
            "analysis_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        # Parse code
        ast_tree = self.parser.parse(code, language)
        
        # Analyze
        complexity_results = self.complexity_analyzer.analyze(ast_tree, language)
        
        algorithms = []
        if metadata["line_count"] >= self.config.min_lines:
            algorithms = self.algorithm_detector.detect(ast_tree, language)
        
        invariants = []
        if metadata["line_count"] < self.config.min_lines:
            invariants = self.invariant_extractor.extract(ast_tree, language)
        
        hashes = self._generate_hashes(code, ast_tree)
        
        # GNN analysis
        gnn_analysis = self._perform_gnn_analysis(ast_tree, language)
        
        return self._build_output(metadata, complexity_results, algorithms, invariants, hashes, gnn_analysis)
    
    def _generate_hashes(self, code: str, ast_tree: Any) -> Dict[str, Any]:
        """Generate all types of hashes for the code."""
        hashes = {
            "direct": {},
            "fuzzy": {},
            "semantic": {}
        }
        
        # Direct hashes
        if "sha256" in self.config.hash_algorithms:
            hashes["direct"]["sha256"] = self.direct_hasher.sha256(code)
        if "md5" in self.config.hash_algorithms:
            hashes["direct"]["md5"] = self.direct_hasher.md5(code)
        
        # Fuzzy hashes
        if "tlsh" in self.config.hash_algorithms:
            tlsh_hash = self.fuzzy_hasher.tlsh(code)
            hashes["fuzzy"]["tlsh"] = tlsh_hash
            hashes["fuzzy"]["tlsh_threshold"] = self.config.tlsh_threshold
        
        # Semantic hashes
        if "minhash" in self.config.hash_algorithms:
            minhash = self.semantic_hasher.minhash(ast_tree)
            hashes["semantic"]["minhash"] = minhash
            hashes["semantic"]["lsh_bands"] = self.config.lsh_bands
        
        if "simhash" in self.config.hash_algorithms:
            simhash = self.semantic_hasher.simhash(code)
            hashes["semantic"]["simhash"] = simhash
        
        return hashes
    
    def _build_output(self, metadata: Dict, complexity_results: Dict, 
                     algorithms: List[Dict], invariants: List[Dict], 
                     hashes: Dict, gnn_analysis: Dict) -> Dict[str, Any]:
        """Build the complete output structure."""
        output = {
            "copycatm_version": "1.0.0",
            "analysis_config": self.config.to_dict(),
            "file_metadata": metadata,
            "file_properties": {
                "has_invariants": len(invariants) > 0,
                "has_signatures": len(algorithms) > 0,
                "transformation_resistant": self._calculate_transformation_resistance(algorithms, invariants),
                "mathematical_complexity": complexity_results.get("average_complexity", 0),
                "has_property_distribution": len(algorithms) > 1,
                "algorithm_count": len(algorithms)
            },
            "algorithms": algorithms,
            "mathematical_invariants": invariants,
            "gnn_analysis": gnn_analysis,
            "analysis_summary": {
                "total_algorithms": len(algorithms),
                "total_invariants": len(invariants),
                "highest_complexity": complexity_results.get("max_complexity", 0),
                "average_confidence": self._calculate_average_confidence(algorithms, invariants),
                "processing_time_ms": int(self.analysis_times.get(metadata["absolute_path"], 0) * 1000)
            }
        }
        
        return format_output(output)
    
    def _calculate_transformation_resistance(self, algorithms: List[Dict], 
                                          invariants: List[Dict]) -> float:
        """Calculate overall transformation resistance score."""
        if not algorithms and not invariants:
            return 0.0
        
        total_resistance = 0.0
        count = 0
        
        for algo in algorithms:
            resistance = algo.get("transformation_resistance", {})
            avg_resistance = sum(resistance.values()) / len(resistance) if resistance else 0.0
            total_resistance += avg_resistance
            count += 1
        
        for inv in invariants:
            resistance = inv.get("transformation_resistance", {})
            avg_resistance = sum(resistance.values()) / len(resistance) if resistance else 0.0
            total_resistance += avg_resistance
            count += 1
        
        return total_resistance / count if count > 0 else 0.0
    
    def _perform_gnn_analysis(self, ast_tree: Any, language: str) -> Dict[str, Any]:
        """Perform GNN-based analysis on the AST."""
        try:
            # Build graph from AST
            graph = self.gnn_detector.graph_builder.build_graph_from_ast(ast_tree, language)
            
            # Extract graph features
            graph_features = self.gnn_detector.graph_builder.get_graph_features(graph)
            
            # Generate similarity hash
            similarity_hash = self.gnn_detector.get_similarity_hash(graph)
            
            return {
                "graph_features": graph_features,
                "similarity_hash": similarity_hash,
                "num_nodes": graph.number_of_nodes(),
                "num_edges": graph.number_of_edges(),
                "model_type": self.gnn_detector.gnn_model.__class__.__name__
            }
        except Exception as e:
            return {
                "error": f"GNN analysis failed: {str(e)}",
                "graph_features": {},
                "similarity_hash": "",
                "num_nodes": 0,
                "num_edges": 0,
                "model_type": "error"
            }
    
    def _calculate_average_confidence(self, algorithms: List[Dict], 
                                    invariants: List[Dict]) -> float:
        """Calculate average confidence score."""
        confidences = []
        
        for algo in algorithms:
            confidences.append(algo.get("confidence", 0.0))
        
        for inv in invariants:
            confidences.append(inv.get("confidence", 0.0))
        
        return sum(confidences) / len(confidences) if confidences else 0.0 