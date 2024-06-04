import re

class Interpreter:
    def __init__(self, config):
        self.variables = {}
        self.config = config
        self.handlers = self.create_handlers(config)

    def create_handlers(self, config):
        handlers = {}
        for keyword in config.get("declare", []):
            handlers[keyword] = self.handle_declaration
        for keyword in config.get("display", []):
            handlers[keyword] = self.handle_display
        handlers["="] = self.handle_assignment
        return handlers

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
                        if self.validate_syntax(tokens, keyword):
                            handler(tokens)
                        matched = True
                        break

                if not matched:
                    print(f"Syntax Error: Unknown statement '{statement}'.")

    def validate_syntax(self, tokens, keyword):
        if keyword in self.config["declare"]:
            if len(tokens) < 5 or tokens[3] != "=":
                print("Syntax Error: Invalid variable declaration.")
                return False
            if tokens[1] != self.config["int"] and tokens[1] != self.config["string"]:
                print("Syntax Error: Invalid type for declaration.")
                return False
            if not re.match(r'^[a-zA-Z_]\w*$', tokens[2]):
                print(f"Syntax Error: Invalid variable name '{tokens[2]}'.")
                return False
        elif keyword in self.config["display"]:
            if len(tokens) < 2:
                print("Syntax Error: Display statement must have an expression.")
                return False
        elif "=" in tokens:
            if len(tokens) < 3 or tokens[1] != "=":
                print("Syntax Error: Invalid assignment statement.")
                return False
            if not re.match(r'^[a-zA-Z_]\w*$', tokens[0]):
                print(f"Syntax Error: Invalid variable name '{tokens[0]}'.")
                return False
        else:
            print("Syntax Error: Unrecognized syntax.")
            return False
        return True

    def handle_declaration(self, tokens):
        if len(tokens) < 5 or tokens[3] != "=":
            print("Syntax Error: Invalid variable declaration.")
            return
        var_type = tokens[1]
        var_name = tokens[2]
        expr = " ".join(tokens[4:])
        value = self.evaluate_expression(expr.split())

        if var_type == self.config["int"]:
            value = int(value)
        elif var_type == self.config["string"]:
            value = str(value.strip('"'))
        else:
            print(f"Syntax Error: Unknown type '{var_type}' for declaration.")
            return
        
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
        "declare": ["grahs", "hero"],   # Change this keyword to anything you want for variable declaration
        "display": ["display-"], # Change this keyword to anything you want for display
        "int": "inte",         # Change this keyword to anything you want for integer type
        "string": "string"    # Change this keyword to anything you want for string type
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
