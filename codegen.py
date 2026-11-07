from parser import (
    parse_program,
    NODE_PROGRAM, NODE_DECLARATION, NODE_ASSIGNMENT, NODE_PRINT,
    NODE_IF, NODE_WHILE, NODE_BLOCK,
    NODE_BINARY_OPERATION, NODE_UNARY_MINUS, NODE_NUMBER, NODE_VARIABLE,
)

ONE_INDENT = "    "

def generate_expression(expression_node, needs_parentheses=True):
    node_type = expression_node.node_type

    if node_type == NODE_NUMBER:

        return str(expression_node.value)

    if node_type == NODE_VARIABLE:

        return expression_node.value

    if node_type == NODE_UNARY_MINUS:

        operand_node = expression_node.children[0]
        operand_text = generate_expression(operand_node, needs_parentheses=True)
        return "-" + operand_text

    if node_type == NODE_BINARY_OPERATION:

        left_node = expression_node.children[0]
        right_node = expression_node.children[1]
        operation_sign = expression_node.value          # +, *, < ...

        left_text = generate_expression(left_node, needs_parentheses=True)
        right_text = generate_expression(right_node, needs_parentheses=True)
        full_text = f"{left_text} {operation_sign} {right_text}"

        if needs_parentheses:
            return "(" + full_text + ")"
        return full_text

    raise ValueError(f"Невідомий вузол виразу: {node_type}")


def generate_statement(statement_node, indent_level=0):
    node_type = statement_node.node_type
    indent = ONE_INDENT * indent_level

    if node_type == NODE_DECLARATION or node_type == NODE_ASSIGNMENT:

        variable_name = statement_node.value
        value_node = statement_node.children[0]
        value_text = generate_expression(value_node, needs_parentheses=False)
        return f"{indent}{variable_name} = {value_text}\n"

    if node_type == NODE_PRINT:

        expression_node = statement_node.children[0]
        expression_text = generate_expression(expression_node, needs_parentheses=False)
        return f"{indent}print({expression_text})\n"

    if node_type == NODE_IF:

        condition_node = statement_node.children[0]
        then_block_node = statement_node.children[1]

        condition_text = generate_expression(condition_node, needs_parentheses=False)
        result_text = f"{indent}if {condition_text}:\n"
        result_text += generate_statement(then_block_node, indent_level + 1)

        if len(statement_node.children) == 3:        # є гілка else
            else_block_node = statement_node.children[2]
            result_text += f"{indent}else:\n"
            result_text += generate_statement(else_block_node, indent_level + 1)
        return result_text

    if node_type == NODE_WHILE:

        condition_node = statement_node.children[0]
        loop_body_node = statement_node.children[1]

        condition_text = generate_expression(condition_node, needs_parentheses=False)
        result_text = f"{indent}while {condition_text}:\n"
        result_text += generate_statement(loop_body_node, indent_level + 1)
        return result_text

    if node_type == NODE_BLOCK:
        block_text = ""
        for inner_statement_node in statement_node.children:
            block_text += generate_statement(inner_statement_node, indent_level)
        return block_text

    raise ValueError(f"Невідомий вузол інструкції: {node_type}")

def generate_python_code(program_node):
    """Приймає корінь дерева (вузол Program), повертає текст програми на Python."""
    python_code = ""
    for statement_node in program_node.children:
        python_code += generate_statement(statement_node, indent_level=0)
    return python_code


if __name__ == "__main__":
    test_program = """
    let a = 5;
    let b = a * 2 + 1;
    print(b);
    if (b > 10) { print(a); } else { print(0); }
    while (a > 0) { a = a - 1; }
    print(a);
    """

    syntax_tree = parse_program(test_program)
    if syntax_tree is not None:
        generated_code = generate_python_code(syntax_tree)

        print("=== Згенерований код на Python ===")
        print(generated_code)

        print("=== Результат виконання ===")
        exec(generated_code)
