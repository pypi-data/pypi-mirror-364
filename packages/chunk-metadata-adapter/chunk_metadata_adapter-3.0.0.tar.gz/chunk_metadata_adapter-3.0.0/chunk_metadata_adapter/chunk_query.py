"""
Enhanced ChunkQuery with AST-based filtering for Redis metadata operations.

This module provides an enhanced ChunkQuery class that integrates with the AST
filtering system for efficient Redis metadata filtering and search operations.

Key features:
- AST-based filter parsing and execution
- Support for complex logical expressions
- Integration with Redis flat dictionary format
- Type-safe filtering with SemanticChunk compatibility
- Performance optimization for Redis operations
- Support for vector search and metadata filtering

Architecture:
- FilterParser: Parses string expressions into AST
- FilterExecutor: Executes AST against flat dictionaries
- QueryValidator: Validates filter expressions for security
- ASTOptimizer: Optimizes AST for performance
- Integration with RedisMetadataFilterService

Usage examples:
    >>> # Simple field filtering
    >>> query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
    >>> ast = query.get_ast()
    
    >>> # Complex logical expressions
    >>> query = ChunkQuery(filter_expr="(type = 'DocBlock' OR type = 'CodeBlock') AND quality_score >= 0.7")
    >>> matches = query.matches(chunk_data)
    
    >>> # Integration with Redis filter service
    >>> results = await filter_service.search(query, limit=10)

Dependencies:
- ast_nodes: For AST structures and execution
- filter_parser: For parsing filter expressions
- filter_executor: For executing AST against data
- query_validator: For validation and security
- ast_optimizer: For performance optimization
- semantic_chunk: For data model compatibility

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

from typing import Optional, Union, Any, List, Dict, Set
from pydantic import Field, BaseModel, ConfigDict, field_validator, ValidationError
import re
from datetime import datetime

from .ast_nodes import ASTNode, TypedValue
from .filter_parser import FilterParser, FilterParseError
from .filter_executor import FilterExecutor
from .query_validator import QueryValidator, ValidationResult
from .ast_optimizer import ASTOptimizer
from .semantic_chunk import SemanticChunk
from .data_types import ChunkType, ChunkRole, ChunkStatus, BlockType, LanguageEnum


class ChunkQuery(BaseModel):
    """
    Enhanced query model for Redis metadata filtering with AST support.
    
    This class provides both simple field-based filtering and complex
    AST-based filtering for efficient Redis metadata operations.
    
    Features:
    - Simple field filtering (legacy compatibility)
    - Complex AST-based filtering with logical expressions
    - Type-safe field validation
    - Performance optimization for Redis operations
    - Integration with vector search capabilities
    
    Field Types:
    - Simple fields: Direct value comparison
    - Numeric fields: Support comparison operators (>, >=, <, <=, =, !=)
    - List fields: Support inclusion operators (in, not_in, intersects)
    - String fields: Support pattern matching (like, ~, !~)
    - Enum fields: Strict validation against enum values
    
    AST Filtering:
    - Complex logical expressions (AND, OR, NOT)
    - Parenthesized expressions for precedence
    - Nested field access (e.g., metrics.quality_score)
    - Type-safe value comparisons
    - Performance optimization through AST caching
    
    Usage:
        >>> # Simple filtering
        >>> query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
        >>> # Complex filtering
        >>> query = ChunkQuery(filter_expr="
        (type = 'DocBlock' OR type = 'CodeBlock') AND
        ...     quality_score >= 0.7 AND
        ...     tags intersects ['ai', 'ml'] AND
        ...     year >= 2020 AND
        ...     NOT is_deleted
        ... ")
        
        >>> # Check if chunk matches
        >>> matches = query.matches(chunk_data)
        
        >>> # Get AST representation
        >>> ast = query.get_ast()
        
        >>> # Validate filter expression
        >>> validation = query.validate()
    """
    
    # Simple field filters (legacy compatibility)
    uuid: Optional[str] = Field(default=None, description="Unique identifier (UUIDv4)")
    source_id: Optional[str] = Field(default=None, description="Source identifier (UUIDv4)")
    project: Optional[str] = Field(default=None, description="Project name")
    task_id: Optional[str] = Field(default=None, description="Task identifier (UUIDv4)")
    subtask_id: Optional[str] = Field(default=None, description="Subtask identifier (UUIDv4)")
    unit_id: Optional[str] = Field(default=None, description="Processing unit identifier (UUIDv4)")
    type: Optional[Union[str, ChunkType]] = Field(default=None, description="Chunk type")
    role: Optional[Union[str, ChunkRole]] = Field(default=None, description="Role in the system")
    language: Optional[Union[str, LanguageEnum]] = Field(default=None, description="Language code")
    body: Optional[str] = Field(default=None, description="Original chunk text")
    text: Optional[str] = Field(default=None, description="Normalized text for search")
    summary: Optional[str] = Field(default=None, description="Short summary of the chunk")
    ordinal: Optional[Union[int, str]] = Field(default=None, description="Order of the chunk")
    sha256: Optional[str] = Field(default=None, description="SHA256 hash of the text")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat(), description="ISO8601 creation date")
    status: Optional[Union[str, ChunkStatus]] = Field(default=None, description="Processing status")
    source_path: Optional[str] = Field(default=None, description="Path to the source file")
    quality_score: Optional[Union[float, str]] = Field(default=None, description="Quality score [0,1]")
    coverage: Optional[Union[float, str]] = Field(default=None, description="Coverage [0,1]")
    cohesion: Optional[Union[float, str]] = Field(default=None, description="Cohesion [0,1]")
    boundary_prev: Optional[Union[float, str]] = Field(default=None, description="Boundary similarity with previous chunk")
    boundary_next: Optional[Union[float, str]] = Field(default=None, description="Boundary similarity with next chunk")
    used_in_generation: Optional[Union[bool, str]] = Field(default=None, description="Whether used in generation")
    feedback_accepted: Optional[Union[int, str]] = Field(default=None, description="How many times the chunk was accepted")
    feedback_rejected: Optional[Union[int, str]] = Field(default=None, description="How many times the chunk was rejected")
    start: Optional[Union[int, str]] = Field(default=None, description="Start offset")
    end: Optional[Union[int, str]] = Field(default=None, description="End offset")
    category: Optional[str] = Field(default=None, description="Business category")
    title: Optional[str] = Field(default=None, description="Title or short name")
    year: Optional[Union[int, str]] = Field(default=None, description="Year")
    is_public: Optional[Union[bool, str]] = Field(default=None, description="Public visibility")
    is_deleted: Optional[Union[bool, str]] = Field(default=None, description="Soft delete flag")
    source: Optional[str] = Field(default=None, description="Data source")
    block_type: Optional[Union[str, BlockType]] = Field(default=None, description="Type of the source block")
    chunking_version: Optional[str] = Field(default=None, description="Version of the chunking algorithm")
    block_id: Optional[str] = Field(default=None, description="UUIDv4 of the source block")
    embedding: Optional[Union[List[float], List[List[float]]]] = Field(default=None, description="Embedding vector(s)")
    block_index: Optional[Union[int, str]] = Field(default=None, description="Index of the block in the source document")
    source_lines_start: Optional[Union[int, str]] = Field(default=None, description="Start line in the source file")
    source_lines_end: Optional[Union[int, str]] = Field(default=None, description="End line in the source file")
    tags: Optional[Union[List[str], str]] = Field(default=None, description="Categorical tags for the chunk")
    links: Optional[Union[List[str], str]] = Field(default=None, description="References to other chunks")
    block_meta: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the block")
    tags_flat: Optional[str] = Field(default=None, description="Comma-separated tags for flat storage")
    link_related: Optional[str] = Field(default=None, description="Related chunk UUID")
    link_parent: Optional[str] = Field(default=None, description="Parent chunk UUID")
    
    # AST-based filtering
    filter_expr: Optional[str] = Field(default=None, description="Complex filter expression for AST parsing")
    
    # Configuration
    model_config = ConfigDict(extra="allow")

    # Cached components
    _ast_cache: Optional[ASTNode] = None
    _validation_cache: Optional[ValidationResult] = None
    _parser: Optional[FilterParser] = None
    _executor: Optional[FilterExecutor] = None
    _validator: Optional[QueryValidator] = None
    _optimizer: Optional[ASTOptimizer] = None
    
    @field_validator('uuid', 'source_id', 'task_id', 'subtask_id', 'unit_id', 'block_id', 'link_parent', 'link_related')
    @classmethod
    def validate_uuid_fields(cls, v):
        """Validate UUID fields."""
        if v is None:
            return v
        if not isinstance(v, str) or not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', v, re.IGNORECASE):
            raise ValueError(f"Invalid UUID format: {v}")
        return v
    
    @field_validator('type')
    @classmethod
    def validate_type_field(cls, v):
        """Validate type field."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return ChunkType(v)
            except ValueError:
                raise ValueError(f"Invalid chunk type: {v}")
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role_field(cls, v):
        """Validate role field."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return ChunkRole(v)
            except ValueError:
                raise ValueError(f"Invalid chunk role: {v}")
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status_field(cls, v):
        """Validate status field."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return ChunkStatus(v)
            except ValueError:
                raise ValueError(f"Invalid chunk status: {v}")
        return v
    
    @field_validator('language')
    @classmethod
    def validate_language_field(cls, v):
        """Validate language field."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return LanguageEnum(v)
            except ValueError:
                raise ValueError(f"Invalid language: {v}")
        return v
    
    @field_validator('block_type')
    @classmethod
    def validate_block_type_field(cls, v):
        """Validate block_type field."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return BlockType(v)
            except ValueError:
                raise ValueError(f"Invalid block type: {v}")
        return v
    
    def get_ast(self) -> Optional[ASTNode]:
        """
        Get AST representation of the filter.
        
        This method parses the filter expression into an Abstract Syntax Tree
        for efficient execution. The AST is cached for performance.
        
        Returns:
            ASTNode: Root node of the parsed AST, or None if no filter expression
            
        Raises:
            FilterParseError: If filter expression cannot be parsed
            ValueError: If filter expression is invalid
            
        Usage examples:
            >>> query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
            >>> ast = query.get_ast()
            >>> print(type(ast))  # <class 'LogicalOperator'>
            
            >>> query = ChunkQuery(type="DocBlock")  # Simple field filter
            >>> ast = query.get_ast()  # None (no complex expression)
        """
        # If no filter expression, return None
        if not self.filter_expr:
            return None
        
        # Return cached AST if available
        if self._ast_cache is not None:
            return self._ast_cache
        
        # Parse filter expression
        try:
            parser = self._get_parser()
            ast = parser.parse(self.filter_expr)
            
            # Optimize AST for performance
            optimizer = self._get_optimizer()
            optimized_ast = optimizer.optimize(ast)
            
            # Cache the optimized AST
            self._ast_cache = optimized_ast
            return optimized_ast
            
        except FilterParseError as e:
            raise FilterParseError(f"Failed to parse filter expression: {e.message}", self.filter_expr, e.position)
        except Exception as e:
            raise ValueError(f"Failed to create AST: {e}")
    
    def matches(self, chunk_data: Union[Dict[str, Any], SemanticChunk]) -> bool:
        """
        Check if chunk data matches the filter criteria.
        
        This method evaluates the filter against chunk data, supporting both
        simple field filtering and complex AST-based filtering.
        
        Args:
            chunk_data: Chunk data to evaluate (dict or SemanticChunk)
                - Dict: Flat dictionary from Redis
                - SemanticChunk: Structured chunk object
                
        Returns:
            bool: True if chunk matches filter, False otherwise
            
        Raises:
            ValueError: If chunk_data is invalid or filter execution fails
            
        Usage examples:
            >>> query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
            >>> chunk = {"type": "DocBlock", "quality_score": 0.9}
            >>> matches = query.matches(chunk)  # True
            
            >>> query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
            >>> matches = query.matches(chunk)  # True
            
            >>> semantic_chunk = SemanticChunk(type=ChunkType.DOC_BLOCK, quality_score=0.9)
            >>> matches = query.matches(semantic_chunk)  # True
        """
        # Convert SemanticChunk to dict if needed
        if isinstance(chunk_data, SemanticChunk):
            chunk_dict = chunk_data.model_dump()
        elif isinstance(chunk_data, dict):
            chunk_dict = chunk_data
        else:
            raise ValueError(f"Invalid chunk_data type: {type(chunk_data)}")
        
        # Check if we have AST-based filtering
        ast = self.get_ast()
        if ast is not None:
            # Use AST-based filtering
            try:
                executor = self._get_executor()
                return executor.execute(ast, chunk_dict)
            except Exception as e:
                raise ValueError(f"AST execution failed: {e}")
        
        # Fall back to simple field filtering
        return self._matches_simple_fields(chunk_dict)
    
    def validate(self) -> ValidationResult:
        """
        Validate the filter expression for security and correctness.
        
        This method performs comprehensive validation of the filter expression,
        including security checks, syntax validation, and performance analysis.
        
        Returns:
            ValidationResult: Validation result with errors, warnings, and details
            
        Usage examples:
            >>> query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
            >>> result = query.validate()
            >>> print(f"Valid: {result.is_valid}")
            >>> print(f"Errors: {result.errors}")
            
            >>> query = ChunkQuery(filter_expr="__import__('os').system('rm -rf /')")
            >>> result = query.validate()
            >>> print(f"Valid: {result.is_valid}")  # False
            >>> print(f"Errors: {result.errors}")  # Security violations
        """
        # Return cached validation if available
        if self._validation_cache is not None:
            return self._validation_cache
        
        # If no filter expression, return valid result
        if not self.filter_expr:
            result = ValidationResult(is_valid=True, errors=[], warnings=[])
            self._validation_cache = result
            return result
        
        # Validate filter expression
        try:
            validator = self._get_validator()
            result = validator.validate(self.filter_expr)
            self._validation_cache = result
            return result
        except Exception as e:
            result = ValidationResult(
                is_valid=False,
                errors=[f"Validation failed: {e}"],
                warnings=[]
            )
            self._validation_cache = result
            return result
    
    def to_flat_dict(self, for_redis: bool = True, include_embedding: bool = False) -> dict:
        """
        Convert query to flat dictionary for Redis operations.
        
        This method serializes the query into a flat dictionary format
        suitable for Redis storage and transmission.
        
        Args:
            for_redis: Whether to format for Redis storage
            include_embedding: Whether to include embedding vectors
            
        Returns:
            dict: Flat dictionary representation of the query
            
        Usage examples:
            >>> query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
            >>> flat = query.to_flat_dict()
            >>> print(flat)  # {'type': 'DocBlock', 'quality_score': '>=0.8'}
        """
        from .utils import to_flat_dict
        
        # Convert to dict
        query_dict = self.model_dump()
        
        # Remove None values (including created_at when it's None)
        filtered_dict = {}
        for k, v in query_dict.items():
            if v is not None:
                filtered_dict[k] = v
        
        # Convert to flat format
        flat_dict = to_flat_dict(filtered_dict, for_redis=for_redis, include_embedding=include_embedding)
        
        return flat_dict

    @classmethod
    def from_flat_dict(cls, data: dict) -> "ChunkQuery":
        """
        Create query from flat dictionary.
        
        This method deserializes a flat dictionary into a ChunkQuery object,
        handling type conversions and validation.
        
        Args:
            data: Flat dictionary data
            
        Returns:
            ChunkQuery: Query object created from flat data
            
        Usage examples:
            >>> flat_data = {'type': 'DocBlock', 'quality_score': '>=0.8'}
            >>> query = ChunkQuery.from_flat_dict(flat_data)
            >>> print(query.type)  # ChunkType.DOC_BLOCK
        """
        from .utils import from_flat_dict
        
        # Convert from flat format
        restored_data = from_flat_dict(data)
        
        # Create query object
        return cls(**restored_data)

    @classmethod
    def from_dict_with_validation(cls, data: dict) -> ("ChunkQuery", Optional[dict]):
        """
        Create query from dictionary with validation.
        
        This method validates input data and creates a ChunkQuery object,
        returning validation errors if any.
        
        Args:
            data: Input dictionary data
            
        Returns:
            tuple: (ChunkQuery, errors) - query object and validation errors
            
        Usage examples:
            >>> data = {'type': 'DocBlock', 'quality_score': '>=0.8'}
            >>> query, errors = ChunkQuery.from_dict_with_validation(data)
            >>> if errors:
            ...     print(f"Validation errors: {errors}")
            ... else:
            ...     print("Query created successfully")
        """
        try:
            query = cls(**data)
            
            # Validate filter expression if present
            if query.filter_expr:
                validation_result = query.validate()
                if not validation_result.is_valid:
                    return None, {
                        "errors": validation_result.errors,
                        "warnings": validation_result.warnings
                    }
            
            return query, None
            
        except ValidationError as e:
            # Handle Pydantic validation errors
            errors = {"fields": {}}
            for error in e.errors():
                field_name = error["loc"][0] if error["loc"] else "unknown"
                if field_name not in errors["fields"]:
                    errors["fields"][field_name] = []
                errors["fields"][field_name].append(error["msg"])
            return None, errors
            
        except Exception as e:
            return None, {"error": str(e)}

    def to_json_dict(self) -> dict:
        """
        Convert query to JSON-serializable dictionary.
        
        Returns:
            dict: JSON-serializable dictionary representation
            
        Usage examples:
            >>> query = ChunkQuery(type="DocBlock", quality_score=">=0.8")
            >>> json_dict = query.to_json_dict()
            >>> import json
            >>> json_str = json.dumps(json_dict)
        """
        import json
        
        def make_json_serializable(obj):
            if isinstance(obj, (str, int, float, bool)) or obj is None:
                return obj
            elif isinstance(obj, (list, tuple)):
                return [make_json_serializable(x) for x in obj]
            elif isinstance(obj, dict):
                return {str(k): make_json_serializable(v) for k, v in obj.items()}
            else:
                return str(obj)
        
        query_dict = self.model_dump()
        return make_json_serializable(query_dict)

    @classmethod
    def from_json_dict(cls, data: dict) -> "ChunkQuery":
        """
        Create query from JSON dictionary.
        
        Args:
            data: JSON dictionary data
            
        Returns:
            ChunkQuery: Query object created from JSON data
        """
        return cls(**data)
    
    def clear_cache(self) -> None:
        """
        Clear internal caches for AST, validation, and components.
        
        This method clears all cached data, forcing re-parsing and re-validation
        on next access. Useful when filter expression changes.
        
        Usage examples:
            >>> query = ChunkQuery(filter_expr="type = 'DocBlock'")
            >>> ast1 = query.get_ast()  # Parses and caches AST
            >>> query.filter_expr = "type = 'CodeBlock'"
            >>> query.clear_cache()  # Clear cached AST
            >>> ast2 = query.get_ast()  # Re-parses with new expression
        """
        self._ast_cache = None
        self._validation_cache = None
        self._parser = None
        self._executor = None
        self._validator = None
        self._optimizer = None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for performance monitoring.
        
        Returns:
            dict: Cache statistics including hit rates and memory usage
            
        Usage examples:
            >>> query = ChunkQuery(filter_expr="type = 'DocBlock' AND quality_score >= 0.8")
            >>> ast = query.get_ast()  # First access - parses
            >>> ast2 = query.get_ast()  # Second access - cached
            >>> stats = query.get_cache_stats()
            >>> print(f"AST cache hits: {stats['ast_cache_hits']}")
        """
        stats = {
            "ast_cached": self._ast_cache is not None,
            "validation_cached": self._validation_cache is not None,
            "parser_initialized": self._parser is not None,
            "executor_initialized": self._executor is not None,
            "validator_initialized": self._validator is not None,
            "optimizer_initialized": self._optimizer is not None,
        }
        
        # Add executor cache stats if available
        if self._executor:
            executor_stats = self._executor.get_cache_stats()
            stats.update(executor_stats)
        
        return stats
    
    # Private methods for component management
    def _get_parser(self) -> FilterParser:
        """Get or create FilterParser instance."""
        if self._parser is None:
            self._parser = FilterParser()
        return self._parser
    
    def _get_executor(self) -> FilterExecutor:
        """Get or create FilterExecutor instance."""
        if self._executor is None:
            self._executor = FilterExecutor()
        return self._executor
    
    def _get_validator(self) -> QueryValidator:
        """Get or create QueryValidator instance."""
        if self._validator is None:
            self._validator = QueryValidator()
        return self._validator
    
    def _get_optimizer(self) -> ASTOptimizer:
        """Get or create ASTOptimizer instance."""
        if self._optimizer is None:
            self._optimizer = ASTOptimizer()
        return self._optimizer
    
    def _matches_simple_fields(self, chunk_dict: Dict[str, Any]) -> bool:
        """
        Check if chunk matches simple field filters.
        
        This method implements legacy field-based filtering for backward
        compatibility with simple field queries.
        
        Args:
            chunk_dict: Chunk data dictionary
            
        Returns:
            bool: True if chunk matches all field criteria
        """
        # Get query fields (excluding special fields)
        query_fields = self.model_dump()
        special_fields = {'filter_expr', 'model_config', '_ast_cache', '_validation_cache', 
                         '_parser', '_executor', '_validator', '_optimizer', 'created_at'}
        
        for field, query_value in query_fields.items():
            if field in special_fields or query_value is None or field.startswith('_'):
                continue
            
            chunk_value = chunk_dict.get(field)
            
            # Handle different field types
            if not self._matches_field_value(chunk_value, query_value, field):
                return False
        
        return True
    
    def _matches_field_value(self, chunk_value: Any, query_value: Any, field_name: str) -> bool:
        """
        Check if a single field value matches the query criteria.
        
        Args:
            chunk_value: Value from chunk data
            query_value: Value from query
            field_name: Name of the field
            
        Returns:
            bool: True if values match according to field type
        """
        # Handle None values
        if query_value is None:
            return True
        if chunk_value is None:
            return False
        
        # Handle string comparison with operators
        if isinstance(query_value, str) and self._is_operator_string(query_value):
            return self._matches_operator_string(chunk_value, query_value, field_name)
        
        # Handle list fields
        if field_name in ['tags', 'links']:
            return self._matches_list_field(chunk_value, query_value)
        
        # Handle boolean fields
        if field_name in ['is_deleted', 'is_public', 'used_in_generation']:
            return self._matches_boolean_field(chunk_value, query_value)
        
        # Handle numeric fields
        if field_name in ['quality_score', 'coverage', 'cohesion', 'boundary_prev', 'boundary_next',
                         'feedback_accepted', 'feedback_rejected', 'start', 'end', 'year',
                         'ordinal', 'source_lines_start', 'source_lines_end', 'block_index']:
            return self._matches_numeric_field(chunk_value, query_value)
        
        # Handle enum fields
        if field_name in ['type', 'role', 'status', 'language', 'block_type']:
            # For enum fields, compare values
            if hasattr(query_value, 'value'):
                query_str = query_value.value.lower()
            else:
                query_str = str(query_value).lower()
            
            if hasattr(chunk_value, 'value'):
                chunk_str = chunk_value.value.lower()
            else:
                chunk_str = str(chunk_value).lower()
            
            return chunk_str == query_str
        
        # Default: string comparison
        return str(chunk_value).lower() == str(query_value).lower()
    
    def _is_operator_string(self, value: str) -> bool:
        """Check if string contains comparison operators."""
        operators = ['>=', '<=', '>', '<', '!=', '=', 'in:', 'not_in:', 'like:', '~', '!~']
        return any(value.startswith(op) for op in operators)
    
    def _matches_operator_string(self, chunk_value: Any, query_value: str, field_name: str) -> bool:
        """Match value against operator string."""
        try:
            # Extract operator and value
            if query_value.startswith('>='):
                operator, value_str = '>=', query_value[2:]
            elif query_value.startswith('<='):
                operator, value_str = '<=', query_value[2:]
            elif query_value.startswith('>'):
                operator, value_str = '>', query_value[1:]
            elif query_value.startswith('<'):
                operator, value_str = '<', query_value[1:]
            elif query_value.startswith('!='):
                operator, value_str = '!=', query_value[2:]
            elif query_value.startswith('='):
                operator, value_str = '=', query_value[1:]
            elif query_value.startswith('in:'):
                operator, value_str = 'in', query_value[3:]
            elif query_value.startswith('not_in:'):
                operator, value_str = 'not_in', query_value[7:]
            elif query_value.startswith('like:'):
                operator, value_str = 'like', query_value[5:]
            elif query_value.startswith('~'):
                operator, value_str = '~', query_value[1:]
            elif query_value.startswith('!~'):
                operator, value_str = '!~', query_value[2:]
            else:
                return str(chunk_value).lower() == query_value.lower()
            
            # Handle list operators
            if operator in ['in', 'not_in']:
                return self._matches_list_operator(chunk_value, operator, value_str)
            
            # Convert values for comparison
            if field_name in ['quality_score', 'coverage', 'cohesion', 'boundary_prev', 'boundary_next']:
                chunk_num = float(chunk_value) if chunk_value is not None else 0.0
                query_num = float(value_str)
            elif field_name in ['feedback_accepted', 'feedback_rejected', 'start', 'end', 'year',
                               'ordinal', 'source_lines_start', 'source_lines_end', 'block_index']:
                chunk_num = int(chunk_value) if chunk_value is not None else 0
                query_num = int(value_str)
            else:
                chunk_str = str(chunk_value).lower()
                query_str = value_str.lower()
                return self._compare_strings(chunk_str, operator, query_str)
            
            # Numeric comparison
            if operator == '>=':
                return chunk_num >= query_num
            elif operator == '<=':
                return chunk_num <= query_num
            elif operator == '>':
                return chunk_num > query_num
            elif operator == '<':
                return chunk_num < query_num
            elif operator == '!=':
                return chunk_num != query_num
            elif operator == '=':
                return chunk_num == query_num
            else:
                return False
                
        except (ValueError, TypeError):
            return False
    
    def _compare_strings(self, chunk_str: str, operator: str, query_str: str) -> bool:
        """Compare strings using various operators."""
        if operator == '=':
            return chunk_str == query_str
        elif operator == '!=':
            return chunk_str != query_str
        elif operator == 'like':
            return query_str in chunk_str
        elif operator == '~':
            import re
            try:
                return bool(re.search(query_str, chunk_str))
            except re.error:
                return False
        elif operator == '!~':
            import re
            try:
                return not bool(re.search(query_str, chunk_str))
            except re.error:
                return True
        else:
            return False
    
    def _matches_list_field(self, chunk_value: Any, query_value: Any) -> bool:
        """Match list field values."""
        # Convert chunk value to list
        if isinstance(chunk_value, str):
            chunk_list = [item.strip() for item in chunk_value.split(',') if item.strip()]
        elif isinstance(chunk_value, (list, tuple)):
            chunk_list = [str(item) for item in chunk_value if item is not None]
        else:
            chunk_list = [str(chunk_value)] if chunk_value is not None else []
        
        # Convert query value to list
        if isinstance(query_value, str):
            query_list = [item.strip() for item in query_value.split(',') if item.strip()]
        elif isinstance(query_value, (list, tuple)):
            query_list = [str(item) for item in query_value if item is not None]
        else:
            query_list = [str(query_value)] if query_value is not None else []
        
        # Check intersection
        chunk_set = set(item.lower() for item in chunk_list)
        query_set = set(item.lower() for item in query_list)
        return bool(chunk_set.intersection(query_set))
    
    def _matches_boolean_field(self, chunk_value: Any, query_value: Any) -> bool:
        """Match boolean field values."""
        # Convert chunk value to boolean
        if isinstance(chunk_value, bool):
            chunk_bool = chunk_value
        elif isinstance(chunk_value, str):
            chunk_bool = chunk_value.lower() in ['true', '1', 'yes', 'on']
        else:
            chunk_bool = bool(chunk_value)
        
        # Convert query value to boolean
        if isinstance(query_value, bool):
            query_bool = query_value
        elif isinstance(query_value, str):
            query_bool = query_value.lower() in ['true', '1', 'yes', 'on']
        else:
            query_bool = bool(query_value)
        
        return chunk_bool == query_bool
    
    def _matches_numeric_field(self, chunk_value: Any, query_value: Any) -> bool:
        """Match numeric field values."""
        try:
            # Convert chunk value to number
            if isinstance(chunk_value, (int, float)):
                chunk_num = chunk_value
            elif isinstance(chunk_value, str):
                chunk_num = float(chunk_value) if '.' in chunk_value else int(chunk_value)
            else:
                chunk_num = 0
            
            # Convert query value to number
            if isinstance(query_value, (int, float)):
                query_num = query_value
            elif isinstance(query_value, str):
                query_num = float(query_value) if '.' in query_value else int(query_value)
            else:
                query_num = 0
            
            return chunk_num == query_num
            
        except (ValueError, TypeError):
            return False
    
    def _matches_list_operator(self, chunk_value: Any, operator: str, value_str: str) -> bool:
        """Match list operators (in, not_in)."""
        # Parse query value as comma-separated list
        query_list = [item.strip() for item in value_str.split(',') if item.strip()]
        
        # Convert chunk value to list
        if isinstance(chunk_value, str):
            chunk_list = [item.strip() for item in chunk_value.split(',') if item.strip()]
        elif isinstance(chunk_value, (list, tuple)):
            chunk_list = [str(item) for item in chunk_value if item is not None]
        else:
            chunk_list = [str(chunk_value)] if chunk_value is not None else []
        
        # Check intersection
        chunk_set = set(item.lower() for item in chunk_list)
        query_set = set(item.lower() for item in query_list)
        
        if operator == 'in':
            return bool(chunk_set & query_set)  # Intersection
        elif operator == 'not_in':
            return not bool(chunk_set & query_set)  # No intersection
        else:
            return False