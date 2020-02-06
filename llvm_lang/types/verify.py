from collections import Counter
from functools import singledispatch
from operator import attrgetter, itemgetter

from .. import types
from . import TypeError


@singledispatch
def verify(t):
    raise NotImplementedError()


@verify.register(types.BoolType)
@verify.register(types.SymbolType)
def verify_always_valid(_self):
    pass


@verify.register
def verify_type_variable(self: types.TypeVariable):
    if self.value is None:
        raise TypeError(f"Type variable {self.name} is not defined")


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


@verify.register
def verify_template(self: types.Template):
    if self.type_parameters:
        verify_no_duplicate(self.type_parameters, "Duplicate type variable %s")
    unbound = self.free_type_variables()
    if unbound:
        raise TypeError("Unbound type variables: " +
                        ", ".join(map(attrgetter("name"), unbound)))


@verify.register
def verify_newtype(self: types.NewType):
    verify_template(self)
    verify(self.inner_type)


@verify.register
def verify_union_type(self: types.UnionTemplate):
    verify_template(self)
    verify_no_duplicate(map(itemgetter(0), self.variants),
                        "Duplicate union variant %s")


@verify.register
def verify_struct_type(self: types.StructTemplate):
    verify_template(self)
    verify_no_duplicate(map(itemgetter(0), self.fields),
                        "Duplicate field name %s")


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
def verify_function_type(self: types.FunctionTemplate):
    verify_template(self)
    verify_no_duplicate(map(itemgetter(0), self.parameters),
                        "Duplicate parameter name %s")
