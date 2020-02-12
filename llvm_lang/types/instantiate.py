from functools import singledispatch
from itertools import zip_longest
from typing import Dict, Iterable

from .. import types

TypeMap = Dict[types.TypeVariable, types.Type]


@singledispatch
def instantiate(ty: types.Type, arguments: TypeMap) -> types.Type:
    raise NotImplementedError()


@instantiate.register(types.TypeVariable)
@instantiate.register(types.BoolType)
@instantiate.register(types.IntType)
@instantiate.register(types.FloatType)
@instantiate.register(types.SymbolType)
@instantiate.register(types.EnumType)
def instantiate_primitive(ty: types.Type, arguments) -> types.Type:
    return ty


@instantiate.register
def instantiate_tupletype(self: types.TupleType,
                          arguments: TypeMap) -> types.Type:
    new_elements = []
    for elem in self.elements:
        if isinstance(elem, types.TypeVariable):
            new_elem = arguments.get(elem, elem)
        elif isinstance(elem, types.ScopedType):
            new_elem = instantiate_scoped(elem,
                                          (arguments.get(t, t) if isinstance(
                                              t, types.TypeVariable) else t
                                           for t in elem.type_arguments))
        else:
            new_elem = instantiate(elem, arguments)

        new_elements.append(new_elem)

    return types.TupleType(elements=tuple(new_elements))


@instantiate.register
def instantiate_arraytype(self: types.ArrayType, arguments: TypeMap):
    raise NotImplementedError()


@instantiate.register
def instantiate_slicetype(self: types.SliceType, arguments: TypeMap):
    raise NotImplementedError()


def zipped_typevariables(self: types.ScopedType,
                         type_arguments: Iterable[types.Type]) -> TypeMap:
    for var, arg in zip_longest(self.type_parameters, type_arguments):
        if var is None:
            raise TypeError("Too many type arguments")
        if arg is None:
            raise TypeError(f"Missing type argument {var.name}")
    return dict(zip(self.type_parameters, type_arguments))


@instantiate.register
def instantiate_uniontype(self: types.UnionType,
                          arguments: Iterable[types.Type]) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    new_variants = []
    for name, variant_type in self.variants:
        if isinstance(variant_type, types.TypeVariable):
            ty = zipped.get(variant_type, variant_type)
        else:
            ty = variant_type

        if isinstance(ty, types.ScopedType):
            type_vars = (zipped.get(t, t) for t in ty.type_parameters
                         if isinstance(t, types.TypeVariable))
            new_variant = instantiate_scoped(ty, type_vars)
        else:
            new_variant = instantiate(ty, zipped)

        new_variants.append((name, new_variant))

    return types.UnionType(name=self.name,
                           variants=tuple(new_variants),
                           type_parameters=self.type_parameters,
                           type_arguments=arguments)


@singledispatch
def instantiate_scoped(self: types.ScopedType,
                       arguments: Iterable[types.Type]) -> types.Type:
    raise NotImplementedError()


@instantiate_scoped.register
def instantiate_newtype(self: types.NewType,
                        arguments: Iterable[types.Type]) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    if not isinstance(self.inner_type, types.ScopedType):
        inner = instantiate(self.inner_type, zipped)
    else:
        inner_typeargs = self.inner_type.type_arguments
        inner = instantiate_scoped(self.inner_type,
                                   (zipped.get(t, t) for t in inner_typeargs))
    return types.NewType(name=self.name,
                         type_parameters=self.type_parameters,
                         type_arguments=arguments,
                         inner_type=inner)


@instantiate_scoped.register
def instantiate_structtype(self: types.StructType,
                           arguments: Iterable[types.Type]) -> types.Type:
    arguments = tuple(arguments)
    zipped = zipped_typevariables(self, arguments)

    new_fields = []
    for name, field_type in self.fields:
        if isinstance(field_type, types.TypeVariable):
            ty = zipped.get(field_type, field_type)
        else:
            ty = field_type

        if isinstance(ty, types.ScopedType):
            type_vars = (zipped.get(t, t) for t in ty.type_parameters
                         if isinstance(t, types.TypeVariable))
            new_variant = instantiate_scoped(ty, type_vars)
        else:
            new_variant = instantiate(ty, zipped)

        new_fields.append((name, new_variant))

    return types.StructType(name=self.name,
                            fields=tuple(new_fields),
                            type_parameters=self.type_parameters,
                            type_arguments=arguments)
