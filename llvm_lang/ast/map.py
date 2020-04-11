from llvm_lang import ast
from llvm_lang.ast.utils import expect_all_concrete_nodes


class MapAST(ast.Visitor):
    def visit_Program(self, node: ast.Program):
        return ast.Program(map(self.visit, node))

    def visit_NamedTypeExpression(self, node: ast.NamedTypeExpression):
        generic_arguments = None
        if node.generic_arguments is not None:
            generic_arguments = [
                self.visit(arg) for arg in node.generic_arguments
            ]
        return ast.NamedTypeExpression(name=node.name,
                                       generic_arguments=generic_arguments)

    def visit_TupleTypeExpression(self, node: ast.TupleTypeExpression):
        return ast.TupleTypeExpression(
            elements=[self.visit(n) for n in node.elements])

    def visit_ArrayTypeExpression(self, node: ast.ArrayTypeExpression):
        return ast.ArrayTypeExpression(element_type=self.visit(
            node.element_type),
                                       length=node.length)

    def visit_SliceTypeExpression(self, node: ast.SliceTypeExpression):
        return ast.SliceTypeExpression(
            element_type=self.visit(node.element_type))

    def visit_TypedExpression(self, node: ast.TypedExpression):
        return ast.TypedExpression(value=self.visit(node.value),
                                   type=node.type)

    def visit_BinaryOperation(self, node: ast.BinaryOperation):
        return ast.BinaryOperation(lhs=self.visit(node.lhs),
                                   op=node.op,
                                   rhs=self.visit(node.rhs))

    def visit_UnaryOperation(self, node: ast.UnaryOperation):
        return ast.UnaryOperation(op=node.op, rhs=self.visit(node.rhs))

    def visit_CallExpression(self, node: ast.CallExpression):
        return ast.CallExpression(target=self.visit(node.target),
                                  args=[self.visit(a) for a in node.args])

    def visit_ReturnStatement(self, node: ast.ReturnStatement):
        value = None if node.value is None else self.visit(node.value)
        return ast.ReturnStatement(value=value)

    def visit_ExpressionStatement(self, node: ast.ExpressionStatement):
        return ast.ExpressionStatement(expr=self.visit(node.expr))

    def visit_FunctionParameter(self, node: ast.FunctionParameter):
        return ast.FunctionParameter(name=node.name,
                                     type=self.visit(node.type))

    def _visit_generic_parameters(self, node: ast.GenericTypeDeclaration):
        if node.generic_parameters is None:
            return None
        return [self.visit(p) for p in node.generic_parameters]

    def visit_FunctionDeclaration(self, node: ast.FunctionDeclaration):
        return ast.FunctionDeclaration(
            name=node.name,
            return_type=self.visit(node.return_type),
            generic_parameters=self._visit_generic_parameters(node),
            parameters=[self.visit(p) for p in node.parameters],
            body=[self.visit(s) for s in node.body])

    def visit_NewTypeDeclaration(self, node: ast.NewTypeDeclaration):
        return ast.NewTypeDeclaration(
            name=node.name,
            generic_parameters=self._visit_generic_parameters(node),
            inner_type=self.visit(node.inner_type))

    def visit_StructTypeField(self, node: ast.StructTypeField):
        return ast.StructTypeField(name=node.name, type=self.visit(node.type))

    def visit_StructTypeDeclaration(self, node: ast.StructTypeDeclaration):
        return ast.StructTypeDeclaration(
            name=node.name,
            generic_parameters=self._visit_generic_parameters(node),
            fields=[self.visit(f) for f in node.fields])

    def visit_UnionTypeStructVariant(self, node: ast.UnionTypeStructVariant):
        return ast.UnionTypeStructVariant(
            name=node.name, fields=[self.visit(f) for f in node.fields])

    def visit_UnionTypeTupleVariant(self, node: ast.UnionTypeTupleVariant):
        return ast.UnionTypeTupleVariant(
            name=node.name, elements=[self.visit(e) for e in node.elements])

    def visit_UnionTypeDeclaration(self, node: ast.UnionTypeDeclaration):
        return ast.UnionTypeDeclaration(
            name=node.name,
            generic_parameters=self._visit_generic_parameters(node),
            variants=[self.visit(v) for v in node.variants])

    def generic_visit(self, node: ast.Node):
        return node


expect_all_concrete_nodes('MapAST',
                          lambda ty: hasattr(MapAST, f'visit_{ty.__name__}'))
