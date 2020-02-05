# llvm-lang

Playing around with [PLY][ply] and [llvmlite][llvmlite].


The classes in [`llvm_lang/types`][types] hold information needed to generate
LLVM types later. These classes will be instantiated during a pass after
parsing probably, and then used later in codegen.

[ply]: http://www.dabeaz.com/ply/ply.html
[llvmlite]: https://github.com/numba/llvmlite
[types]: https://github.com/p7g/llvm-lang/tree/master/llvm_lang/types

The passes are likely to be as follows:

1. Lex/parse with PLY, building AST
1. Do some basic semantic checks on the AST, like `break` statements outside of
   loops
1. Verify type information
1. Optimize a bit, stuff like constant folding and dead code elimination if
   possible
1. Generate LLVM IR
