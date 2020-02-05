import sys

from ply import lex, yacc

from . import ast

tokens = (
    "IDENTIFIER",
    "INTEGER",
    "REAL",
    "STRING",
    "EQUAL",
    "PLUS",
    "MINUS",
    "STAR",
    "SLASH",
    "AMPERSAND",
    "LEFT_PAREN",
    "RIGHT_PAREN",
    "LEFT_BRACKET",
    "RIGHT_BRACKET",
    "LEFT_BRACE",
    "RIGHT_BRACE",
    "SEMICOLON",
    "COMMA",
    "COMMENT",
)

t_IDENTIFIER = r"[a-zA-Z_][-a-zA-Z0-9_]*[\'?!]?"
t_INTEGER = r"\d+"
t_REAL = r"\d+(?:\.\d+|[eE][+-]?\d+)"

t_EQUAL = r"="
t_PLUS = r"\+"
t_MINUS = r"-"
t_STAR = r"\*"
t_SLASH = r"/"
t_AMPERSAND = r"&"

t_LEFT_PAREN = r"\("
t_RIGHT_PAREN = r"\)"
t_LEFT_BRACKET = r"\["
t_RIGHT_BRACKET = r"\]"
t_LEFT_BRACE = r"\}"
t_RIGHT_BRACE = r"\}"

t_SEMICOLON = r";"
t_COMMA = r","

t_ignore = " \t"


def t_STRING(t):
    r'"(?:[^"\\]|\\["\\nt])*"'
    t.value = (t.value.replace('\\"', '"').replace("\\n", "\n").replace(
        "\\t", "\t").replace("\\\\", "\\"))
    return t


def t_COMMENT(t):
    r"\#.*"


def t_newline(t):
    r"(?:\r?\n)+"
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0], file=sys.stderr)


lexer = lex.lex()

precedence = (
    ("right", "EQUAL"),
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "SLASH"),
    ("left", "INDEX"),
    ("right", "UMINUS", "DEREF", "AMPERSAND"),
)


def p_program(t):
    "program : declaration"
    t[0] = [t[1]]


def p_program_multiple(t):
    "program : program declaration"
    t[0] = t[1] + [t[2]]


def p_declaration_function(t):
    """declaration : identifier identifier LEFT_PAREN argument_list RIGHT_PAREN
    LEFT_BRACE function_body RIGHT_BRACE"""
    t[0] = ast.FunctionDeclaration(t[2], t[1], t[4], t[7])


def p_statement_expression(t):
    "statement : expression SEMICOLON"
    t[0] = ast.ExpressionStatement(t[1])


def p_expression_binop(t):
    """expression : expression EQUAL expression
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression STAR expression
                  | expression SLASH expression"""
    if t[2] == "+":
        op = ast.Op.plus
    elif t[2] == "-":
        op = ast.Op.minus
    elif t[2] == "*":
        op = ast.Op.times
    elif t[2] == "/":
        op = ast.Op.divide
    elif t[2] == "=":
        op = ast.Op.assign
    else:
        raise ValueError("Unknown binary operation '%s'" % t[2])

    t[0] = ast.BinaryOperation(t[1], op, t[3])


def p_expression_group(t):
    "expression : LEFT_PAREN expression RIGHT_PAREN"
    t[0] = t[1]


def p_expression_uminus(t):
    "expression : MINUS expression %prec UMINUS"
    t[0] = ast.UnaryOperation(ast.Op.negate, t[2])


def p_expression_integer(t):
    "expression : INTEGER"
    t[0] = ast.IntegerLiteral(int(t[1]))


def p_expression_real(t):
    "expression : REAL"
    t[0] = ast.RealLiteral(float(t[1]))


def p_expression_string(t):
    "expression : STRING"
    t[0] = ast.StringLiteral(t[1][1:-1])


def p_expression_call(t):
    "expression : expression LEFT_PAREN expression_list RIGHT_PAREN"
    t[0] = ast.CallExpression(t[1], t[3])


def p_expression_address_of(t):
    "expression : AMPERSAND expression"
    t[0] = ast.UnaryOperation(ast.Op.ref, t[2])


def p_expression_assignment_target(t):
    "expression : assignment_target"
    t[0] = t[1]


def p_assignment_target_identifier(t):
    "assignment_target : IDENTIFIER"
    t[0] = ast.Identifier(t[1])


def p_assignment_target_index(t):
    "assignment_target : expression LEFT_BRACKET expression RIGHT_BRACKET %prec INDEX"  # noqa
    t[0] = ast.BinaryOperation(t[1], ast.Op.index, t[3])


def p_assignment_target_deref(t):
    "assignment_target : STAR expression %prec DEREF"
    t[0] = ast.UnaryOperation(ast.Op.deref, t[2])


def p_expression_list_empty(t):
    "expression_list : empty"
    t[0] = []


def p_expression_list_one(t):
    "expression_list : expression"
    t[0] = [t[1]]


def p_expression_list_list(t):
    "expression_list : expression COMMA expression_list"
    t[0] = [t[1]] + t[3]


def p_empty(t):
    "empty :"


def p_error(t):
    print("Syntax error at '%s'" % t.value, file=sys.stderr)


parser = yacc.yacc(debug=True)


def parse(s):
    print(parser.parse(s))
