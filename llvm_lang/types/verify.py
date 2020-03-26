from collections import Counter
from functools import singledispatch
from operator import itemgetter

from .. import types
from ..errors import ReferenceError, TypeError


@singledispatch
def verify(t):
    raise NotImplementedError()


@verify.register(types.BoolType)
@verify.register(types.SymbolType)
def verify_always_valid(_self):
    pass


@verify.register
def verify_type_variable(self: types.TypeVariable):
    # If there is a type variable left by the time we do verification, it must
    # have been unbound (it was never substituted with a concrete type)
    raise ReferenceError(f"Type variable {self.name} is not defined")


@verify.register
def verify_type_ref(self: types.TypeRef):
    raise ReferenceError(f"Type {self.name} is not defined")


@verify.register
def verify_int_type(self: types.IntType):
    if self.size not in self.VALID_SIZES:
        raise TypeError("Integer size must be one of: " +
                        ", ".join(map(str, self.VALID_SIZES)))


@verify.register
def verify_float_type(self: types.FloatType):
    if self.size not in self.VALID_SIZES:
        raise TypeError("Float size must be one of: " +
                        ", ".join(map(str, self.VALID_SIZES)))


def verify_no_duplicate(elems, msg):
    counted = Counter(elems)
    most_common, times = counted.most_common(1)[0]
    if times > 1:
        raise TypeError(msg % most_common)


@verify.register
def verify_enum_type(self: types.EnumType):
    verify_no_duplicate(self.variants, "Duplicate enum variant %s")


def verify_scopedtype(self: types.ScopedType):
    if self.type_parameters:
        verify_no_duplicate(self.type_parameters, "Duplicate type variable %s")


@verify.register
def verify_newtype(self: types.NewType):
    verify_scopedtype(self)
    verify(self.inner_type)


@verify.register
def verify_union_type(self: types.UnionType):
    verify_scopedtype(self)
    verify_no_duplicate(map(itemgetter(0), self.variants),
                        "Duplicate union variant %s")
    for _name, variant in self.variants:
        verify(variant)


@verify.register
def verify_struct_type(self: types.StructType):
    verify_scopedtype(self)
    verify_no_duplicate(map(itemgetter(0), self.fields),
                        "Duplicate field name %s")
    for _name, field in self.fields:
        verify(field)


@verify.register
def verify_tuple_type(self: types.TupleType):
    for ty in self.elements:
        verify(ty)


@verify.register
def verify_array_type(self: types.ArrayType):
    if self.length < 0:
        raise TypeError("Array length must be a positive integer")
    verify(self.element_type)


@verify.register
def verify_slice_type(self: types.SliceType):
    verify(self.element_type)


@verify.register
def verify_function_type(self: types.FunctionType):
    verify_scopedtype(self)
    verify_no_duplicate(map(itemgetter(0), self.parameters),
                        "Duplicate parameter name %s")
    if self.return_type:
        verify(self.return_type)
    for _name, ty in self.parameters:
        verify(ty)
