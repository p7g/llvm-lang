from dataclasses import dataclass
from typing import Dict

from .resolve_declared_types import ResolveDeclaredTypesContext
from .. import ast, types


@dataclass
class InstantiateTypeExpressionsContext:
    ast_root: ast.Program
    declared_types: Dict[str, types.Type]


# should probably instead be instantiate_type_expressions and result in a CST
def instantiate_type_expressions(
        ctx: ResolveDeclaredTypesContext) -> InstantiateTypeExpressionsContext:
    pass
