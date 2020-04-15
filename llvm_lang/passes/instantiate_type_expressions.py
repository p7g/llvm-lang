from dataclasses import dataclass
from typing import Dict

from llvm_lang import ast, types, errors
from llvm_lang.ast.map import MapAST
from llvm_lang.types.instantiate import instantiate as instantiate_type
from llvm_lang.utils import identity

from .annotate_expressions import AnnotateExpressionsContext


@dataclass
class InstantiateTypeExpressionsContext:
    ast_root: ast.Program
    declared_types: Dict[str, types.Type]


class InstantiateTypeExpressionsVisitor(MapAST):
    def __init__(self, ctx: AnnotateExpressionsContext):
        super().__init__()
        self.ctx = ctx

    def visit_NamedTypeExpression(self, node: ast.NamedTypeExpression):
        if node.name in types.primitive_types:
            if node.generic_arguments:
                raise errors.TypeError(f'Type {node.name} is not generic')
            return ast.InstantiatedTypeExpression(
                type=types.primitive_types[node.name])
        elif node.name in self.ctx.declared_types:
            typ = self.ctx.declared_types[node.name]
            if isinstance(typ, types.ScopedType):
                generic_arguments = {
                    name: self.visit(arg)
                    for name, arg in zip(typ.type_parameters,
                                         node.generic_arguments or [])
                }
            else:
                generic_arguments = {}
            return ast.InstantiatedTypeExpression(
                type=instantiate_type(typ, generic_arguments))
        raise errors.ReferenceError(f'type "{node.name}" not found')

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        if node.generic_parameters:
            return node
        return super().visit_FunctionDeclaration(node)

    visit_NewTypeDeclaration = \
        visit_StructTypeDeclaration = \
        visit_UnionTypeDeclaration = \
        visit_EnumTypeDeclaration = \
        identity

    def generic_visit(self, node: ast.Node):
        if isinstance(node, ast.TypeExpression):
            raise NotImplementedError(
                'Missing InstantiateTypeExpressionsVisitor implementation for'
                f' {type(node).__name__}')
        elif isinstance(node, ast.TypeDeclaration):
            # declarations will be instantiated when they're used or something
            # I guess
            return node
        return super().generic_visit(node)


def instantiate_type_expressions(
        ctx: AnnotateExpressionsContext) -> InstantiateTypeExpressionsContext:
    visitor = InstantiateTypeExpressionsVisitor(ctx)
    return InstantiateTypeExpressionsContext(ast_root=visitor.visit(
        ctx.ast_root),
                                             declared_types=ctx.declared_types)
