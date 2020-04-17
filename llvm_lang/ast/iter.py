from functools import singledispatch
from typing import Union

from . import node
from .utils import assert_all_registered

__all__ = ('iter_node', )


def iter_node_not_implemented(node):
    raise NotImplementedError(type(node).__name__)


iter_node = singledispatch(iter_node_not_implemented)

for typ in (node.Node, node.Expression, node.Statement, node.TypeExpression,
            node.Declaration, node.TypeDeclaration, node.UnionTypeVariant,
            node.GenericTypeDeclaration):
    iter_node.register(typ)(iter_node_not_implemented)


@iter_node.register(node.Identifier)
@iter_node.register(node.IntegerLiteral)
@iter_node.register(node.FloatLiteral)
@iter_node.register(node.StringLiteral)
@iter_node.register(node.EnumTypeDeclaration)
@iter_node.register(node.UnionTypeSymbolVariant)
@iter_node.register(node.InstantiatedTypeExpression)
def iter_node_no_fields(node):
    return []


@iter_node.register
def iter_node_program(node: node.Program):
    for child in node:
        yield child


@iter_node.register
def iter_node_namedtypeexpression(node: node.NamedTypeExpression):
    if node.generic_arguments:
        for arg in node.generic_arguments:
            yield arg


@iter_node.register
def iter_node_tupletypeexpression(node: node.TupleTypeExpression):
    for arg in node.elements:
        yield arg


@iter_node.register(node.ArrayTypeExpression)
@iter_node.register(node.SliceTypeExpression)
def iter_node_arraytypeexpression(node: Union[node.ArrayTypeExpression,
                                              node.SliceTypeExpression]):
    yield node.element_type


@iter_node.register
def iter_node_binaryoperation(node: node.BinaryOperation):
    yield node.lhs
    yield node.rhs


@iter_node.register
def iter_node_unaryoperation(node: node.UnaryOperation):
    yield node.rhs


@iter_node.register
def iter_node_callexperession(node: node.CallExpression):
    yield node.target

    for arg in node.args:
        yield arg


@iter_node.register
def iter_node_breakstatement(node: node.BreakStatement):
    return []


@iter_node.register
def iter_node_continuestatment(node: node.ContinueStatement):
    return []


@iter_node.register
def iter_node_returnstatement(node: node.ReturnStatement):
    if node.value:
        yield node.value


@iter_node.register
def iter_node_expressionstatement(node: node.ExpressionStatement):
    yield node.expr


@iter_node.register
def iter_node_functionparameter(node: node.FunctionParameter):
    yield node.type


@iter_node.register
def iter_node_functiondeclaration(node: node.FunctionDeclaration):
    yield node.return_type

    for param in node.parameters:
        yield param

    for stmt in node.body:
        yield stmt


@iter_node.register
def iter_node_variabledeclaration(node: node.VariableDeclaration):
    yield node.type
    yield node.initializer


@iter_node.register
def iter_node_newtypedeclaration(node: node.NewTypeDeclaration):
    yield node.inner_type


@iter_node.register
def iter_node_structtypefield(node: node.StructTypeField):
    yield node.type


@iter_node.register
def iter_node_structtypedeclaration(node: node.StructTypeDeclaration):
    for field in node.fields:
        yield field


@iter_node.register
def iter_node_uniontypetuplevariant(node: node.UnionTypeTupleVariant):
    for element_type in node.elements:
        yield element_type


@iter_node.register
def iter_node_uniontypestructvariant(node: node.UnionTypeStructVariant):
    for field in node.fields:
        yield field


@iter_node.register
def iter_node_uniontypedeclaration(node: node.UnionTypeDeclaration):
    for variant in node.variants:
        yield variant


assert_all_registered(iter_node)
