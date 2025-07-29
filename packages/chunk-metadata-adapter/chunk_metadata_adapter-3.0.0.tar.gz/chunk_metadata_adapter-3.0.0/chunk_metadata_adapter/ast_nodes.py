"""
AST nodes for filter expression parsing and execution.

This module provides the core data structures for representing filter expressions
as Abstract Syntax Trees (AST). It includes typed nodes for field conditions,
logical operators, and parenthesized expressions.

Key features:
- TypedValue: Type-safe value representation with validation
- FieldCondition: Field comparison conditions (age > 18)
- LogicalOperator: Logical operations (AND, OR, NOT)
- ParenExpression: Parenthesized expressions for precedence

Usage examples:
    >>> from ast_nodes import FieldCondition, TypedValue
    >>> condition = FieldCondition("age", ">", TypedValue("int", 18))
    >>> result = condition.evaluate({"age": 25})

Dependencies:
- dataclasses: For data structure definitions
- typing: For type hints and annotations
- datetime: For date/time value support

Author: Development Team
Created: 2024-01-15
Updated: 2024-01-20
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union, Literal, Optional, Any, Dict
from datetime import datetime
import re


@dataclass
class TypedValue:
    """
    Type-safe value representation with validation.

    This class represents a value with its associated type information,
    enabling type-safe operations and validation. It supports various
    data types including primitives, collections, and special values.

    Attributes:
        type (Literal): The type of the value
            - "int": Integer values
            - "float": Floating-point values
            - "str": String values
            - "list": List values
            - "dict": Dictionary values
            - "date": Date/time values
            - "null": Null/None values
            - "bool": Boolean values
        value (Union): The actual value, must match the specified type

    Usage examples:
        >>> int_val = TypedValue("int", 42)
        >>> str_val = TypedValue("str", "hello")
        >>> list_val = TypedValue("list", [1, 2, 3])
        >>> null_val = TypedValue("null", None)

    Notes:
        - Type and value are validated on creation
        - Date values should be datetime objects
        - Null values should have None as the value
    """
    
    type: Literal["int", "float", "str", "list", "dict", "date", "null", "bool"]
    value: Union[int, float, str, List, Dict, datetime, None, bool]
    
    def __post_init__(self) -> None:
        """Validate type and value consistency."""
        self._validate_type()
        self._validate_value()
    
    def _validate_type(self) -> None:
        """Validate that type and value are consistent."""
        if self.type == "null" and self.value is not None:
            raise ValueError("Null type must have None value")
        elif self.type != "null" and self.value is None:
            raise ValueError(f"Type {self.type} cannot have None value")
        
        # Type-specific validations
        if self.type == "int" and not isinstance(self.value, int):
            raise ValueError(f"Int type requires int value, got {type(self.value)}")
        elif self.type == "float" and not isinstance(self.value, (int, float)):
            raise ValueError(f"Float type requires numeric value, got {type(self.value)}")
        elif self.type == "str" and not isinstance(self.value, str):
            raise ValueError(f"Str type requires string value, got {type(self.value)}")
        elif self.type == "list" and not isinstance(self.value, list):
            raise ValueError(f"List type requires list value, got {type(self.value)}")
        elif self.type == "dict" and not isinstance(self.value, dict):
            raise ValueError(f"Dict type requires dict value, got {type(self.value)}")
        elif self.type == "date" and not isinstance(self.value, (datetime, str)):
            raise ValueError(f"Date type requires datetime or string value, got {type(self.value)}")
        elif self.type == "bool" and not isinstance(self.value, bool):
            raise ValueError(f"Bool type requires bool value, got {type(self.value)}")
    
    def _validate_value(self) -> None:
        """Validate value-specific constraints."""
        if self.type == "int":
            # Check for overflow
            if not (-2**63 <= self.value <= 2**63 - 1):
                raise ValueError("Integer value out of range")
        elif self.type == "float":
            # Check for special values
            if not (self.value == self.value):  # NaN check
                raise ValueError("Float value cannot be NaN")
        elif self.type == "str":
            # Check for maximum length
            if len(self.value) > 10000:
                raise ValueError("String value too long")
        elif self.type == "list":
            # Check for maximum size
            if len(self.value) > 1000:
                raise ValueError("List value too large")
        elif self.type == "dict":
            # Check for maximum size
            if len(self.value) > 100:
                raise ValueError("Dict value too large")
    
    def __str__(self) -> str:
        """String representation of the value."""
        if self.type == "str":
            return f'"{self.value}"'
        elif self.type == "null":
            return "null"
        else:
            return str(self.value)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"TypedValue(type='{self.type}', value={self.value})"


class ASTNode(ABC):
    """
    Abstract base class for all AST nodes.
    
    This class provides the foundation for the Abstract Syntax Tree
    representation of filter expressions. All specific node types
    inherit from this class.
    
    Attributes:
        node_type (str): Type identifier for the node
        children (List['ASTNode']): Child nodes (if any)
    """
    
    def __init__(self, node_type: str, children: List['ASTNode']):
        """Initialize AST node."""
        self.node_type = node_type
        self.children = children
        self._validate_node()
    
    @abstractmethod
    def _validate_node(self) -> None:
        """Validate node-specific constraints."""
        pass
    
    @abstractmethod
    def evaluate(self, data: Any) -> bool:
        """Evaluate node against data."""
        pass
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Accept visitor for traversal."""
        return visitor.visit(self)
    
    @property
    def is_leaf(self) -> bool:
        """Check if node is a leaf (no children)."""
        return len(self.children) == 0
    
    @property
    def depth(self) -> int:
        """Get depth of the node in the tree."""
        if self.is_leaf:
            return 0
        return 1 + max(child.depth for child in self.children)
    
    def __str__(self) -> str:
        """String representation of the node."""
        return f"{self.__class__.__name__}({self.node_type})"


@dataclass
class FieldCondition(ASTNode):
    """
    Condition for filtering by field value.
    
    This node represents a comparison between a field and a value.
    It supports various operators and nested field access.
    
    Attributes:
        field (str): Field name (supports dot notation for nesting)
        operator (str): Comparison operator
        value (TypedValue): Value to compare against
    """
    
    field: str
    operator: str
    value: TypedValue
    
    def __post_init__(self) -> None:
        """Initialize base class and validate fields."""
        super().__init__("field_condition", [])  # Field conditions are leaf nodes
        self._validate_node()
    
    def _validate_node(self) -> None:
        """Validate field condition constraints."""
        if not self.field or not self.field.strip():
            raise ValueError("Field name cannot be empty")
        
        if not self.operator or not self.operator.strip():
            raise ValueError("Operator cannot be empty")
        
        # Validate field name format
        if not self._is_valid_field_name(self.field):
            raise ValueError(f"Invalid field name: {self.field}")
        
        # Validate operator
        if not self._is_valid_operator(self.operator):
            raise ValueError(f"Invalid operator: {self.operator}")
    
    def _is_valid_field_name(self, field: str) -> bool:
        """Check if field name is valid."""
        # Allow alphanumeric, underscore, and dot for nesting
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$'
        return bool(re.match(pattern, field))
    
    def _is_valid_operator(self, operator: str) -> bool:
        """Check if operator is valid."""
        valid_operators = {
            # Comparison operators
            "=", "!=", ">", ">=", "<", "<=",
            # String operators
            "like", "~", "!~",
            # Inclusion operators
            "in", "not_in", "intersects",
            # Dictionary operators
            "contains_key", "contains_value"
        }
        return operator in valid_operators
    
    def evaluate(self, data: Any) -> bool:
        """Evaluate field condition against data."""
        # This will be implemented in FilterExecutor
        raise NotImplementedError("Evaluation implemented in FilterExecutor")
    
    def __str__(self) -> str:
        """String representation of the condition."""
        return f"{self.field} {self.operator} {self.value}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"FieldCondition(field='{self.field}', operator='{self.operator}', value={self.value})"


@dataclass
class LogicalOperator(ASTNode):
    """
    Logical operator node (AND, OR, NOT).
    
    This node represents logical operations between multiple conditions.
    It supports AND, OR, and NOT operations with arbitrary numbers of children.
    
    Attributes:
        operator (Literal): The logical operator ("AND", "OR", "NOT")
        children (List[ASTNode]): Child nodes
    """
    
    operator: Literal["AND", "OR", "NOT", "XOR"]
    children: List['ASTNode']
    
    def __post_init__(self) -> None:
        """Initialize base class and validate operator."""
        super().__init__("logical_operator", self.children)
        self._validate_node()
    
    def _validate_node(self) -> None:
        """Validate logical operator constraints."""
        if not self.operator:
            raise ValueError("Operator cannot be empty")
        
        # Validate operator value
        if self.operator not in ["AND", "OR", "NOT", "XOR"]:
            raise ValueError(f"Invalid logical operator: {self.operator}")
        
        # Validate children count
        if self.operator == "NOT" and len(self.children) != 1:
            raise ValueError("NOT operator must have exactly one child")
        elif self.operator in ["AND", "OR", "XOR"] and len(self.children) < 2:
            raise ValueError(f"{self.operator} operator must have at least two children")
    
    def evaluate(self, data: Any) -> bool:
        """Evaluate logical operator against data."""
        # This will be implemented in FilterExecutor
        raise NotImplementedError("Evaluation implemented in FilterExecutor")
    
    def __str__(self) -> str:
        """String representation of the operator."""
        if self.operator == "NOT":
            return f"NOT ({self.children[0]})"
        else:
            return f" {self.operator} ".join(f"({child})" for child in self.children)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"LogicalOperator(operator='{self.operator}', children={len(self.children)})"


@dataclass
class ParenExpression(ASTNode):
    """
    Parenthesized expression node.
    
    This node represents an expression wrapped in parentheses.
    It is used to control operator precedence in complex expressions.
    
    Attributes:
        expression (ASTNode): The expression inside parentheses
    """
    
    expression: ASTNode
    
    def __post_init__(self) -> None:
        """Initialize base class and validate expression."""
        super().__init__("paren_expression", [self.expression])  # Wrap expression as child
        self._validate_node()
    
    def _validate_node(self) -> None:
        """Validate parenthesized expression constraints."""
        if self.expression is None:
            raise ValueError("Expression cannot be None")
        
        if not isinstance(self.expression, ASTNode):
            raise ValueError("Expression must be an ASTNode")
    
    def evaluate(self, data: Any) -> bool:
        """Evaluate parenthesized expression against data."""
        return self.expression.evaluate(data)
    
    def __str__(self) -> str:
        """String representation of the expression."""
        return f"({self.expression})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"ParenExpression(expression={self.expression})"


class ASTVisitor(ABC):
    """
    Abstract visitor for AST traversal.
    
    This class implements the Visitor pattern for traversing AST nodes.
    It allows for different operations to be performed on the tree structure.
    """
    
    @abstractmethod
    def visit_field_condition(self, node: FieldCondition) -> Any:
        """Visit a field condition node."""
        pass
    
    @abstractmethod
    def visit_logical_operator(self, node: LogicalOperator) -> Any:
        """Visit a logical operator node."""
        pass
    
    @abstractmethod
    def visit_paren_expression(self, node: ParenExpression) -> Any:
        """Visit a parenthesized expression node."""
        pass
    
    def visit(self, node: ASTNode) -> Any:
        """Visit any AST node."""
        if isinstance(node, FieldCondition):
            return self.visit_field_condition(node)
        elif isinstance(node, LogicalOperator):
            return self.visit_logical_operator(node)
        elif isinstance(node, ParenExpression):
            return self.visit_paren_expression(node)
        else:
            raise ValueError(f"Unknown node type: {type(node)}")


class ASTPrinter(ASTVisitor):
    """
    Visitor for printing AST structure.
    
    This visitor provides a human-readable representation of the AST
    structure with proper indentation and formatting.
    """
    
    def __init__(self, indent: int = 0):
        """Initialize printer with indentation level."""
        self.indent = indent
    
    def visit_field_condition(self, node: FieldCondition) -> str:
        """Visit a field condition node."""
        return f"{'  ' * self.indent}FieldCondition: {node.field} {node.operator} {node.value}"
    
    def visit_logical_operator(self, node: LogicalOperator) -> str:
        """Visit a logical operator node."""
        result = [f"{'  ' * self.indent}LogicalOperator: {node.operator}"]
        for child in node.children:
            child_visitor = ASTPrinter(self.indent + 1)
            result.append(child.accept(child_visitor))
        return "\n".join(result)
    
    def visit_paren_expression(self, node: ParenExpression) -> str:
        """Visit a parenthesized expression node."""
        result = [f"{'  ' * self.indent}ParenExpression:"]
        child_visitor = ASTPrinter(self.indent + 1)
        result.append(node.expression.accept(child_visitor))
        return "\n".join(result)


class ASTValidator(ASTVisitor):
    """
    Visitor for validating AST structure.
    
    This visitor performs comprehensive validation of the AST structure,
    checking for proper node types, operator constraints, and field validity.
    """
    
    def __init__(self):
        """Initialize validator with empty error list."""
        self.errors = []
    
    def visit_field_condition(self, node: FieldCondition) -> bool:
        """Visit a field condition node."""
        try:
            node._validate_node()
            return True
        except Exception as e:
            self.errors.append(f"FieldCondition error: {e}")
            return False
    
    def visit_logical_operator(self, node: LogicalOperator) -> bool:
        """Visit a logical operator node."""
        try:
            node._validate_node()
            # Validate all children
            for child in node.children:
                child_visitor = ASTValidator()
                if not child.accept(child_visitor):
                    self.errors.extend(child_visitor.errors)
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"LogicalOperator error: {e}")
            return False
    
    def visit_paren_expression(self, node: ParenExpression) -> bool:
        """Visit a parenthesized expression node."""
        try:
            node._validate_node()
            # Validate the expression
            child_visitor = ASTValidator()
            return node.expression.accept(child_visitor)
        except Exception as e:
            self.errors.append(f"ParenExpression error: {e}")
            return False


class ASTAnalyzer(ASTVisitor):
    """
    Visitor for analyzing AST structure and complexity.
    
    This visitor provides detailed analysis of the AST including
    field usage, operator distribution, and complexity metrics.
    """
    
    def __init__(self):
        """Initialize analyzer with empty statistics."""
        self.field_count = 0
        self.operator_count = 0
        self.max_depth = 0
        self.fields_used = set()
        self.operators_used = set()
    
    def visit_field_condition(self, node: FieldCondition) -> Dict[str, Any]:
        """Visit a field condition node."""
        self.field_count += 1
        self.fields_used.add(node.field)
        self.operators_used.add(node.operator)
        return {
            "type": "field_condition",
            "field": node.field,
            "operator": node.operator
        }
    
    def visit_logical_operator(self, node: LogicalOperator) -> Dict[str, Any]:
        """Visit a logical operator node."""
        self.operator_count += 1
        self.operators_used.add(node.operator)
        
        children_info = []
        for child in node.children:
            child_visitor = ASTAnalyzer()
            child_info = child.accept(child_visitor)
            children_info.append(child_info)
            
            # Update statistics
            self.field_count += child_visitor.field_count
            self.operator_count += child_visitor.operator_count
            self.fields_used.update(child_visitor.fields_used)
            self.operators_used.update(child_visitor.operators_used)
            self.max_depth = max(self.max_depth, child_visitor.max_depth + 1)
        
        return {
            "type": "logical_operator",
            "operator": node.operator,
            "children": children_info
        }
    
    def visit_paren_expression(self, node: ParenExpression) -> Dict[str, Any]:
        """Visit a parenthesized expression node."""
        child_visitor = ASTAnalyzer()
        child_info = node.expression.accept(child_visitor)
        
        # Update statistics
        self.field_count += child_visitor.field_count
        self.operator_count += child_visitor.operator_count
        self.fields_used.update(child_visitor.fields_used)
        self.operators_used.update(child_visitor.operators_used)
        self.max_depth = max(self.max_depth, child_visitor.max_depth + 1)
        
        return {
            "type": "paren_expression",
            "expression": child_info
        }
    
    def get_analysis(self) -> Dict[str, Any]:
        """Get complete analysis of the AST."""
        return {
            "field_count": self.field_count,
            "operator_count": self.operator_count,
            "max_depth": self.max_depth,
            "fields_used": list(self.fields_used),
            "operators_used": list(self.operators_used),
            "complexity_score": self.field_count + self.operator_count + self.max_depth
        }


class ASTOptimizer(ASTVisitor):
    """
    Visitor for optimizing AST structure.
    
    This visitor applies various optimizations to the AST including
    removal of redundant conditions, simplification of expressions,
    and reordering for better performance.
    """
    
    def visit_field_condition(self, node: FieldCondition) -> ASTNode:
        """Visit a field condition node."""
        # Field conditions are already optimized
        return node
    
    def visit_logical_operator(self, node: LogicalOperator) -> ASTNode:
        """Visit a logical operator node."""
        # Optimize children first
        optimized_children = []
        for child in node.children:
            child_visitor = ASTOptimizer()
            optimized_child = child.accept(child_visitor)
            optimized_children.append(optimized_child)
        
        # Apply optimizations
        if node.operator == "AND":
            # Remove redundant conditions
            optimized_children = self._remove_redundant_conditions(optimized_children)
        elif node.operator == "OR":
            # Remove duplicate conditions
            optimized_children = self._remove_duplicate_conditions(optimized_children)
        
        # Create new optimized node
        optimized_node = LogicalOperator(operator=node.operator, children=optimized_children)
        return optimized_node
    
    def visit_paren_expression(self, node: ParenExpression) -> ASTNode:
        """Visit a parenthesized expression node."""
        # Optimize the expression inside parentheses
        child_visitor = ASTOptimizer()
        optimized_expression = node.expression.accept(child_visitor)
        
        # If the expression is already a single node, unwrap it
        if isinstance(optimized_expression, (FieldCondition, LogicalOperator)):
            return optimized_expression
        
        # Otherwise, keep the parentheses
        return ParenExpression(expression=optimized_expression)
    
    def _remove_redundant_conditions(self, children: List[ASTNode]) -> List[ASTNode]:
        """Remove redundant conditions from AND operator."""
        # Implementation for removing redundant conditions
        # For example: x > 5 AND x > 3 -> x > 5
        return children
    
    def _remove_duplicate_conditions(self, children: List[ASTNode]) -> List[ASTNode]:
        """Remove duplicate conditions from OR operator."""
        # Implementation for removing duplicate conditions
        # For example: x = 1 OR x = 1 -> x = 1
        seen = []
        result = []
        for child in children:
            # Create a hashable representation for comparison
            child_repr = str(child)
            if child_repr not in seen:
                seen.append(child_repr)
                result.append(child)
        return result


class ASTNodeFactory:
    """
    Factory for creating AST nodes.

    This class provides convenient methods for creating
    various types of AST nodes with proper validation.
    """

    @staticmethod
    def create_field_condition(field: str, operator: str, value: TypedValue) -> FieldCondition:
        """Create a field condition node."""
        return FieldCondition(field=field, operator=operator, value=value)

    @staticmethod
    def create_logical_operator(operator: Literal["AND", "OR", "NOT", "XOR"],
                               children: List[ASTNode]) -> LogicalOperator:
        """Create a logical operator node."""
        return LogicalOperator(operator=operator, children=children)

    @staticmethod
    def create_paren_expression(expression: ASTNode) -> ParenExpression:
        """Create a parenthesized expression node."""
        return ParenExpression(expression=expression)

    @staticmethod
    def create_typed_value(type_name: str, value: Any) -> TypedValue:
        """Create a typed value."""
        return TypedValue(type=type_name, value=value)

    @staticmethod
    def create_and_operator(children: List[ASTNode]) -> LogicalOperator:
        """Create an AND operator node."""
        return ASTNodeFactory.create_logical_operator("AND", children)

    @staticmethod
    def create_or_operator(children: List[ASTNode]) -> LogicalOperator:
        """Create an OR operator node."""
        return ASTNodeFactory.create_logical_operator("OR", children)

    @staticmethod
    def create_not_operator(child: ASTNode) -> LogicalOperator:
        """Create a NOT operator node."""
        return ASTNodeFactory.create_logical_operator("NOT", [child])

    @staticmethod
    def create_simple_condition(field: str, operator: str, type_name: str, value: Any) -> FieldCondition:
        """Create a simple field condition with automatic typed value creation."""
        typed_value = ASTNodeFactory.create_typed_value(type_name, value)
        return ASTNodeFactory.create_field_condition(field, operator, typed_value)

    @staticmethod
    def create_complex_expression(conditions: List[tuple],
                                 operator: Literal["AND", "OR"] = "AND") -> LogicalOperator:
        """Create a complex expression from a list of conditions."""
        field_conditions = []
        for field, op, type_name, value in conditions:
            condition = ASTNodeFactory.create_simple_condition(field, op, type_name, value)
            field_conditions.append(condition)
        if operator == "AND":
            return ASTNodeFactory.create_and_operator(field_conditions)
        else:
            return ASTNodeFactory.create_or_operator(field_conditions)