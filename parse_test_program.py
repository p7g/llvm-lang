from llvm_lang.compiler import compiler

test_program = '''\
union Result<T, U> {
    Ok(T,)
    Err(U,)
}

enum Test {
    VARIANT_A
}

struct Greeter {
    string name
}

newtype Test2 = (int32, );

let global_var: int64 = 0;

void greet(greeter: Greeter) {
    let a: int64 = 123;

    # print("Hello, " + greeter.name + "!" + 123);
    # break;
    return "hello";
}

void main() {
    let greeter: Greeter = "this is wrong";
    let result: uint8[] = greet(greeter);
}
'''

ctx = compiler.compile(test_program)

print(str(ctx.ast_root))
