from functools import singledispatch
from itertools import zip_longest
from typing import Dict, Iterable

from .. import types

TypeMap = Dict[types.TypeVariable, types.Type]


def instantiate(ty: types.Type, arguments: TypeMap) -> types.Type:
    if isinstance(ty, types.ScopedType):
        if ty.type_arguments:
            type_arguments = (arguments.get(t, t) if isinstance(
                t, types.TypeVariable) else instantiate(t, arguments)
                              for t in ty.type_arguments)
        else:
            type_arguments = arguments.values()
        return instantiate_scoped(ty, type_arguments)

    return instantiate_unscoped(ty, arguments)


@singledispatch
def instantiate_unscoped(ty: types.Type, arguments: TypeMap) -> types.Type:
    raise NotImplementedError()


@instantiate_unscoped.register(types.BoolType)
@instantiate_unscoped.register(types.IntType)
@instantiate_unscoped.register(types.FloatType)
@instantiate_unscoped.register(types.SymbolType)
@instantiate_unscoped.register(types.EnumType)
def instantiate_unscoped_primitive(ty: types.Type, arguments) -> types.Type:
    return ty


@instantiate_unscoped.register
def instantiate_unscoped_typevariable(self: types.TypeVariable,
                                      arguments: TypeMap) -> types.Type:
    return arguments.get(self, self)


@instantiate_unscoped.register
def instantiate_unscoped_tupletype(self: types.TupleType,
                                   arguments: TypeMap) -> types.Type:
    return types.TupleType(elements=tuple(
        instantiate(elem, arguments) for elem in self.elements))


@instantiate_unscoped.register
def instantiate_unscoped_arraytype(self: types.ArrayType, arguments: TypeMap):
    raise NotImplementedError()


@instantiate_unscoped.register
def instantiate_unscoped_slicetype(self: types.SliceType, arguments: TypeMap):
    raise NotImplementedError()


def zipped_typevariables(self: types.ScopedType,
                         type_arguments: Iterable[types.Type]) -> TypeMap:
    for var, arg in zip_longest(self.type_parameters, type_arguments):
        if var is None:
            raise TypeError("Too many type arguments")
        if arg is None:
            raise TypeError(f"Missing type argument {var.name}")
    return dict(zip(self.type_parameters, type_arguments))


@singledispatch
def instantiate_scoped(self: types.ScopedType,
                       arguments: Iterable[types.Type]) -> types.Type:
    raise NotImplementedError()


@instantiate_scoped.register
def instantiate_scoped_uniontype(
        self: types.UnionType, arguments: Iterable[types.Type]) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    new_variants = []
    for name, variant_type in self.variants:
        new_variants.append((name, instantiate(variant_type, zipped)))

    return types.UnionType(name=self.name,
                           variants=tuple(new_variants),
                           type_parameters=self.type_parameters,
                           type_arguments=arguments)


@instantiate_scoped.register
def instantiate_newtype(self: types.NewType,
                        arguments: Iterable[types.Type]) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    return types.NewType(name=self.name,
                         type_parameters=self.type_parameters,
                         type_arguments=arguments,
                         inner_type=instantiate(self.inner_type, zipped))


@instantiate_scoped.register
def instantiate_structtype(self: types.StructType,
                           arguments: Iterable[types.Type]) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    new_fields = []
    for name, field_type in self.fields:
        new_fields.append((name, instantiate(field_type, zipped)))

    return types.StructType(name=self.name,
                            fields=tuple(new_fields),
                            type_parameters=self.type_parameters,
                            type_arguments=arguments)
