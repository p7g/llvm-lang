import attr
import itertools

from typing import Optional, Tuple, Union

__all__ = (
    'primitive_types',
    'Type',
    'PrimitiveType',
    'IntType',
    'FloatType',
    'BoolType',
    'SymbolType',
    'VoidType',
    'EnumType',
    'TypeVariable',
    'TypeRef',
    'ScopedType',
    'NewType',
    'UnionType',
    'StructType',
    'TupleType',
    'ArrayType',
    'SliceType',
    'FunctionType',
)

type_ = attr.s(auto_attribs=True, frozen=True)


@type_
class Type:
    pass


class PrimitiveType(Type):
    pass


@type_
class IntType(PrimitiveType):
    VALID_SIZES = (8, 16, 32, 64, 128)

    size: int
    signed: bool

    def __str__(self):
        return f"{'' if self.signed else 'u'}int{self.size}"


@type_
class FloatType(PrimitiveType):
    VALID_SIZES = (32, 64)

    size: int

    def __str__(self):
        return f"float{self.size}"


@type_
class BoolType(PrimitiveType):
    def __str__(self):
        return "bool"


@type_
class SymbolType(PrimitiveType):
    """
    :something

    type checking at compile time, at runtime usize with symbol_to_string
    function
    """
    def __str__(self):
        return "symbol"


@type_
class VoidType(PrimitiveType):
    def __str__(self):
        return "void"


@type_
class EnumType(Type):
    """
    enum TokenType {
        STRING,
        INTEGER,
        FLOAT,
    }

    - name
    - variants
    - can convert between int and enum easily

    %enum.TokenType = type { i8 }
    @TokenType.STRING = constant %enum.TokenType { 0 }
    @TokenType.INTEGER = constant %enum.TokenType { 1 }
    @TokenType.FLOAT = constant %enum.TokenType { 2 }
    """

    name: str
    variants: Tuple[str, ...]

    def __str__(self):
        return self.name


@type_
class TypeVariable(Type):
    name: str

    # TODO: constraints?

    def __str__(self):
        return self.name


@type_
class TypeRef(Type):
    name: str
    type_arguments: Tuple[Type, ...]

    def __str__(self):
        return f"{self.name}{super().__str__()}"


@type_
class ScopedType(Type):
    """A scoped type declares type variables that must be provided during
    instantiation"""

    type_parameters: Tuple[TypeVariable, ...] = attr.ib(factory=tuple,
                                                        kw_only=True)
    type_arguments: Tuple[Optional[TypeVariable], ...] = attr.ib(factory=tuple,
                                                                 kw_only=True)

    def __str__(self):
        types = []
        for param, arg in itertools.zip_longest(self.type_parameters,
                                                self.type_arguments):
            types.append(arg if arg is not None else param)

        if types:
            return "<" + ", ".join(map(str, types)) + ">"
        return ""


@type_
class NewType(ScopedType):
    name: str
    inner_type: Type

    def __str__(self):
        return f"{self.name}{super().__str__()}"


@type_
class UnionType(ScopedType):
    """
    union Token {
        EOF
        String(string),
        Integer(int32),
        Float(float64),
        SomethingElse { List<Field> stuff },
    }

    - name
    - variants
      - empty, tuple, or struct
      - details of contents
    - optionally generic

    (where List<Field> is 24 bytes)

    %union.Token = type { i8, [ 24 x i8 ] }

    ; assuming
    %union = alloca %union.Token

    %EOF = bitcast %union.Token* %union to { i8 }*
    %String = bitcast %union.Token* %union to { i8, %string }*
    %Integer = bitcast %union.Token* %union to { i8, i32 }*
    %Float = bitcast %union.Token* %union to { i8, double }*
    %SomethingElse = bitcast %union.Token* %union to { i8, %"List<Field>" }*
    """

    name: str
    variants: Tuple[Tuple[str, Union["TupleType", "StructType"]], ...]

    def __str__(self):
        return f"{self.name}{super().__str__()}"


@type_
class StructType(ScopedType):
    """
    struct Token {
        TokenType type,
        Range range,
        // stretch goal:
        // struct {
        //     string hello,
        // } test,
    }

    - name
    - fields
    - optionally generic

    %struct.Token = type {
        %enum.TokenType,
        %struct.Range,
    }
    """

    name: str
    fields: Tuple[Tuple[str, Type], ...]

    def __str__(self):
        return f"{self.name}{super().__str__()}"


@type_
class TupleType(Type):
    """
    (123, "abc", 3.2)

    - maps to llvm tuple
    - can destructure (also in pattern matching)

    %0 = alloca { i32, %struct.string, double }
    """

    elements: Tuple[Type, ...] = ()

    def __str__(self):
        trailing_comma = "," if len(self.elements) == 1 else ""
        return "(" + ", ".join(map(str, self.elements)) + trailing_comma + ")"


@type_
class ArrayType(Type):
    """
    string[2] strings = ["abc", "123"];

    - element type
    - not generic
    - fixed length
    - length known statically

    %array = alloca [2 x %struct.string]
    """

    length: int
    element_type: Type

    def __str__(self):
        return f"{self.element_type}[{self.length}]"


@type_
class SliceType(Type):
    """
    // is basically length + pointer to elems: type { i32 len, T* elems }
    int32[] someints;

    %slice = alloca i32, %len
    """

    element_type: Type

    def __str__(self):
        return f"{self.element_type}[]"


@type_
class FunctionType(ScopedType):
    """
    pub int main(string[] argv) {
        return 0;
    }

    define i32 @__the_main(%"string[]" %argv) {
    ret i32 0
    }
    """

    name: Optional[str]
    return_type: Optional[Type]  # `void` if None
    parameters: Tuple[Tuple[str, Type], ...]

    def __str__(self):
        name = "<anon>" if self.name is None else self.name
        params = ", ".join(f"{t} {name}" for name, t in self.parameters)

        return f"{self.return_type} {name}{super().__str__()}({params})"


primitive_types = {
    "bool": BoolType(),
    "symbol": SymbolType(),
    "void": VoidType(),
}

for size, signed in itertools.product(IntType.VALID_SIZES, (True, False)):
    ty = IntType(size=size, signed=signed)
    primitive_types[str(ty)] = ty

for size in FloatType.VALID_SIZES:
    ty = FloatType(size=size)
    primitive_types[str(ty)] = ty

# stretch goal: INTERFACE
# aka typeclasses
# explicit implementation for better error locality (compared to go)
"""
interface ToString T {
    string to_string(value: T);
}

impl ToString for string {
    string to_string(self: string) {
        return self;
    }
}

void myfun(ToString thing) {
    print(to_string(thing))
}

interface Into<T> for U {
    T into(value: U);
}

newtype Name = string;

impl Into<string> for Name {
    string into(value: Name) {
        return string(value);
    }
}

impl Into<T> for Name
where
  T implements From<Name>
{
  T into(name: Name) {
    return from(name);
  }
}
"""
