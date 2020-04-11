from llvm_lang.compiler import compiler

test_program = '''
union Result<T, U> {
    Ok(T)
    Err(U)
}

enum Test {
    VARIANT_A
}

struct Greeter {
    string name
}

void greet(Greeter greeter) {
    int a = 123;

    print("Hello, " + greeter.name + "!" + 123);
    # break;
    return "hello";
}
'''

ctx = compiler.compile(test_program)

for typ in ctx.declared_types:
    print(str(typ.type))

from llvm_lang import ast, types
from llvm_lang.ast.map import MapAST


class AddTypesToIntegers(MapAST):
    def visit_IntegerLiteral(self, node: ast.IntegerLiteral):
        return ast.TypedExpression(value=node, type=types.IntType(32))


print(AddTypesToIntegers().visit(ctx.ast_root))
