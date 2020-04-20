from dataclasses import dataclass
from typing import Dict

from llvm_lang import ast, types
from llvm_lang.ast.map import MapAST
from llvm_lang.ast.types import generate_type, infer_type
from llvm_lang.scopes import Scopes

from .resolve_declared_types import ResolveDeclaredTypesContext


@dataclass
class AnnotateExpressionsContext:
    ast_root: ast.Program
    declared_types: Dict[str, types.Type]


class AnnotateExpressionsVisitor(MapAST):
    def __init__(self, ctx: ResolveDeclaredTypesContext):
        self.ctx = ctx
        self.scopes = Scopes[types.Type]()

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        self.scopes.add_binding(node.name, self.ctx.declared_types[node.name])
        with self.scopes.new_scope():
            result = super().visit_FunctionDeclaration(node)
        return result

    def visit_VariableDeclaration(self, node: ast.VariableDeclaration):
        initializer = super().visit(node.initializer)
        self.scopes.add_binding(node.name, generate_type(node.type))
        return ast.VariableDeclaration(name=node.name,
                                       type=node.type,
                                       initializer=initializer)

    # FIXME: add other statements
    # def visit_IfStatement(self, node: ast.IfStatement):
    #     with self.scopes.new_scope():
    #         super().visit_IfStatement(node)

    def visit_Expression(self, node: ast.Expression):
        return ast.TypedExpression(value=node,
                                   type=infer_type(node, self.scopes))


def annotate_expressions(
        ctx: ResolveDeclaredTypesContext) -> AnnotateExpressionsContext:
    return AnnotateExpressionsContext(
        ast_root=AnnotateExpressionsVisitor(ctx).visit(ctx.ast_root),
        declared_types=ctx.declared_types)
