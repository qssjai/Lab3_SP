# Lab 3: транслятор простої мови на lex/yacc (PLY)

Простий інтерпретатор власної імперативної мови: змінні (`let`), присвоєння, `print`, `if/else`, `while`, арифметика і порівняння. Програма розбирає код (лексер + LALR-парсер на PLY), будує AST, генерує з нього код на Python, виконує його і малює дерево в браузері через d3.js.

## Запуск
    pip install -r requirements.txt
    python main.py                                # example1.txt
    python main.py examples/example2.txt
    python main.py examples/example3_error.txt    # програма з синтаксичною помилкою

Для візуалізації дерева потрібен інтернет (підключається d3.js).

## Файли
- `lexer.py`: лексичний аналіз, токени
- `parser.py`: граматика, побудова AST, повідомлення про помилки
- `parsetab.py`, `parser.out`: таблиці та звіт LALR, які генерує PLY
- `codegen.py`: генерація коду на Python з AST
- `ast_to_json.py`: візуалізація AST у браузері (d3.js)
- `main.py`: запускає весь процес
- `examples/`: приклади програм мовою, один із помилкою
