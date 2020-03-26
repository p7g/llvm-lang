from ..ast import node, Visitor
from .. import ast, errors


class SemanticValidationVisitor(Visitor):
    def __init__(self):
        self.loop_count = 0
        self.function_count = 0

    def visit_FunctionDeclaration(self, node: node.FunctionDeclaration):
        self.function_count += 1
        super().generic_visit(node)
        self.function_count -= 1

    def visit_ReturnStatement(self, node):
        if self.function_count == 0:
            raise errors.SyntaxError('return outside of function')
        super().generic_visit(node)

    def _visit_loop(self, node: node.Node):
        self.loop_count += 1
        super().generic_visit(node)
        self.loop_count -= 1

    visit_WhileLoop = visit_ForLoop = visit_DoWhileLoop = _visit_loop

    def visit_BreakStatement(self, node):
        if self.loop_count == 0:
            raise errors.SyntaxError('break outside of loop')
        super().generic_visit(node)

    def visit_ContinueStatement(self, node):
        if self.loop_count == 0:
            raise errors.SyntaxError('continue outside of loop')
        super().generic_visit(node)


def validate_semantics(ctx: ast.Program) -> ast.Program:
    SemanticValidationVisitor().visit(ctx)
    return ctx
