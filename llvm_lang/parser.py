import sys

from ply import lex, yacc

from . import ast

reserved_words = {
    "break": "BREAK",
    "continue": "CONTINUE",
    "enum": "ENUM",
    "newtype": "NEWTYPE",
    "return": "RETURN",
    "struct": "STRUCT",
    "union": "UNION",
}

tokens = tuple(reserved_words.values()) + (
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
    "LESS_THAN",
    "GREATER_THAN",
    "SEMICOLON",
    "COMMA",
    "DOT",
    "COMMENT",
)

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
t_LEFT_BRACE = r"\{"
t_RIGHT_BRACE = r"\}"
t_LESS_THAN = r"<"
t_GREATER_THAN = r">"

t_SEMICOLON = r";"
t_DOT = r"."
t_COMMA = r","

t_ignore = " \t"


def t_IDENTIFIER(t):
    r"[a-zA-Z_][-a-zA-Z0-9_]*[\'?!]?"
    t.type = reserved_words.get(t.value, "IDENTIFIER")
    return t


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
    ("left", "DOT"),
    ("right", "UMINUS", "DEREF", "AMPERSAND"),
)

start = 'program'


def p_program(t):
    "program : declaration"
    t[0] = ast.Program([t[1]])


def p_program_multiple(t):
    "program : declaration program"
    t[0] = ast.Program([t[1]] + t[2])


def p_declaration_function(t):
    """declaration : type IDENTIFIER LEFT_PAREN parameter_list generic_params_opt RIGHT_PAREN LEFT_BRACE function_body RIGHT_BRACE"""  # noqa
    t[0] = ast.FunctionDeclaration(return_type=t[1],
                                   name=t[2],
                                   parameters=t[4],
                                   generic_parameters=t[5],
                                   body=t[8])


def p_declaration_newtype(t):
    """declaration : NEWTYPE IDENTIFIER EQUAL type SEMICOLON"""
    t[0] = ast.NewTypeDeclaration(name=t[2], inner_type=t[4])


def p_declaration_struct(t):
    """declaration : STRUCT IDENTIFIER generic_params_opt LEFT_BRACE struct_declaration_fields RIGHT_BRACE"""  # noqa
    t[0] = ast.StructTypeDeclaration(name=t[2],
                                     generic_parameters=t[3] or [],
                                     fields=t[5])


def p_declaration_union(t):
    """declaration : UNION IDENTIFIER generic_params_opt LEFT_BRACE union_declaration_fields RIGHT_BRACE"""  # noqa


def p_declaration_enum(t):
    """declaration : ENUM IDENTIFIER LEFT_BRACE enum_declaration_fields RIGHT_BRACE"""  # noqa


def p_parameter_list_list(t):
    """parameter_list : type IDENTIFIER COMMA parameter_list"""
    t[0] = [ast.FunctionParameter(name=t[2], type=t[1])] + t[4]


def p_parameter_list_empty(t):
    """parameter_list : empty"""
    t[0] = []


def p_parameter_list_item(t):
    """parameter_list : type IDENTIFIER comma_opt"""
    t[0] = [ast.FunctionParameter(name=t[2], type=t[1])]


def p_argument_list(t):
    """argument_list : expression comma_opt
                     | expression COMMA argument_list
                     | empty"""


def p_function_body_empty(t):
    "function_body : empty"
    t[0] = []


def p_function_body(t):
    """function_body : statement function_body"""
    t[0] = [t[1]] + t[2]


def p_type_basic(t):
    """type : IDENTIFIER generic_args_opt"""
    t[0] = ast.NamedTypeExpression(name=t[1], generic_arguments=t[2])


def p_type_tuple(t):
    """type : tuple_type"""


def p_tuple_type(t):
    """tuple_type : LEFT_PAREN type_list RIGHT_PAREN"""


def p_generic_params(t):
    """generic_params : LESS_THAN identifier_list GREATER_THAN"""
    t[0] = t[2]


def p_generic_params_opt(t):
    """generic_params_opt : generic_params
                          | empty"""
    t[0] = t[1]


def p_generic_args(t):
    """generic_args : LESS_THAN type_list GREATER_THAN"""
    t[0] = t[2]


def p_generic_args_opt(t):
    """generic_args_opt : generic_args
                        | empty"""
    t[0] = t[1]


def p_type_list(t):
    """type_list : type comma_opt"""
    t[0] = [t[1]]


def p_type_list_list(t):
    """type_list : type COMMA type_list"""
    t[0] = [t[1]] + t[3]


def p_identifier_list(t):
    """identifier_list : IDENTIFIER comma_opt"""
    t[0] = [t[1]]


def p_identifier_list_list(t):
    """identifier_list : IDENTIFIER COMMA identifier_list"""
    t[0] = [t[1]] + t[3]


def p_comma_opt(t):
    """comma_opt : COMMA
                 | empty"""


def p_struct_declaration_fields(t):
    """struct_declaration_fields : type IDENTIFIER struct_declaration_fields"""
    t[0] = [ast.StructTypeField(name=t[2], type=t[1])] + t[3]


def p_struct_declaration_fields_empty(t):
    """struct_declaration_fields : empty"""
    t[0] = []


def p_union_declaration_fields_symbol(t):
    """union_declaration_fields : IDENTIFIER union_declaration_fields"""


def p_union_declaration_fields_tuple(t):
    """union_declaration_fields : IDENTIFIER tuple_type union_declaration_fields"""  # noqa


def p_union_declaration_fields_struct(t):
    """union_declaration_fields : IDENTIFIER LEFT_BRACE struct_declaration_fields RIGHT_BRACE union_declaration_fields"""  # noqa


def p_union_declaration_fields_empty(t):
    """union_declaration_fields : empty"""


def p_enum_declaration_fields(t):
    """enum_declaration_fields : IDENTIFIER"""


def p_enum_declaration_fields_empty(t):
    """enum_declaration_fields : empty"""


def p_statement_break(t):
    """statement : BREAK IDENTIFIER SEMICOLON
                 | BREAK SEMICOLON"""
    label = t[2] if len(t) == 3 else None
    t[0] = ast.BreakStatement(label=label)


def p_statement_continue(t):
    """statement : CONTINUE IDENTIFIER SEMICOLON
                 | CONTINUE SEMICOLON"""
    label = t[2] if len(t) == 3 else None
    t[0] = ast.ContinueStatement(label=label)


def p_statement_return(t):
    """statement : RETURN expression SEMICOLON
                | RETURN SEMICOLON"""
    expr = t[2] if len(t) == 3 else None
    t[0] = ast.ReturnStatement(value=expr)


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


def p_assignment_target_field_access(t):
    "assignment_target : expression DOT IDENTIFIER"
    t[0] = ast.BinaryOperation(t[1], ast.Op.field, ast.Identifier(t[3]))


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
    print("Syntax error at line %d: unexpected '%s'" %
          (t.lineno, getattr(t, 'value', 'EOF')),
          file=sys.stderr)


parser = yacc.yacc(debug=True)


def parse(s):
    return parser.parse(s)
