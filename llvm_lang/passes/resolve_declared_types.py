from dataclasses import dataclass
from typing import List

from .. import ast


@dataclass
class DeclaredType:
    name: str
    type_param_count: int


@dataclass
class ResolveDeclaredTypesContext:
    ast_root: ast.Program
    declared_types: List[DeclaredType]


def resolve_declared_types(ctx: ast.Program) -> ResolveDeclaredTypesContext:
    next_context = ResolveDeclaredTypesContext(ast_root=ctx, declared_types=[])

    for declaration in ctx:
        if not isinstance(declaration, ast.TypeDeclaration):
            continue

        type_param_count = 0
        if declaration.generic_parameters:
            type_param_count = len(declaration.generic_parameters)

        next_context.declared_types.append(
            DeclaredType(name=declaration.name,
                         type_param_count=type_param_count))

    return next_context
