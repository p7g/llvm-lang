from dataclasses import dataclass
from typing import Dict

from llvm_lang import ast, types, errors
from llvm_lang.ast.map import MapAST
from llvm_lang.types.instantiate import instantiate as instantiate_type
from llvm_lang.scopes import Scopes

from .annotate_expressions import AnnotateExpressionsContext


@dataclass
class InstantiateTypeExpressionsContext:
    ast_root: ast.Program
    declared_types: Dict[str, types.Type]


class InstantiateTypeExpressionsVisitor(MapAST):
    def __init__(self, ctx: AnnotateExpressionsContext):
        super().__init__()
        self.ctx = ctx
        self.scopes = Scopes(ctx.declared_types.items())

    def visit_NamedTypeExpression(self, node: ast.NamedTypeExpression):
        typ = self.scopes.resolve_binding(node.name)

        if isinstance(typ, types.ScopedType):
            generic_arguments = {
                name: self.visit(arg)
                for name, arg in zip(typ.type_parameters,
                                     node.generic_arguments or [])
            }
        else:
            generic_arguments = {}
        return ast.InstantiatedTypeExpression(
            type=instantiate_type(typ, generic_arguments, self.scopes))

    def visit_TypedExpression(self, node: ast.TypedExpression):
        print(repr(node.type))
        return ast.TypedExpression(value=self.visit(node.value),
                                   type=instantiate_type(
                                       node.type, {}, self.scopes))

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        if node.generic_parameters:
            raise NotImplementedError()
        return super().visit_FunctionDeclaration(node)

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
