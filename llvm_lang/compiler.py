from dataclasses import dataclass
from functools import reduce
from typing import List

from .passes import Pass
from .passes.parse import parse
from .passes.validate_semantics import validate_semantics
from .passes.resolve_declared_types import resolve_declared_types
from .passes.annotate_expressions import annotate_expressions
from .passes.instantiate_type_expressions import instantiate_type_expressions
from .passes.check_types import check_types


@dataclass
class Compiler:
    passes: List[Pass]

    def compile(self, input_: str):
        return reduce(lambda acc, pass_: pass_(acc), self.passes, input_)


passes = (
    parse,
    validate_semantics,
    resolve_declared_types,
    annotate_expressions,
    instantiate_type_expressions,
    check_types,
)

compiler = Compiler(passes=passes)
