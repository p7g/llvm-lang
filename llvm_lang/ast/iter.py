from functools import singledispatch
from typing import Union

from . import node
from .utils import assert_all_registered

__all__ = ('iter_node', )


def iter_node_not_implemented(node):
    raise NotImplementedError(type(node).__name__)


iter_node = singledispatch(iter_node_not_implemented)

for typ in (node.Node, node.Expression, node.Statement, node.TypeExpression,
            node.Declaration, node.TypeDeclaration):
    iter_node.register(typ)(iter_node_not_implemented)


@iter_node.register(node.Identifier)
@iter_node.register(node.IntegerLiteral)
@iter_node.register(node.FloatLiteral)
@iter_node.register(node.StringLiteral)
@iter_node.register(node.EnumTypeDeclaration)
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
    return node.element_type


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

    if node.generic_parameters:
        for typeparam in node.generic_parameters:
            yield typeparam

    for param in node.parameters:
        yield param

    for stmt in node.body:
        yield stmt


@iter_node.register
def iter_node_variabledeclaration(node: node.VariableDeclaration):
    yield node.type

    if node.initializer:
        yield node.initializer


@iter_node.register
def iter_node_newtypedeclaration(node: node.NewTypeDeclaration):
    if node.generic_parameters:
        for param in node.generic_parameters:
            yield param

    yield node.inner_type


@iter_node.register
def iter_node_structtypefield(node: node.StructTypeField):
    yield node.type


@iter_node.register
def iter_node_structtypedeclaration(node: node.StructTypeDeclaration):
    if node.generic_parameters:
        for param in node.generic_parameters:
            yield param

    for field in node.fields:
        yield field


@iter_node.register
def iter_node_uniontypevariant(node: node.UnionTypeVariant):
    yield node.type


@iter_node.register
def iter_node_uniontypedeclaration(node: node.UnionTypeDeclaration):
    if node.generic_parameters:
        for param in node.generic_parameters:
            yield param

    for variant in node.variants:
        yield variant


assert_all_registered(iter_node)
