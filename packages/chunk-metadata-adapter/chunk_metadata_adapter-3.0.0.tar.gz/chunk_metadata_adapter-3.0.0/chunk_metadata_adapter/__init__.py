"""
Chunk Metadata Adapter - A package for managing metadata for chunked content.

This package provides tools for creating, managing, and converting metadata 
for chunks of content in various systems, including RAG pipelines, document 
processing, and machine learning training datasets.
"""

# Core classes
from .semantic_chunk import SemanticChunk, ChunkMetrics, FeedbackMetrics
from .chunk_query import ChunkQuery
from .metadata_builder import ChunkMetadataBuilder

# Data types and enums
from .data_types import (
    ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum,
    ComparableEnum
)

# AST and parsing
from .ast_nodes import (
    ASTNode, ASTVisitor, ASTValidator, ASTAnalyzer,
    FieldCondition, LogicalOperator, ParenExpression, TypedValue,
    ASTNodeFactory
)
from .filter_parser import FilterParser, FilterParseError
from .filter_grammar import FILTER_GRAMMAR
from .ast_optimizer import ASTOptimizer, optimize_ast
from .filter_executor import FilterExecutor

# Validation and analysis
from .query_validator import QueryValidator, ValidationResult
from .complexity_analyzer import ComplexityAnalyzer, analyze_complexity
from .security_validator import SecurityValidator
from .performance_analyzer import PerformanceAnalyzer

__version__ = "3.0.0"

__all__ = [
    # Core classes
    "SemanticChunk", "ChunkMetrics",
    "ChunkQuery", 
    "ChunkMetadataBuilder",
    
    # Data types and enums
    "ChunkType", "ChunkRole", "ChunkStatus", "BlockType", "LanguageEnum",
    "FeedbackMetrics", "ComparableEnum",
    
    # AST and parsing
    "ASTNode", "ASTVisitor", "ASTValidator", "ASTAnalyzer",
    "FieldCondition", "LogicalOperator", "ParenExpression", "TypedValue",
    "ASTNodeFactory",
    "FilterParser", "FilterParseError", "FILTER_GRAMMAR",
    "ASTOptimizer", "optimize_ast", "FilterExecutor",
    
    # Validation and analysis
    "QueryValidator", "ValidationResult",
    "ComplexityAnalyzer", "analyze_complexity",
    "SecurityValidator", "PerformanceAnalyzer",
]
