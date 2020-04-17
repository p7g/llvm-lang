import enum
import textwrap

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from llvm_lang.types import Type

__all__ = [
    'Op',
    'Node',
    'Program',
    'TypeExpression',
    'InstantiatedTypeExpression',
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
    'TypedExpression',
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
    'GenericTypeDeclaration',
    'NewTypeDeclaration',
    'StructTypeField',
    'StructTypeDeclaration',
    'EnumTypeDeclaration',
    'UnionTypeVariant',
    'UnionTypeSymbolVariant',
    'UnionTypeTupleVariant',
    'UnionTypeStructVariant',
    'UnionTypeDeclaration',
]

INDENTATION = ' ' * 4


def indent(s: str) -> str:
    return textwrap.indent(s, INDENTATION)


class Op(enum.Enum):
    assign = enum.auto()
    negate = enum.auto()
    plus = enum.auto()
    minus = enum.auto()
    times = enum.auto()
    divide = enum.auto()
    index = enum.auto()
    field = enum.auto()

    def __str__(self):  # noqa C901
        if self == self.assign:
            return '='
        if self == self.negate:
            return '-'
        if self == self.plus:
            return '+'
        if self == self.minus:
            return '-'
        if self == self.times:
            return '*'
        if self == self.divide:
            return '/'
        if self == self.index:
            return '[]'
        if self == self.field:
            return '.'


def node(cls):
    return dataclass(frozen=True)(cls)


class Node(ABC):
    @abstractmethod
    def __str__(self) -> str:
        ...


class Program(Node, list):
    def __str__(self):
        return '\n\n'.join(map(str, self))


@node
class TypeExpression(Node, ABC):
    pass


@node
class InstantiatedTypeExpression(TypeExpression):
    type: Type

    def __str__(self):
        return str(self.type)


@node
class NamedTypeExpression(TypeExpression):
    name: str
    generic_arguments: Optional[List[TypeExpression]]

    def __str__(self):
        type_args = ''

        if self.generic_arguments:
            type_args = f'<{", ".join(map(str, self.generic_arguments))}>'

        return f'{self.name}{type_args}'


@node
class TupleTypeExpression(TypeExpression):
    elements: List[TypeExpression]

    def __str__(self):
        elements = ', '.join(map(str, self.elements))

        if len(self.elements) == 1:
            elements += ', '

        return f'({elements})'


@node
class ArrayTypeExpression(TypeExpression):
    element_type: TypeExpression
    length: int

    def __str__(self):
        return f'{self.element_type}[{self.length}]'


@node
class SliceTypeExpression(TypeExpression):
    element_type: TypeExpression

    def __str__(self):
        return f'{self.element_type}[]'


@node
class Expression(Node, ABC):
    pass


@node
class TypedExpression(Expression):
    value: Expression
    type: Type

    def __str__(self):
        return f'({self.value})::{self.type}'

    def __post_init__(self):
        if not isinstance(self.type, Type):
            raise ValueError(repr(self))


@node
class BinaryOperation(Expression):
    lhs: Expression
    op: Op
    rhs: Expression

    def __str__(self):
        if self.op == Op.index:
            return f'{self.lhs}[{self.rhs}]'
        if self.op == Op.field:
            return f'{self.lhs}.{self.rhs}'
        return f'{self.lhs} {self.op} {self.rhs}'


@node
class UnaryOperation(Expression):
    op: Op
    rhs: Expression

    def __str__(self):
        return f'{self.op} {self.rhs}'


@node
class CallExpression(Expression):
    target: Expression
    args: List[Expression]

    def __str__(self):
        target = self.target
        if isinstance(target, TypedExpression):
            target = target.value
        return f'{target}({", ".join(map(str, self.args))})'


@node
class Identifier(Expression):
    name: str

    def __str__(self):
        return self.name


@node
class IntegerLiteral(Expression):
    value: int

    def __str__(self):
        return str(self.value)


@node
class FloatLiteral(Expression):
    value: float

    def __str__(self):
        return str(self.value)


@node
class StringLiteral(Expression):
    value: str

    def __str__(self):
        return f'"{self.value}"'


@node
class Statement(Node, ABC):
    pass


@node
class BreakStatement(Statement):
    label: Optional[str]

    def __str__(self):
        return 'break;'


@node
class ContinueStatement(Statement):
    label: Optional[str]

    def __str__(self):
        return 'continue;'


@node
class ReturnStatement(Statement):
    value: Optional[Expression]

    def __str__(self):
        retval = ''

        if self.value is not None:
            retval = f' {self.value}'

        return f'return{retval};'


@node
class ExpressionStatement(Statement):
    expr: Expression

    def __str__(self):
        return f'{self.expr};'


@node
class Declaration(Statement, ABC):
    name: str


@node
class FunctionParameter(Node):
    name: str
    type: TypeExpression

    def __str__(self):
        return f'{self.name}: {self.type}'


@node
class VariableDeclaration(Declaration):
    type: TypeExpression
    initializer: Expression

    def __str__(self):
        return f'let {self.name}: {self.type} = {self.initializer};'


@node
class FunctionDeclaration(Declaration):
    return_type: TypeExpression
    generic_parameters: Optional[List[str]]
    parameters: List[FunctionParameter]
    body: List[Statement]

    def __str__(self):
        params = ", ".join(map(str, self.parameters))
        type_params = ''

        if self.generic_parameters is not None:
            type_params = f'<{", ".join(self.generic_parameters)}>'

        body = indent('\n'.join(map(str, self.body)))

        return (
            f'function {self.name}{type_params}({params}): {self.return_type} '
            f'{{\n{body}\n}}')


@node
class TypeDeclaration(Declaration, ABC):
    pass


@node
class EnumTypeDeclaration(TypeDeclaration):
    variants: List[str]

    def __str__(self):
        body = indent('\n'.join(self.variants))
        return f'enum {self.name} {{\n{body}\n}}'


@node
class GenericTypeDeclaration(TypeDeclaration, ABC):
    generic_parameters: Optional[List[str]]

    def __str__(self):
        if self.generic_parameters:
            return f'<{", ".join(self.generic_parameters)}>'
        return ''


@node
class NewTypeDeclaration(GenericTypeDeclaration):
    inner_type: TypeExpression

    def __str__(self):
        params = super().__str__()
        return f'newtype {self.name}{params} = {self.inner_type};'


@node
class StructTypeField(Node):
    name: str
    type: TypeExpression

    def __str__(self):
        return f'{self.name}: {self.type}'


@node
class StructTypeDeclaration(GenericTypeDeclaration):
    fields: List[StructTypeField]

    def __str__(self):
        body = indent('\n'.join(map(str, self.fields)))
        return f'struct {self.name}{super().__str__()} {{\n{body}\n}}'


@node
class UnionTypeVariant(Node, ABC):
    name: str


@node
class UnionTypeStructVariant(UnionTypeVariant):
    fields: List[StructTypeField]

    def __str__(self):
        body = indent('\n'.join(map(str, self.fields)))
        return f'{self.name} {{\n{body}\n}}'


@node
class UnionTypeTupleVariant(UnionTypeVariant):
    elements: List[TypeExpression]

    def __str__(self):
        return f'{self.name}({", ".join(map(str, self.elements))})'


@node
class UnionTypeSymbolVariant(UnionTypeVariant):
    def __str__(self):
        return self.name


@node
class UnionTypeDeclaration(GenericTypeDeclaration):
    variants: List[UnionTypeVariant]

    def __str__(self):
        body = indent('\n'.join(map(str, self.variants)))
        return f'union {self.name}{super().__str__()} {{\n{body}\n}}'
