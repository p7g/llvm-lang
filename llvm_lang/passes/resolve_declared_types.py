from dataclasses import dataclass
from typing import List

from llvm_lang import ast, types
from llvm_lang.ast.types import generate_type


@dataclass
class DeclaredType:
    name: str
    type: types.Type


@dataclass
class ResolveDeclaredTypesContext:
    ast_root: ast.Program
    declared_types: List[DeclaredType]


class ResolveDeclaredTypesVisitor(ast.Visitor):
    def __init__(self):
        super().__init__()
        self.declared_types = []

    def visit_NewTypeDeclaration(self, node: ast.NewTypeDeclaration):
        self.declared_types.append(
            DeclaredType(name=node.name,
                         type=types.NewType(
                             name=node.name,
                             inner_type=generate_type(node.inner_type),
                             type_parameters=tuple(
                                 map(types.TypeVariable,
                                     node.generic_parameters)))))

    def visit_StructTypeDeclaration(self, node: ast.StructTypeDeclaration):
        type_parameters = tuple(
            map(types.TypeVariable, node.generic_parameters))
        fields = []

        for field in node.fields:
            fields.append((field.name, generate_type(field.type)))

        self.declared_types.append(
            DeclaredType(name=node.name,
                         type=types.StructType(name=node.name,
                                               type_parameters=type_parameters,
                                               fields=tuple(fields))))

    def visit_UnionTypeDeclaration(self, node: ast.UnionTypeDeclaration):
        type_parameters = tuple(
            map(types.TypeVariable, node.generic_parameters))
        variants = []

        for variant in node.variants:
            # FIXME: Need to fix type of UnionType.variants
            variants.append((variant.name, types.TypeRef("T",
                                                         type_arguments=())))

        self.declared_types.append(
            DeclaredType(name=node.name,
                         type=types.UnionType(name=node.name,
                                              type_parameters=type_parameters,
                                              variants=tuple(variants))))

    def visit_EnumTypeDeclaration(self, node: ast.EnumTypeDeclaration):
        self.declared_types.append(
            DeclaredType(name=node.name,
                         type=types.EnumType(name=node.name,
                                             variants=tuple(node.variants))))

    def generic_visit(self, node: ast.Node):
        if not isinstance(node, ast.TypeDeclaration):
            super().generic_visit(node)
            return

        raise NotImplementedError(
            f'Unsupported type declaration type "{type(node).__name__}"')


def resolve_declared_types(ctx: ast.Program) -> ResolveDeclaredTypesContext:
    visitor = ResolveDeclaredTypesVisitor()
    visitor.visit(ctx)

    return ResolveDeclaredTypesContext(ast_root=ctx,
                                       declared_types=visitor.declared_types)
