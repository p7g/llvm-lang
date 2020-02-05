import pytest

from llvm_lang import types


def test_inttype_verify():
    for size in (8, 16, 32, 64, 128):
        assert types.IntType(size).verify() is None, \
            f"IntType({size}) is valid"

    with pytest.raises(types.TypeError):
        types.IntType(7).verify()


def test_floattype_verify():
    for size in (32, 64):
        assert types.FloatType(size).verify() is None, \
            f"FloatType({size}) is valid"

    with pytest.raises(types.TypeError):
        types.FloatType(128).verify()


def test_booltype_verify():
    assert types.BoolType().verify() is None, "BoolType is valid"


def test_symboltype_verify():
    assert types.SymbolType("hello").verify() is None, \
        'SymbolType("Hello") is valid'

    with pytest.raises(types.TypeError):
        types.SymbolType("").verify()


def test_verify_no_duplicate():
    with pytest.raises(types.TypeError):
        types.verify_no_duplicate([1, 1, 2, 3], "%s")

    with pytest.raises(types.TypeError):
        types.verify_no_duplicate([
            types.StructType(name="test", fields=(("a", types.BoolType()), )),
            types.StructType(name="test", fields=(("a", types.BoolType()), )),
        ], "%s")

    assert types.verify_no_duplicate([1, 2, 3], "%s") is None


def test_enumtype_verify():
    typ = types.EnumType("test_enum", variants=("A", "B", "C"))
    assert typ.verify() is None, "EnumType without duplicate variants is ok"

    typ2 = types.EnumType("test_enum", variants=("A", "A"))
    with pytest.raises(types.TypeError):
        typ2.verify()


def test_generictype_verify():
    typ = types.GenericType(type_parameters=(types.TypeVariable("T"),
                                             types.TypeVariable("U")))

    assert typ.verify() is None, "Generic with unique parameters is ok"

    typ = types.GenericType(type_parameters=(types.TypeVariable("T"),
                                             types.TypeVariable("T")))

    with pytest.raises(types.TypeError):
        typ.verify()


def test_uniontype_verify():
    typ = types.UnionType("test_union",
                          variants=(
                              ("A", types.TupleType(types.IntType(32))),
                              ("B", types.TupleType(types.IntType(8))),
                          ))

    assert typ.verify() is None, "Union with unique variant names is ok"

    typ = types.UnionType("test_union",
                          variants=(
                              ("A", types.TupleType(types.IntType(32))),
                              ("A", types.TupleType(types.IntType(8))),
                          ))

    with pytest.raises(types.TypeError):
        typ.verify()


def test_structtype_verify():
    typ = types.StructType("test_struct",
                           fields=(
                               ("a", types.IntType(8)),
                               ("b", types.IntType(16)),
                           ))

    assert typ.verify() is None, "Struct with unique field names is ok"

    typ = types.StructType("test_struct",
                           fields=(
                               ("a", types.IntType(8)),
                               ("a", types.IntType(16)),
                           ))

    with pytest.raises(types.TypeError):
        typ.verify()


def test_tupletype_verify():
    assert types.TupleType().verify() is None, "Empty TupleType is ok"
    assert types.TupleType((types.IntType(8),)).verify() is None, \
        "Non-empty TupleType is ok"


def test_arraytype_verify():
    assert types.ArrayType(3, types.IntType(8)).verify() is None, \
        "ArrayType of int8[3] is valid"


def test_slicetype_verify():
    assert types.SliceType(types.FloatType(32)).verify() is None, \
        "SliceType of int8 is valid"


def test_functiontype_verify():
    typ = types.FunctionType(
        name="test_func",
        return_type=None,
        parameters=(("a", types.IntType(8)), ("b", types.IntType(8))),
    )

    assert typ.verify() is None, "FunctionType with unique params is ok"

    typ = types.FunctionType(
        name="test_func",
        return_type=None,
        parameters=(("a", types.IntType(8)), ("a", types.IntType(8))),
    )

    with pytest.raises(types.TypeError):
        typ.verify()
