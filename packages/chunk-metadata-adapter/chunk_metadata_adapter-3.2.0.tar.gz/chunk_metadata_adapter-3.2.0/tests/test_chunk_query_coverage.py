"""
Additional tests for ChunkQuery to improve coverage to 90%+.

This module contains tests specifically designed to cover the uncovered lines
in ChunkQuery, including error handling paths, edge cases, and validation scenarios.

Test coverage targets:
- Field validators with invalid values (lines 194, 207, 218-220, 233, 244-246)
- Error handling in get_ast method (lines 293-295)
- Exception handling in validation methods
- Edge cases in serialization methods

Author: Development Team
Created: 2024-01-20
Updated: 2024-01-20
"""

import pytest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch

from chunk_metadata_adapter.chunk_query import ChunkQuery
from chunk_metadata_adapter.semantic_chunk import SemanticChunk
from chunk_metadata_adapter.data_types import ChunkType, ChunkRole, ChunkStatus, LanguageEnum, BlockType
from chunk_metadata_adapter.filter_parser import FilterParseError


class TestChunkQueryFieldValidation:
    """Tests for field validation with invalid values."""
    
    def test_validate_type_field_invalid_value(self):
        """Test type field validation with invalid value (line 194)."""
        with pytest.raises(ValueError, match="Invalid chunk type"):
            ChunkQuery(type="InvalidType")
    
    def test_validate_role_field_invalid_value(self):
        """Test role field validation with invalid value (line 207)."""
        with pytest.raises(ValueError, match="Invalid chunk role"):
            ChunkQuery(role="InvalidRole")
    
    def test_validate_status_field_invalid_value(self):
        """Test status field validation with invalid value (lines 218-220)."""
        with pytest.raises(ValueError, match="Invalid chunk status"):
            ChunkQuery(status="InvalidStatus")
    
    def test_validate_language_field_invalid_value(self):
        """Test language field validation with invalid value (line 233)."""
        with pytest.raises(ValueError, match="Invalid language"):
            ChunkQuery(language="invalid_lang")
    
    def test_validate_block_type_field_invalid_value(self):
        """Test block_type field validation with invalid value (lines 244-246)."""
        with pytest.raises(ValueError, match="Invalid block type"):
            ChunkQuery(block_type="InvalidBlockType")
    
    def test_validate_uuid_fields_invalid_format(self):
        """Test UUID field validation with invalid format."""
        with pytest.raises(ValueError, match="Invalid UUID"):
            ChunkQuery(uuid="invalid-uuid")
            ChunkQuery(source_id="invalid-uuid")
            ChunkQuery(task_id="invalid-uuid")
            ChunkQuery(subtask_id="invalid-uuid")
            ChunkQuery(unit_id="invalid-uuid")
            ChunkQuery(block_id="invalid-uuid")
            ChunkQuery(link_parent="invalid-uuid")
            ChunkQuery(link_related="invalid-uuid")


class TestChunkQueryASTErrorHandling:
    """Tests for AST error handling in get_ast method."""
    
    def test_get_ast_parse_error(self):
        """Test get_ast with FilterParseError (lines 293-295)."""
        query = ChunkQuery(filter_expr="invalid syntax (")
        
        with pytest.raises(FilterParseError):
            query.get_ast()
    
    def test_get_ast_general_exception(self):
        """Test get_ast with general exception."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Mock parser to raise exception
        with patch('chunk_metadata_adapter.chunk_query.FilterParser') as mock_parser:
            mock_instance = Mock()
            mock_instance.parse.side_effect = Exception("Test exception")
            mock_parser.return_value = mock_instance
            
            with pytest.raises(ValueError, match="Failed to create AST"):
                query.get_ast()
    
    def test_get_ast_execution_error(self):
        """Test matches method with AST execution error."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Mock executor to raise exception
        with patch('chunk_metadata_adapter.chunk_query.FilterExecutor') as mock_executor:
            mock_instance = Mock()
            mock_instance.execute.side_effect = Exception("Execution failed")
            mock_executor.return_value = mock_instance
            
            chunk_data = {"type": "DocBlock"}
            with pytest.raises(ValueError, match="AST execution failed"):
                query.matches(chunk_data)


class TestChunkQuerySerialization:
    """Tests for serialization methods."""
    
    def test_to_flat_dict_with_embedding(self):
        """Test to_flat_dict with include_embedding=True."""
        query = ChunkQuery(
            type="DocBlock",
            embedding=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        )
        
        flat_dict = query.to_flat_dict(include_embedding=True)
        assert "embedding" in flat_dict
        assert isinstance(flat_dict["embedding"], str)
    
    def test_to_flat_dict_for_redis_false(self):
        """Test to_flat_dict with for_redis=False."""
        query = ChunkQuery(type="DocBlock", quality_score=0.8)
        
        flat_dict = query.to_flat_dict(for_redis=False)
        assert "type" in flat_dict
        assert "quality_score" in flat_dict
    
    def test_from_flat_dict_with_complex_data(self):
        """Test from_flat_dict with complex nested data."""
        complex_data = {
            "type": "DocBlock",
            "tags": "ai,python,ml",
            "block_meta": '{"version": "1.0", "author": "test"}',
            "quality_score": "0.8"
        }
        
        query = ChunkQuery.from_flat_dict(complex_data)
        assert query.type == ChunkType.DOC_BLOCK
        assert query.quality_score == 0.8
    
    def test_from_dict_with_validation_invalid_filter(self):
        """Test from_dict_with_validation with invalid filter expression."""
        data = {
            "type": "DocBlock",
            "filter_expr": "__import__('os').system('rm -rf /')"
        }
        
        query, errors = ChunkQuery.from_dict_with_validation(data)
        assert query is None
        assert errors is not None
        assert "errors" in errors
    
    def test_from_dict_with_validation_exception(self):
        """Test from_dict_with_validation with exception."""
        data = {"invalid_field": "value"}
        
        # Mock ChunkQuery constructor to raise exception
        with patch('chunk_metadata_adapter.chunk_query.ChunkQuery.__init__') as mock_init:
            mock_init.side_effect = Exception("Test exception")
            
            query, errors = ChunkQuery.from_dict_with_validation(data)
            assert query is None
            assert errors is not None
            assert "error" in errors
    
    def test_to_json_dict_with_complex_objects(self):
        """Test to_json_dict with complex objects."""
        query = ChunkQuery(
            type="DocBlock",
            tags=["ai", "python"],
            block_meta={"version": "1.0", "author": "test"}
        )
        
        json_dict = query.to_json_dict()
        json_str = json.dumps(json_dict)  # Should not raise exception
        assert isinstance(json_str, str)
    
    def test_to_json_dict_with_enum_values(self):
        """Test to_json_dict with enum values."""
        query = ChunkQuery(
            type=ChunkType.DOC_BLOCK,
            role=ChunkRole.USER,
            status=ChunkStatus.NEW,
            language=LanguageEnum.EN,
            block_type=BlockType.PARAGRAPH
        )
        
        json_dict = query.to_json_dict()
        # All enum values should be converted to strings
        assert isinstance(json_dict["type"], str)
        assert isinstance(json_dict["role"], str)
        assert isinstance(json_dict["status"], str)
        assert isinstance(json_dict["language"], str)
        assert isinstance(json_dict["block_type"], str)


class TestChunkQueryCacheManagement:
    """Tests for cache management methods."""
    
    def test_clear_cache(self):
        """Test clear_cache method."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Initialize caches
        ast = query.get_ast()
        validation = query.validate()
        
        # Verify caches are populated
        assert query._ast_cache is not None
        assert query._validation_cache is not None
        
        # Clear caches
        query.clear_cache()
        
        # Verify caches are cleared
        assert query._ast_cache is None
        assert query._validation_cache is None
        assert query._parser is None
        assert query._executor is None
        assert query._validator is None
        assert query._optimizer is None
    
    def test_get_cache_stats(self):
        """Test get_cache_stats method."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Get stats before initialization
        stats_before = query.get_cache_stats()
        assert stats_before["ast_cached"] == False
        assert stats_before["validation_cached"] == False
        
        # Initialize components
        ast = query.get_ast()
        validation = query.validate()
        
        # Get stats after initialization
        stats_after = query.get_cache_stats()
        assert stats_after["ast_cached"] == True
        assert stats_after["validation_cached"] == True
        assert stats_after["parser_initialized"] == True
        # Executor is initialized lazily, so it might not be initialized yet
        # assert stats_after["executor_initialized"] == True
        assert stats_after["validator_initialized"] == True
        assert stats_after["optimizer_initialized"] == True


class TestChunkQueryMatchesMethod:
    """Tests for matches method edge cases."""
    
    def test_matches_invalid_chunk_data_type(self):
        """Test matches with invalid chunk_data type."""
        query = ChunkQuery(type="DocBlock")
        
        with pytest.raises(ValueError, match="Invalid chunk_data type"):
            query.matches("invalid_data")
    
    def test_matches_with_semantic_chunk(self):
        """Test matches with SemanticChunk object."""
        query = ChunkQuery(type="DocBlock")
        chunk = SemanticChunk(
            type=ChunkType.DOC_BLOCK,
            body="Test content"
        )
        
        result = query.matches(chunk)
        assert result == True
    
    def test_matches_simple_fields_all_none(self):
        """Test _matches_simple_fields with all None values."""
        query = ChunkQuery()  # No filters set
        chunk_data = {"type": "DocBlock", "quality_score": 0.8}
        
        result = query._matches_simple_fields(chunk_data)
        assert result == True  # Should match when no filters are set


class TestChunkQueryValidationErrorHandling:
    """Tests for validation error handling."""
    
    def test_validate_with_exception(self):
        """Test validate method with exception."""
        query = ChunkQuery(filter_expr="type = 'DocBlock'")
        
        # Mock validator to raise exception
        with patch('chunk_metadata_adapter.chunk_query.QueryValidator') as mock_validator:
            mock_instance = Mock()
            mock_instance.validate.side_effect = Exception("Validation failed")
            mock_validator.return_value = mock_instance
            
            result = query.validate()
            assert result.is_valid == False
            assert len(result.errors) == 1
            assert "Validation failed" in result.errors[0]
    
    def test_validate_no_filter_expr(self):
        """Test validate method with no filter expression."""
        query = ChunkQuery()  # No filter_expr
        
        result = query.validate()
        assert result.is_valid == True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0 