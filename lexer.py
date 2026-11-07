import ply.lex as lex

reserved_words = {
    "let": "LET",        # оголошення змінної:   let a = 5;
    "print": "PRINT",    # вивід на екран:       print(a);
    "if": "IF",          # умова:                if (a > 3) { ... }
    "else": "ELSE",      # інакше:               else { ... }
    "while": "WHILE",    # цикл:                 while (a > 0) { ... }
}

tokens = [
    "NUMBER",         # число: 5, 3.14
    "IDENTIFIER",     # ім'я змінної: a, counter, total_sum

    "PLUS",           # +
    "MINUS",          # -
    "TIMES",          # *
    "DIVIDE",         # /

    "ASSIGN",         # =   (присвоєння)
    "EQUALS",         # ==  (порівняння на рівність)
    "NOT_EQUALS",     # !=
    "LESS",           # <
    "GREATER",        # >
    "LESS_OR_EQUAL",  # <=
    "GREATER_OR_EQUAL",  # >=

    "LEFT_PAREN",     # (
    "RIGHT_PAREN",    # )
    "LEFT_BRACE",     # {
    "RIGHT_BRACE",    # }
    "SEMICOLON",      # ;
] + list(reserved_words.values())   # додаємо до списку LET, PRINT, IF, ELSE, WHILE

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"

t_ASSIGN = r"="
t_EQUALS = r"=="
t_NOT_EQUALS = r"!="
t_LESS = r"<"
t_GREATER = r">"
t_LESS_OR_EQUAL = r"<="
t_GREATER_OR_EQUAL = r">="

t_LEFT_PAREN = r"\("
t_RIGHT_PAREN = r"\)"
t_LEFT_BRACE = r"\{"
t_RIGHT_BRACE = r"\}"
t_SEMICOLON = r";"


t_ignore = " \t"


def t_COMMENT(matched_token):
    r"//.*"
    pass


def t_NUMBER(matched_token):
    r"\d+\.\d+|\d+"
    if "." in matched_token.value:
        matched_token.value = float(matched_token.value)
    else:
        matched_token.value = int(matched_token.value)
    return matched_token


def t_IDENTIFIER(matched_token):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    matched_token.type = reserved_words.get(matched_token.value, "IDENTIFIER")
    return matched_token


def t_newline(matched_token):
    r"\n+"
    matched_token.lexer.lineno += len(matched_token.value)

def t_error(matched_token):
    print(f"[Лексична помилка] Рядок {matched_token.lexer.lineno}: "
          f"невідомий символ '{matched_token.value[0]}'")
    matched_token.lexer.skip(1)   # пропускаємо цей символ і йдемо далі

def build_lexer():
    return lex.lex()

if __name__ == "__main__":
    test_program = """
    // це коментар
    let a = 5;
    let b = a * 2 + 3.5;
    if (b >= 10) { print(b); }
    while (a > 0) { a = a - 1; }
    let c = 7 @ 2;
    """

    lexer = build_lexer()
    lexer.input(test_program)

    print("Лексема  ->  Тип токена")
    print("-" * 30)
    while True:
        found_token = lexer.token()
        if found_token is None:
            break
        print(f"{found_token.value!r:10} ->  {found_token.type}")
