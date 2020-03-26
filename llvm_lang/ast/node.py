import enum

from dataclasses import dataclass
from typing import List, Optional

__all__ = [
    'Op',
    'Node',
    'Program',
    'TypeExpression',
    'NamedTypeExpression',
    'TupleTypeExpression',
    'ArrayTypeExpression',
    'SliceTypeExpression',
    'Expression',
    'BinaryOperation',
    'UnaryOperation',
    'CallExpression',
    'Identifier',
    'IntegerLiteral',
    'FloatLiteral',
    'StringLiteral',
    'Statement',
    'BreakStatement',
    'ContinueStatement',
    'ReturnStatement',
    'ExpressionStatement',
    'Declaration',
    'FunctionParameter',
    'FunctionDeclaration',
    'VariableDeclaration',
    'TypeDeclaration',
    'NewTypeDeclaration',
    'StructTypeField',
    'StructTypeDeclaration',
    'EnumTypeDeclaration',
    'UnionTypeVariant',
    'UnionTypeDeclaration',
]


class Op(enum.Enum):
    assign = enum.auto()
    negate = enum.auto()
    plus = enum.auto()
    minus = enum.auto()
    times = enum.auto()
    divide = enum.auto()
    index = enum.auto()
    field = enum.auto()
    deref = enum.auto()
    ref = enum.auto()


class Node:
    pass


class Program(Node, list):
    pass


@dataclass
class TypeExpression(Node):
    pass


@dataclass
class NamedTypeExpression(TypeExpression):
    name: str
    generic_arguments: Optional[List['TypeExpression']]


@dataclass
class TupleTypeExpression(TypeExpression):
    elements: List[TypeExpression]


@dataclass
class ArrayTypeExpression(TypeExpression):
    element_type: TypeExpression
    length: int


@dataclass
class SliceTypeExpression(TypeExpression):
    element_type: TypeExpression


@dataclass
class Expression(Node):
    pass


@dataclass
class BinaryOperation(Expression):
    lhs: Expression
    op: Op
    rhs: Expression


@dataclass
class UnaryOperation(Expression):
    op: Op
    rhs: Expression


@dataclass
class CallExpression(Expression):
    target: Expression
    args: List[Expression]


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class IntegerLiteral(Expression):
    value: int


@dataclass
class FloatLiteral(Expression):
    value: float


@dataclass
class StringLiteral(Expression):
    value: str


@dataclass
class Statement(Node):
    pass


@dataclass
class BreakStatement(Statement):
    label: Optional[str]


@dataclass
class ContinueStatement(Statement):
    label: Optional[str]


@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression]


@dataclass
class ExpressionStatement(Statement):
    expr: Expression


@dataclass
class Declaration(Statement):
    name: str


@dataclass
class FunctionParameter(Node):
    name: str
    type: TypeExpression


@dataclass
class VariableDeclaration(Declaration):
    type: TypeExpression
    initializer: Optional[Expression]


@dataclass
class FunctionDeclaration(Declaration):
    return_type: TypeExpression
    generic_parameters: Optional[List[str]]
    parameters: List[FunctionParameter]
    body: List[Statement]


@dataclass
class TypeDeclaration(Declaration):
    generic_parameters: Optional[List[str]]


@dataclass
class NewTypeDeclaration(TypeDeclaration):
    inner_type: TypeExpression


@dataclass
class StructTypeField(Node):
    name: str
    type: TypeExpression


@dataclass
class StructTypeDeclaration(TypeDeclaration):
    fields: List[StructTypeField]


@dataclass
class EnumTypeDeclaration(TypeDeclaration):
    variants: List[str]


@dataclass
class UnionTypeVariant(Node):
    name: str
    type: TypeExpression


@dataclass
class UnionTypeDeclaration(TypeDeclaration):
    variants: List[UnionTypeVariant]
