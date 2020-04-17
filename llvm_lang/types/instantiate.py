from functools import singledispatch
from itertools import zip_longest
from typing import Dict, Iterable

from llvm_lang import types, errors
from llvm_lang.scopes import Scopes

TypeMap = Dict[types.TypeVariable, types.Type]


def instantiate(ty: types.Type, arguments: TypeMap,
                scopes: Scopes) -> types.Type:
    if isinstance(ty, types.ScopedType):
        if ty.type_arguments:
            type_arguments = (arguments.get(t, t) if isinstance(
                t, types.TypeVariable) else instantiate(t, arguments, scopes)
                              for t in ty.type_arguments)
        else:
            type_arguments = arguments.values()
        return instantiate_scoped(ty, type_arguments, scopes)

    return instantiate_unscoped(ty, arguments, scopes)


@singledispatch
def instantiate_unscoped(ty: types.Type, arguments: TypeMap,
                         scopes: Scopes) -> types.Type:
    raise NotImplementedError(type(ty).__name__)


@instantiate_unscoped.register(types.BoolType)
@instantiate_unscoped.register(types.IntType)
@instantiate_unscoped.register(types.FloatType)
@instantiate_unscoped.register(types.SymbolType)
@instantiate_unscoped.register(types.EnumType)
@instantiate_unscoped.register(types.VoidType)
def instantiate_unscoped_primitive(ty: types.Type, arguments,
                                   scopes: Scopes) -> types.Type:
    return ty


@instantiate_unscoped.register
def instantiate_unscoped_typeref(self: types.TypeRef, arguments: TypeMap,
                                 scopes: Scopes) -> types.Type:
    # if not scopes.has_binding(self.name):
    #     raise errors.TypeError(f'Use of unresolved type {self.name}')
    # return self
    return instantiate(scopes.resolve_binding(self.name), arguments, scopes)


@instantiate_unscoped.register
def instantiate_unscoped_typevariable(self: types.TypeVariable,
                                      arguments: TypeMap,
                                      scopes: Scopes) -> types.Type:
    return arguments.get(self, self)


@instantiate_unscoped.register
def instantiate_unscoped_tupletype(self: types.TupleType, arguments: TypeMap,
                                   scopes: Scopes) -> types.Type:
    return types.TupleType(elements=tuple(
        instantiate(elem, arguments, scopes) for elem in self.elements))


@instantiate_unscoped.register
def instantiate_unscoped_arraytype(self: types.ArrayType, arguments: TypeMap,
                                   scopes: Scopes):
    return types.ArrayType(length=self.length,
                           element_type=instantiate(self.element_type,
                                                    arguments, scopes))


@instantiate_unscoped.register
def instantiate_unscoped_slicetype(self: types.SliceType, arguments: TypeMap,
                                   scopes: Scopes):
    return types.SliceType(
        element_type=instantiate(self.element_type, arguments, scopes))


def zipped_typevariables(self: types.ScopedType,
                         type_arguments: Iterable[types.Type]) -> TypeMap:
    for var, arg in zip_longest(self.type_parameters, type_arguments):
        if var is None:
            raise TypeError("Too many type arguments")
        if arg is None:
            raise TypeError(f"Missing type argument {var.name}")
    return dict(zip(self.type_parameters, type_arguments))


@singledispatch
def instantiate_scoped(self: types.ScopedType, arguments: Iterable[types.Type],
                       scopes: Scopes) -> types.Type:
    raise NotImplementedError()


@instantiate_scoped.register
def instantiate_scoped_uniontype(self: types.UnionType,
                                 arguments: Iterable[types.Type],
                                 scopes: Scopes) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    new_variants = []
    for name, variant_type in self.variants:
        new_variants.append((name, instantiate(variant_type, zipped, scopes)))

    return types.UnionType(name=self.name,
                           variants=tuple(new_variants),
                           type_parameters=self.type_parameters,
                           type_arguments=arguments)


@instantiate_scoped.register
def instantiate_newtype(self: types.NewType, arguments: Iterable[types.Type],
                        scopes: Scopes) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    return types.NewType(name=self.name,
                         type_parameters=self.type_parameters,
                         type_arguments=arguments,
                         inner_type=instantiate(self.inner_type, zipped,
                                                scopes))


@instantiate_scoped.register
def instantiate_structtype(self: types.StructType,
                           arguments: Iterable[types.Type],
                           scopes: Scopes) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    new_fields = []
    for name, field_type in self.fields:
        new_fields.append((name, instantiate(field_type, zipped, scopes)))

    return types.StructType(name=self.name,
                            fields=tuple(new_fields),
                            type_parameters=self.type_parameters,
                            type_arguments=arguments)


@instantiate_scoped.register
def instantiate_scoped_functiontype(self: types.FunctionType,
                                    arguments: Iterable[types.Type],
                                    scopes: Scopes) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    new_params = []
    for name, param_type in self.parameters:
        new_params.append((name, instantiate(param_type, zipped, scopes)))

    return types.FunctionType(name=self.name,
                              return_type=instantiate(self.return_type, zipped,
                                                      scopes),
                              parameters=new_params,
                              type_parameters=self.type_parameters,
                              type_arguments=arguments)
