from abc import ABC, abstractmethod
from collections import Counter
from dataclass import dataclass
from operator import itemgetter
from typing import List, Optional, Tuple, Union


class TypeError(Exception):
    pass


@dataclass
class TypeVariable:
    name: str
    # TODO: constraints?


@dataclass
class Type(ABC):
    @abstractmethod
    def verify(self):
        pass


@dataclass
class IntType(Type):
    VALID_SIZES = (8, 16, 32, 64, 128)

    size: int

    def verify(self):
        if self.size not in self.VALID_SIZES:
            raise TypeError("Integer size must be one of: " +
                            ", ".join(self.VALID_SIZES))


@dataclass
class FloatType(Type):
    VALID_SIZES = (32, 64)

    size: int  # should only be 32 or 64

    def verify(self):
        if self.size not in self.VALID_SIZES:
            raise TypeError("Float size must be one of: " +
                            ", ".join(self.VALID_SIZES))


@dataclass
class BoolType(Type):
    def verify(self):
        pass


@dataclass
class SymbolType(Type):
    """
    :something

    type checking at compile time, at runtime usize with symbol_to_string
    function
    """

    repr: str

    def verify(self):
        if not self.repr:
            raise TypeError("Symbols must not be empty strings")


def verify_no_duplicate(elems, msg):
    counted = Counter(elems)
    most_common, times = counted.most_common(1)[0]
    if times > 1:
        raise TypeError(msg % most_common)


@dataclass
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
    variants: List[str]

    def verify(self):
        verify_no_duplicate(self.variants, "Duplicate enum variant %s")


@dataclass
class GenericType(Type):
    type_parameters: List[TypeVariable]

    def verify(self):
        verify_no_duplicate(self.type_parameters, "Duplicate type variable %s")


@dataclass
class UnionType(GenericType):
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
    variants: List[Tuple[str, Union["TupleType", "StructType"]]]

    def verify(self):
        super(UnionType, self).verify()
        verify_no_duplicate(self.variants, "Duplicate union variant %s")


@dataclass
class StructType(GenericType):
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
    fields: List[Tuple[str, Type]]

    def verify(self):
        super(StructType, self).verify()
        verify_no_duplicate(map(itemgetter(0), self.fields),
                            "Duplicate field name %s")


@dataclass
class TupleType(Type):
    """
    (123, "abc", 3.2)

    - maps to llvm tuple
    - can destructure (also in pattern matching)

    %0 = alloca { i32, %struct.string, double }
    """

    elements: List[Type]

    def verify(self):
        pass


@dataclass
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

    def verify(self):
        pass


@dataclass
class SliceType(Type):
    """
    // is basically length + pointer to elems: type { i32 len, T* elems }
    int32[] someints;

    %slice = alloca i32, %len
    """

    element_type: Type

    def verify(self):
        pass


@dataclass
class FunctionType(GenericType):
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
    parameters: List[Tuple[str, Type]]

    def verify(self):
        super(FunctionType, self).verify()
        verify_no_duplicate(map(itemgetter(0), self.parameters),
                            "Duplicate parameter name %s")


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
