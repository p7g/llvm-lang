import enum

from dataclasses import dataclass
from typing import List, Tuple


class Op(enum.Enum):
    assign = enum.auto()
    negate = enum.auto()
    plus = enum.auto()
    minus = enum.auto()
    times = enum.auto()
    divide = enum.auto()
    index = enum.auto()
    deref = enum.auto()
    ref = enum.auto()


@dataclass
class Expression:
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
class Type:
    pass


@dataclass
class Statement:
    pass


@dataclass
class ExpressionStatement(Statement):
    expr: Expression


@dataclass
class Declaration(Statement):
    pass


@dataclass
class FunctionDeclaration(Declaration):
    name: Identifier
    return_type: Type
    arguments: List[Tuple[Identifier, Type]]
