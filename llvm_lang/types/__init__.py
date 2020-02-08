import attr
import itertools

from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple, Union


def type_(cls):
    return attr.s(auto_attribs=True, frozen=True)(cls)


class TypeError(Exception):
    pass


@type_
class Type:
    pass


@type_
class TypeVariable(Type):
    name: str
    value: Optional[Type] = None

    # TODO: constraints?

    def __str__(self):
        return self.name


@type_
class IntType(Type):
    VALID_SIZES = (8, 16, 32, 64, 128)

    size: int

    def __str__(self):
        return f"int{self.size}"


@type_
class FloatType(Type):
    VALID_SIZES = (32, 64)

    size: int

    def __str__(self):
        return f"float{self.size}"


@type_
class BoolType(Type):
    def __str__(self):
        return "bool"


@type_
class SymbolType(Type):
    """
    :something

    type checking at compile time, at runtime usize with symbol_to_string
    function
    """

    def __str__(self):
        return "symbol"


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
class AggregateType(Type, ABC):
    @abstractmethod
    def free_type_variables(self):
        ...


@type_
class Template(AggregateType, ABC):
    type_parameters: Tuple[TypeVariable, ...] = attr.ib(factory=tuple,
                                                        kw_only=True)

    def __str__(self):
        if self.type_parameters:
            return "<" + ", ".join(map(str, self.type_parameters)) + ">"
        return ""

    def free_type_variables(self):
        child_type_vars = {
            t
            for t in self.child_types() if isinstance(t, TypeVariable)
        }
        return child_type_vars - set(self.type_parameters)

    @abstractmethod
    def child_types(self):
        # types used locally + free type variables of generics
        ...

    def instantiate(self, type_arguments: Iterable[Type]):
        for var, arg in itertools.zip_longest(self.type_parameters,
                                              type_arguments):
            if var is None:
                raise TypeError("Too many type arguments")
            if arg is None:
                raise TypeError(f"Missing type argument {var.name}")
            var.value = arg


@type_
class NewType(Template):
    name: str
    inner_type: Type

    def child_types(self):
        return self.inner_type.free_type_variables()

    def __str__(self):
        return f"{self.name}{super().__str__()}"


@type_
class UnionTemplate(Template):
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

    def child_types(self):
        for _name, typ in self.variants:
            yield from typ.free_type_variables()

    def __str__(self):
        return f"{self.name}{super().__str__()}"


@type_
class StructTemplate(Template):
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

    def child_types(self):
        for _name, typ in self.fields:
            if isinstance(typ, Template):
                yield from typ.free_type_variables()
            else:
                yield typ

    def __str__(self):
        return f"{self.name}{super().__str__()}"


@type_
class TupleType(AggregateType):
    """
    (123, "abc", 3.2)

    - maps to llvm tuple
    - can destructure (also in pattern matching)

    %0 = alloca { i32, %struct.string, double }
    """

    elements: Tuple[Type, ...] = ()

    def free_type_variables(self):
        for ty in self.elements:
            if isinstance(ty, TypeVariable):
                yield ty
            elif isinstance(ty, AggregateType):
                yield from ty.free_type_variables()

    def __str__(self):
        return "(" + ", ".join(map(str, self.elements)) + ")"


@type_
class ArrayType(AggregateType):
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

    def free_type_variables(self):
        if isinstance(self.element_type, TypeVariable):
            yield self.element_type
        elif isinstance(self.element_type, AggregateType):
            yield from self.element_type.free_type_variables()

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

    def free_type_variables(self):
        if isinstance(self.element_type, TypeVariable):
            yield self.element_type
        elif isinstance(self.element_type, AggregateType):
            yield from self.element_type.free_type_variables()

    def __str__(self):
        return f"{self.element_type}[]"


@type_
class FunctionTemplate(Template):
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

    def verify(self):
        super(FunctionTemplate, self).verify()

    def child_types(self):
        if self.return_type is not None:
            yield self.return_type
        for _name, typ in self.parameters:
            if isinstance(typ, Template):
                yield from typ.free_type_variables()
            else:
                yield typ

    def __str__(self):
        name = "<anon>" if self.name is None else self.name
        params = ", ".join(map(str, self.parameters))

        return f"{self.return_type} {name}{super().__str__()}({params})"


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
