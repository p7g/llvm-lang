import pytest

from llvm_lang import types
from llvm_lang.types.verify import verify, verify_no_duplicate


def test_inttype_verify():
    for size in (8, 16, 32, 64, 128):
        assert verify(types.IntType(size)) is None, \
            f"IntType({size}) is valid"

    with pytest.raises(types.TypeError):
        verify(types.IntType(7))


def test_floattype_verify():
    for size in (32, 64):
        assert verify(types.FloatType(size)) is None, \
            f"FloatType({size}) is valid"

    with pytest.raises(types.TypeError):
        verify(types.FloatType(128))


def test_booltype_verify():
    assert verify(types.BoolType()) is None, "BoolType is valid"


def test_symboltype_verify():
    assert verify(types.SymbolType()) is None, 'SymbolType is valid'


def test_verify_no_duplicate():
    with pytest.raises(types.TypeError):
        verify_no_duplicate([1, 1, 2, 3], "%s")

    with pytest.raises(types.TypeError):
        verify_no_duplicate([
            types.StructTemplate(name="test",
                                 fields=(("a", types.BoolType()), )),
            types.StructTemplate(name="test",
                                 fields=(("a", types.BoolType()), )),
        ], "%s")

    assert verify_no_duplicate([1, 2, 3], "%s") is None


def test_enumtype_verify():
    typ = types.EnumType("test_enum", variants=("A", "B", "C"))
    assert verify(typ) is None, "EnumType without duplicate variants is ok"

    typ2 = types.EnumType("test_enum", variants=("A", "A"))
    with pytest.raises(types.TypeError):
        verify(typ2)


def test_template_verify():
    typ = types.StructTemplate(name="test_struct",
                               type_parameters=(types.TypeVariable("T"),
                                                types.TypeVariable("U")),
                               fields=(("a", types.IntType(32)), ))

    assert verify(typ) is None, "Template with unique parameters is ok"

    typ = types.StructTemplate(name="test_struct",
                               type_parameters=(types.TypeVariable("T"),
                                                types.TypeVariable("T")),
                               fields=(("a", types.IntType(32)), ))

    with pytest.raises(types.TypeError):
        verify(typ)


def test_uniontype_verify():
    typ = types.UnionTemplate("test_union",
                              variants=(
                                  ("A", types.TupleType(
                                      (types.IntType(32), ))),
                                  ("B", types.TupleType(
                                      (types.IntType(16), ))),
                              ))

    assert verify(typ) is None, "Union with unique variant names is ok"

    typ = types.UnionTemplate("test_union",
                              variants=(
                                  ("A", types.TupleType(
                                      (types.IntType(32), ))),
                                  ("A", types.TupleType(
                                      (types.IntType(16), ))),
                              ))

    with pytest.raises(types.TypeError):
        verify(typ)


def test_structtype_verify():
    typ = types.StructTemplate("test_struct",
                               fields=(
                                   ("a", types.IntType(8)),
                                   ("b", types.IntType(16)),
                               ))

    assert verify(typ) is None, "Struct with unique field names is ok"

    typ = types.StructTemplate("test_struct",
                               fields=(
                                   ("a", types.IntType(8)),
                                   ("a", types.IntType(16)),
                               ))

    with pytest.raises(types.TypeError):
        verify(typ)


def test_tupletype_verify():
    assert verify(types.TupleType()) is None, "Empty TupleType is ok"
    assert verify(types.TupleType((types.IntType(8),))) is None, \
        "Non-empty TupleType is ok"


def test_arraytype_verify():
    assert verify(types.ArrayType(3, types.IntType(8))) is None, \
        "ArrayType of int8[3] is valid"


def test_slicetype_verify():
    assert verify(types.SliceType(types.FloatType(32))) is None, \
        "SliceType of int8 is valid"


def test_functiontemplate_verify():
    typ = types.FunctionTemplate(
        name="test_func",
        return_type=None,
        parameters=(("a", types.IntType(8)), ("b", types.IntType(8))),
    )

    assert verify(typ) is None, "FunctionTemplate with unique params is ok"

    typ = types.FunctionTemplate(
        name="test_func",
        return_type=None,
        parameters=(("a", types.IntType(8)), ("a", types.IntType(8))),
    )

    with pytest.raises(types.TypeError):
        verify(typ)
