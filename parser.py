import ply.yacc as yacc

# Беремо з нашого файлу lexer.py список токенів і функцію створення лексера
from lexer import tokens, build_lexer

NODE_PROGRAM = "Program"                    # корінь дерева — уся програма
NODE_DECLARATION = "Declaration"            # оголошення змінної:   let a = 5;
NODE_ASSIGNMENT = "Assignment"              # присвоєння:           a = a - 1;
NODE_PRINT = "Print"                        # вивід на екран:       print(a);
NODE_IF = "If"                              # умова:                if (...) {...}
NODE_WHILE = "While"                        # цикл:                 while (...) {...}
NODE_BLOCK = "Block"                        # блок інструкцій у фігурних дужках { }
NODE_BINARY_OPERATION = "BinaryOperation"   # операція з двома операндами: a + b
NODE_UNARY_MINUS = "UnaryMinus"             # мінус перед виразом:  -a
NODE_NUMBER = "Number"                      # число:                5
NODE_VARIABLE = "Variable"                  # використання змінної: a

class Node:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children if children is not None else []

    def show(self, indent_level=0):
        """Виводить дерево в консоль: кожен рівень вкладеності — відступ."""
        line_text = self.node_type
        if self.value is not None:
            line_text += f" ({self.value})"
        print("    " * indent_level + line_text)
        for child_node in self.children:
            child_node.show(indent_level + 1)

precedence = (
    ("nonassoc", "EQUALS", "NOT_EQUALS", "LESS", "GREATER",
     "LESS_OR_EQUAL", "GREATER_OR_EQUAL"),               # найнижчий
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "UNARY_MINUS"),                            # найвищий (мінус перед числом: -5)
)


def p_program(rule_parts):
    """program : statement_list"""
    # Уся програма — це список інструкцій. Робимо корінь дерева.
    all_statements = rule_parts[1]
    rule_parts[0] = Node(NODE_PROGRAM, children=all_statements)


def p_statement_list(rule_parts):
    """statement_list : statement_list statement
                      | statement"""
    # Список інструкцій
    if len(rule_parts) == 3:               # список + інструкція
        statements_so_far = rule_parts[1]
        new_statement = rule_parts[2]
        rule_parts[0] = statements_so_far + [new_statement]
    else:                                  # одна інструкція
        only_statement = rule_parts[1]
        rule_parts[0] = [only_statement]


def p_statement(rule_parts):
    """statement : declaration
                 | assignment
                 | print_statement
                 | if_statement
                 | while_statement"""

    rule_parts[0] = rule_parts[1]


def p_declaration(rule_parts):
    """declaration : LET IDENTIFIER ASSIGN expression SEMICOLON"""

    variable_name = rule_parts[2]          # a
    start_value = rule_parts[4]            # вираз праворуч від "="
    rule_parts[0] = Node(NODE_DECLARATION, value=variable_name,
                         children=[start_value])


def p_assignment(rule_parts):
    """assignment : IDENTIFIER ASSIGN expression SEMICOLON"""
    # Присвоєння нового значення:   a = a - 1;
    variable_name = rule_parts[1]          # a
    new_value = rule_parts[3]              # вираз праворуч від "="
    rule_parts[0] = Node(NODE_ASSIGNMENT, value=variable_name,
                         children=[new_value])


def p_print_statement(rule_parts):
    """print_statement : PRINT LEFT_PAREN expression RIGHT_PAREN SEMICOLON"""
    # Вивід на екран
    expression_to_print = rule_parts[3]    # те, що стоїть у дужках
    rule_parts[0] = Node(NODE_PRINT, children=[expression_to_print])


def p_if_statement(rule_parts):
    """if_statement : IF LEFT_PAREN expression RIGHT_PAREN block
                    | IF LEFT_PAREN expression RIGHT_PAREN block ELSE block"""

    condition = rule_parts[3]              # вираз у дужках після if
    then_block = rule_parts[5]
    if len(rule_parts) == 6:
        rule_parts[0] = Node(NODE_IF, children=[condition, then_block])
    else:
        else_block = rule_parts[7]
        rule_parts[0] = Node(NODE_IF,
                             children=[condition, then_block, else_block])


def p_while_statement(rule_parts):
    """while_statement : WHILE LEFT_PAREN expression RIGHT_PAREN block"""

    condition = rule_parts[3]              # поки умова правдива, повторюємо
    loop_body = rule_parts[5]              # блок, який повторюється
    rule_parts[0] = Node(NODE_WHILE, children=[condition, loop_body])


def p_block(rule_parts):
    """block : LEFT_BRACE statement_list RIGHT_BRACE"""

    statements_inside = rule_parts[2]
    rule_parts[0] = Node(NODE_BLOCK, children=statements_inside)


# Вирази

def p_expression_binary(rule_parts):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EQUALS expression
                  | expression NOT_EQUALS expression
                  | expression LESS expression
                  | expression GREATER expression
                  | expression LESS_OR_EQUAL expression
                  | expression GREATER_OR_EQUAL expression"""
    # Операція з двома операндами: ліве_значення  знак  праве_значення.
    left_operand = rule_parts[1]           # зліва від знака
    operation_sign = rule_parts[2]         # сам знак: +, *, < ...
    right_operand = rule_parts[3]          # справа від знака
    rule_parts[0] = Node(NODE_BINARY_OPERATION, value=operation_sign,
                         children=[left_operand, right_operand])


def p_expression_unary_minus(rule_parts):
    """expression : MINUS expression %prec UNARY_MINUS"""
    operand = rule_parts[2]
    rule_parts[0] = Node(NODE_UNARY_MINUS, children=[operand])


def p_expression_parentheses(rule_parts):
    """expression : LEFT_PAREN expression RIGHT_PAREN"""
    expression_inside = rule_parts[2]
    rule_parts[0] = expression_inside


def p_expression_number(rule_parts):
    """expression : NUMBER"""
    number_value = rule_parts[1]
    rule_parts[0] = Node(NODE_NUMBER, value=number_value)


def p_expression_variable(rule_parts):
    """expression : IDENTIFIER"""
    variable_name = rule_parts[1]
    rule_parts[0] = Node(NODE_VARIABLE, value=variable_name)

def p_error(bad_token):
    if bad_token is None:
        print("[Синтаксична помилка] Несподіваний кінець програми "
              "(можливо, не закрито дужку або пропущено ';')")
    else:
        print(f"[Синтаксична помилка] Рядок {bad_token.lineno}: "
              f"несподіваний елемент '{bad_token.value}'")


grammar_parser = yacc.yacc(debug=True)


def parse_program(program_text):
    """Приймає текст програми, повертає корінь дерева AST (або None при помилці)."""
    lexer = build_lexer()
    lexer.lineno = 1
    return grammar_parser.parse(program_text, lexer=lexer)

if __name__ == "__main__":
    test_program = """
    let a = 5;
    let b = a * 2 + 1;
    print(b);
    if (b > 10) { print(a); } else { print(0); }
    while (a > 0) { a = a - 1; }
    """

    print("=== Правильна програма ===")
    syntax_tree = parse_program(test_program)
    if syntax_tree is not None:
        syntax_tree.show()

    print("\n=== Програма з помилкою (пропущено ';') ===")
    broken_program = "let a = 5\nprint(a);"
    parse_program(broken_program)
