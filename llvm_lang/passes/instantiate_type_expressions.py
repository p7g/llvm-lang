from dataclasses import dataclass
from typing import Dict

from .. import ast, types, errors
from llvm_lang.ast.map import MapAST

from .resolve_declared_types import ResolveDeclaredTypesContext


@dataclass
class InstantiateTypeExpressionsContext:
    ast_root: ast.Program
    instantiated_types: Dict[ast.TypeExpression, types.Type]


class Scopes:
    def __init__(self):
        self.scopes = []

    def push_scope(self):
        self.scopes.append(set())

    def pop_scope(self):
        self.scopes.pop()

    def insert_binding(self, name: str):
        self.scopes[-1].add(name)

    def has_binding(self, name: str):
        for scope in self.scopes:
            if name in scope:
                return True
        return False


primitive_types = ('Boolean', )


class InstantiateTypeExpressionsVisitor(MapAST):
    def __init__(self):
        super().__init__()
        self.instantiated_types = {}
        self.scopes = Scopes()

    def visit_NamedTypeExpression(self, node: ast.NamedTypeExpression):
        if node.name in primitive_types:
            if len(node.generic_arguments) != 0:
                raise errors.TypeError(f'Type {node.name} is not generic')
            self.instantiated_types[node] = None

    def generic_visit(self, node: ast.Node):
        if isinstance(node, ast.TypeExpression):
            raise NotImplementedError(
                'Missing InstantiateTypeExpressionsVisitor implementation for'
                f' {type(node).__name__}')
        super().generic_visit(node)


def instantiate_type_expressions(
        ctx: ResolveDeclaredTypesContext) -> InstantiateTypeExpressionsContext:
    return InstantiateTypeExpressionsContext(ast_root=ctx,
                                             instantiated_types={})
