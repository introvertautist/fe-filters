import ply.lex as lex
import ply.yacc as yacc


parsed_filter = 'event eq 10'

tokens = [
    'NE',  # Отрицание: 'a not b'
    'AND',  # Логическое И: 'a and b'
    'OR',  # Логическое ИЛИ: 'a or b'
    'EQ',  # Эквивалентность: 'a is b'
    'GT',  # Больше чем: 'a > b'
    'GE',  # Больше или равен: 'a >= b'
    'LT',  # Меньше чем: 'a < b'
    'LE',  # Меньше или равен: 'a <= b'
    'PARAM_VALUE',  # Значение параметра(число, строка, или null): 'event="Page open"'
    'NUMBER',  # Число
    'LPAREN',  # Левая скобка: '('
    'RPAREN',  # Правая скобка: ')'
    'PARAM'  # Название параметров: 'event'
]

def t_NE(t):
    'ne'
    return t

def t_AND(t):
    'and'
    return t

def t_EQ(t):
    'eq'
    return t

def t_OR(t):
    'or'
    return t

def t_GT(t):
    'gt'
    return t

def t_GE(t):
    'ge'
    return t

def t_LT(t):
    'lt'
    return t

def t_LE(t):
    'le'
    return t

def t_NUMBER(t):
    r'\d+'
    return t

t_PARAM_VALUE = r'(\"[a-zA-Z_][a-zA-Z0-9_ ]*\")|(null)|(\d+)'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_PARAM = r'[a-zA-Z_][a-zA-Z0-9_]*'

t_ignore = " \t"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()
lexer.input(parsed_filter)

print("GOT: ", parsed_filter)
print("TOKENS:")
while True:
    token = lexer.token()
    if not token:
        break
    print("\t", token)

precedence = (
    ('left', 'NE', 'EQ'),
    ('left', 'GT', 'GE', 'LT', 'LE'),
    ('left', 'AND'),
    ('left', 'OR'),
)

def p_statement_expr(t):
    'statement : expression'
    print("RESULT: ", t[1])

def p_expression_ne_number(t):
    'expression : PARAM NE NUMBER'
    t[0] = f"({t[1]} != {t[3]})"

def p_expression_ne(t):
    'expression : PARAM NE PARAM_VALUE'
    print("in ne")
    if t[3] == 'null':
        t[0] = f"({t[1]} IS NOT NULL)"
    else:
        t[0] = f"({t[1]} != {t[3]})"

def p_expression_compare(t):
    '''expression : PARAM GT NUMBER
                  | PARAM GE NUMBER
                  | PARAM LT NUMBER
                  | PARAM LE NUMBER'''
    if t[2] == 'gt':
        t[0] = f"({t[1]} > {t[3]})"
    elif t[2] == 'ge':
        t[0] = f"({t[1]} >= {t[3]})"
    elif t[2] == 'lt':
        t[0] = f"({t[1]} < {t[3]})"
    else:
        t[0] = f"({t[1]} <= {t[3]})"

def p_expression_logic(t):
    '''expression : expression AND expression
                  | expression OR expression'''
    if t[2] == 'and':
        t[0] = f"{t[1]} AND {t[3]}"
    elif t[2] == 'or': t[0] = f"{t[1]} OR {t[3]}"

def p_expression_eq_number(t):
    'expression : expression EQ NUMBER'
    t[0] = f'({t[1]} = {t[3]})'

def p_expression_eq(t):
    'expression : expression EQ PARAM_VALUE'
    if t[3] == 'null':
        t[0] = f'{t[1]} IS NULL'
    else:
        t[0] = f'{t[1]} = {t[3]}'

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = f"({t[2]})"

def p_expression_name(t):
    'expression : PARAM'
    t[0] = t[1]

def p_error(t):
    print("Syntax error at '%s'" % t.value)


parser = yacc.yacc()
parser.parse(parsed_filter)
