# SYMBOL
'''
:something

type checking at compile time, at runtime usize with symbol_to_string function
'''

# ENUM
'''
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
'''

# UNION
'''
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
'''

# STRUCT
'''
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
'''

# TUPLE
'''
(123, "abc", 3.2)

- maps to llvm tuple
- can destructure (also in pattern matching)

%0 = alloca { i32, %struct.string, double }
'''

# ARRAY
'''
string[2] strings = ["abc", "123"];

- element type
- not generic
- fixed length
- length known statically

%array = alloca [2 x %struct.string]
'''

# SLICE
'''
// is basically length + pointer to elems: type { i32 len, T* elems }
int32[] someints;

%slice = alloca i32, %len
'''

# stretch goal: INTERFACE
# aka typeclasses
# explicit implementation for better error locality (compared to go)
'''
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
'''

# FUNCTION
'''
pub int main(string[] argv) {
    return 0;
}

define i32 @__the_main(%"string[]" %argv) {
  ret i32 0
}
'''
