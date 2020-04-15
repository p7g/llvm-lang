from functools import singledispatch
from operator import itemgetter

from llvm_lang import ast, types, errors
from llvm_lang.ast import Op
from llvm_lang.types import primitive_types as p
from llvm_lang.scopes import Scopes


@singledispatch
def generate_type(node: ast.TypeExpression):
    raise NotImplementedError(type(node).__name__)


@generate_type.register
def generate_type_namedtypeexpression(node: ast.NamedTypeExpression):
    if node.generic_arguments is None:
        generic_arguments = ()
    else:
        generic_arguments = tuple(map(generate_type, node.generic_arguments))
    return types.TypeRef(node.name, type_arguments=generic_arguments)


@generate_type.register
def generate_type_tupletypeexpression(node: ast.TupleTypeExpression):
    return types.TupleType(elements=tuple(map(generate_type, node.elements)))


@generate_type.register
def generate_type_arraytypeexpression(node: ast.ArrayTypeExpression):
    return types.ArrayType(element_type=generate_type(node.element_type),
                           length=node.length)


@generate_type.register
def generate_type_slicetypeexpression(node: ast.SliceTypeExpression):
    return types.SliceType(element_type=generate_type(node.element_type))


@singledispatch
def infer_type(node: ast.Expression, scopes: Scopes) -> types.Type:
    '''Infer the type of an expression'''
    raise NotImplementedError()


@infer_type.register
def infer_type_typedexpression(node: ast.TypedExpression,
                               scopes: Scopes) -> types.Type:
    return node.type


@infer_type.register
def infer_type_identifier(node: ast.Identifier, scopes: Scopes) -> types.Type:
    return scopes.resolve_binding(node.name)


@infer_type.register
def infer_type_integerliteral(node: ast.IntegerLiteral,
                              scopes: Scopes) -> types.Type:
    return p['int64']


@infer_type.register
def infer_type_floatliteral(node: ast.FloatLiteral,
                            scopes: Scopes) -> types.Type:
    return p['float64']


@infer_type.register
def infer_type_stringliteral(node: ast.StringLiteral,
                             scopes: Scopes) -> types.Type:
    return types.ArrayType(length=len(node.value.encode('utf-8')),
                           element_type=p['uint8'])


@infer_type.register
def infer_type_binaryoperation(
        node: ast.BinaryOperation,  # noqa C901
        scopes: Scopes) -> types.Type:
    lhs_type = infer_type(node.lhs)

    if node.op in (Op.plus, Op.minus, Op.times, Op.divide):
        if lhs_type != infer_type(node.rhs):
            raise errors.TypeError(
                f'Both sides of "{node.op}" must have the same type')
        if not isinstance(lhs_type, (types.IntType, types.FloatType)):
            raise errors.TypeError(
                f'Operands of "{node.op}" must be numeric, got "{lhs_type}"')
        return lhs_type
    elif node.op == Op.field:
        if not isinstance(lhs_type, types.StructType):
            raise errors.TypeError(
                f'Cannot access field "{node.rhs}" of non-struct type'
                f' {lhs_type}')
        for name, typ in lhs_type.fields:
            if name == node.rhs.name:
                return typ
        raise errors.TypeError(
            f'Struct type {lhs_type} has no field "{node.rhs}"')
    elif node.op == Op.index:
        if not isinstance(lhs_type, (types.ArrayType, types.SliceType)):
            raise errors.TypeError(f'Type {lhs_type} cannot be indexed')
        rhs_type = infer_type(node.rhs)
        if not isinstance(rhs_type, types.IntType):
            raise errors.TypeError(f'Cannot index {lhs_type} with {rhs_type}')
        return lhs_type.element_type
    elif node.op == Op.assign:
        if (not isinstance(node.lhs, (ast.Identifier, ast.BinaryOperation))
                or (isinstance(node.lhs, ast.BinaryOperation)
                    and node.op not in (Op.assign, Op.index, Op.field))):
            raise errors.SyntaxError(f'Invalid assignment target {node.lhs}')
        return rhs_type
    else:
        raise NotImplementedError()


@infer_type.register
def infer_type_unaryoperation(node: ast.UnaryOperation,
                              scopes: Scopes) -> types.Type:
    return infer_type(node.rhs)


@infer_type.register
def infer_type_callexpression(node: ast.CallExpression,
                              scopes: Scopes) -> types.Type:
    fn_type = infer_type(node.target)

    if not isinstance(fn_type, types.FunctionType):
        raise errors.TypeError(f'{node.target} is not a function')

    arg_types = list(map(infer_type, node.args))

    for arg, param in zip(arg_types, map(itemgetter(1), fn_type.parameters)):
        if arg != param:
            raise TypeError(f'Type {arg} is not assignable to {param}')

    return fn_type.return_type
