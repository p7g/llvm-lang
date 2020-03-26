from dataclasses import dataclass
from functools import reduce
from typing import List

from .passes import Pass
from .passes.parse import parse
from .passes.validate_semantics import validate_semantics
from .passes.resolve_declared_types import resolve_declared_types


@dataclass
class Compiler:
    passes: List[Pass]

    def compile(self, input_: str):
        return reduce(lambda acc, pass_: pass_(acc), self.passes, input_)


passes = (
    parse,
    validate_semantics,
    resolve_declared_types,
)

compiler = Compiler(passes=passes)
