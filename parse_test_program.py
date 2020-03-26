from llvm_lang.compiler import compiler

test_program = '''
# enum Test {}

union Result<T, U> {
    Ok(T)
    Err(U)
}

struct Greeter {
    string name
}

void greet(Greeter greeter) {
    print("Hello, " + greeter.name + "!");
    # break;
    return "hello";
}
'''

print(compiler.compile(test_program))
