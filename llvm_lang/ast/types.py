from functools import singledispatch

from llvm_lang import ast, types


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
