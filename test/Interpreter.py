import re

class Interpreter:
    def __init__(self, config):
        self.variables = {}
        self.undefined_variables = set()
        self.config = config
        self.handlers = {
            self.config["declare"]: self.handle_declaration,
            self.config["display"]: self.handle_display,
            "=": self.handle_assignment
        }

    def interpret(self, program):
        lines = program.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                if not line.endswith('.'):
                    print("Syntax Error: Statements must end with a period.")
                    return
                statement = line[:-1].strip()
                tokens = statement.split()
                matched = False

                for keyword, handler in self.handlers.items():
                    if tokens[0] == keyword or (len(tokens) > 1 and tokens[1] == keyword):
                        handler(tokens)
                        matched = True
                        break

                if not matched:
                    print(f"Syntax Error: Unknown statement '{statement}'.")

    def handle_declaration(self, tokens):
        if len(tokens) < 4 or tokens[2] != "=":
            print("Syntax Error: Invalid variable declaration.")
            return
        var_name = tokens[1]
        expr = " ".join(tokens[3:])
        value = self.evaluate_expression(expr.split())
        self.variables[var_name] = value

    def handle_display(self, tokens):
        expr_tokens = tokens[1:]
        value = self.evaluate_expression(expr_tokens)
        if value is not None:
            print(value)

    def handle_assignment(self, tokens):
        var_name = tokens[0]
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' is used before being declared with '{self.config["declare"]}'.")
            return
        expr = " ".join(tokens[2:])
        value = self.evaluate_expression(expr.split())
        self.variables[var_name] = value

    def evaluate_expression(self, tokens):
        stack = []
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

        def apply_operator(operators, values):
            operator = operators.pop()
            right = values.pop()
            left = values.pop()
            if operator == '+':
                values.append(left + right)
            elif operator == '-':
                values.append(left - right)
            elif operator == '*':
                values.append(left * right)
            elif operator == '/':
                if right == 0:
                    print("Error: Division by zero.")
                    return None
                values.append(left / right)

        operators = []
        values = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.isdigit():
                values.append(int(token))
            elif re.match(r'^[a-zA-Z_]\w*$', token) and token in self.variables:
                values.append(self.variables[token])
            elif re.match(r'^[a-zA-Z_]\w*$', token):
                print(f"Error: Variable '{token}' is not defined.")
                return None
            elif token in precedence:
                while (operators and operators[-1] in precedence and
                       precedence[operators[-1]] >= precedence[token]):
                    apply_operator(operators, values)
                operators.append(token)
            elif token.startswith('"') and token.endswith('"'):
                values.append(token.strip('"'))
            else:
                print(f"Syntax Error: Unrecognized token '{token}'.")
                return None
            i += 1

        while operators:
            apply_operator(operators, values)

        if len(values) != 1:
            print("Error: Invalid expression.")
            return None
        return values[0]

def main():
    config = {
        "declare": "grah",   # Change this keyword to anything you want for variable declaration
        "display": "display-"  # Change this keyword to anything you want for display
    }
    
    interpreter = Interpreter(config)
    file_name = "test/hero.GRAH"

    try:
        with open(file_name, 'r') as file:
            code = file.read()
            interpreter.interpret(code)
    except FileNotFoundError:
        print("File not found.")

if __name__ == "__main__":
    main()
