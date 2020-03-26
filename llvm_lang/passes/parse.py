from .. import ast, parser


def parse(ctx: str) -> ast.Program:
    return parser.parse(ctx)
