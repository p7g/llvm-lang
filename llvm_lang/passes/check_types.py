from dataclasses import dataclass
from typing import Dict, List

from llvm_lang import ast, types, errors
from llvm_lang.ast import Visitor
from llvm_lang.passes.instantiate_type_expressions import \
    InstantiateTypeExpressionsContext


@dataclass
class CheckTypesContext:
    ast_root: ast.Program
    declared_types: Dict[str, types.Type]


class CheckTypesVisitor(Visitor):
    def __init__(self, ctx: InstantiateTypeExpressionsContext):
        super().__init__()
        self.ctx = ctx
        self.function_stack: List[ast.FunctionDeclaration] = []

    @property
    def current_function(self):
        return self.function_stack[-1]

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        self.function_stack.append(node)
        super().generic_visit(node)
        self.function_stack.pop()

    def visit_ReturnStatement(self, node: ast.ReturnStatement):
        if node.value is not None:
            assert isinstance(node.value, ast.TypedExpression)
            if node.value.type != self.current_function.return_type.type:
                raise errors.TypeError(
                    f'Returned value {node.value} is not '
                    f'assignable to type {self.current_function.return_type}')
        elif self.current_function.return_type is not None:
            raise errors.TypeError(
                'Cannot return void from function that '
                f'returns {self.current_function.return_type}')

    def visit_VariableDeclaration(self, node: ast.VariableDeclaration):
        assert isinstance(node.initializer, ast.TypedExpression)
        assert isinstance(node.type, ast.InstantiatedTypeExpression)
        if node.initializer.type != node.type.type:
            raise errors.TypeError(f'Cannot assign {node.initializer} to '
                                   f'variable of type {node.type.type}')

    def visit_CallExpression(self, node: ast.CallExpression):
        assert isinstance(node.target, ast.TypedExpression)
        fn_type = node.target.type

        args_len = len(node.args)
        params_len = len(fn_type.parameters)
        if args_len != params_len:
            raise errors.TypeError(f'Expected {params_len} arguments to '
                                   f'{fn_type.name}, got {args_len}')

        for i, argument in enumerate(node.args):
            assert isinstance(argument, ast.TypedExpression)
            param_type = fn_type.parameters[i][1]
            if argument.type != param_type:
                raise errors.TypeError('Cannot pass expression of type '
                                       f'{argument.type} as argument {i + 1} '
                                       f'of {fn_type.name}, expected '
                                       f'expression of type {param_type}')


def check_types(ctx: InstantiateTypeExpressionsContext) -> CheckTypesContext:
    CheckTypesVisitor(ctx).visit(ctx.ast_root)
    return CheckTypesContext(ast_root=ctx.ast_root,
                             declared_types=ctx.declared_types)
