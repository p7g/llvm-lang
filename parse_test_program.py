from llvm_lang.compiler import compiler

test_program = '''\
# union Result<T, U> {
#     Ok(T,)
#     Err(U,)
# }

struct Greeter {
    name: string
}

newtype string = uint8[];

let global_var: int64 = 0;

function greet(greeter: Greeter): string {
    let a: int64 = 123;

    # print("Hello, " + greeter.name + "!" + 123);
    # break;
    return "hello";
}

function main(): void {
    let greeter: Greeter = "this is wrong";
    let result: uint8[] = greet(greeter);
}
'''

ctx = compiler.compile(test_program)

print(str(ctx.ast_root))
