import os
import sys
import webbrowser
from pathlib import Path

from parser import parse_program
from codegen import generate_python_code
from ast_to_json import create_tree_html


def read_text_file(file_path):
    """Читає текстовий файл і повертає його вміст одним рядком."""
    with open(file_path, "r", encoding="utf-8") as input_file:
        return input_file.read()


def main():
    # тут лежить main.py
    project_folder = os.path.dirname(os.path.abspath(__file__))

    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
    else:
        input_file_path = os.path.join(project_folder, "examples", "example1.txt")

    if not os.path.exists(input_file_path):
        print(f"Файл не знайдено: {input_file_path}")
        print("Створіть папку examples і покладіть туди файл з програмою.")
        return


    program_text = read_text_file(input_file_path)
    print(f"=== Програма з файлу {os.path.basename(input_file_path)} ===")
    print(program_text)


    syntax_tree = parse_program(program_text)
    if syntax_tree is None:
        print("Програму не вдалося розібрати — виправте помилки вище.")
        return

    print("=== Дерево AST ===")
    syntax_tree.show()


    generated_code = generate_python_code(syntax_tree)
    print("\n=== Згенерований код на Python ===")
    print(generated_code)

    # Зберігаємо результат у папку output
    output_folder = os.path.join(project_folder, "output")
    os.makedirs(output_folder, exist_ok=True)

    generated_file_path = os.path.join(output_folder, "generated_program.py")
    with open(generated_file_path, "w", encoding="utf-8") as generated_file:
        generated_file.write(generated_code)


    print("=== Результат виконання ===")
    exec(generated_code)

    tree_page_path = os.path.join(output_folder, "ast_tree.html")
    create_tree_html(syntax_tree, tree_page_path)
    print(f"\nДерево збережено: {tree_page_path}")
    webbrowser.open(Path(tree_page_path).as_uri())


if __name__ == "__main__":
    main()
