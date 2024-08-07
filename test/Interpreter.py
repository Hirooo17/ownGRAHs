import re

class Interpreter:
    def __init__(self, config):
        self.variables = {}
        self.config = config
        self.handlers = self.create_handlers(config)
        self.line_buffer = ""  # Buffer to keep track of the current line content
        self.last_print_was_newline = True  # Flag to track if the last print was a newline

    def create_handlers(self, config):
        handlers = {}
        for keyword in config.get("declare", []):
            handlers[keyword] = self.handle_declaration
        for keyword in config.get("display", []):
            handlers[keyword] = self.handle_display
        handlers["="] = self.handle_assignment
        handlers[config["for"]] = self.handle_for_loop
        handlers[config["print"]] = self.handle_print
        handlers[config["if"]] = self.handle_if_statement
        handlers[config["switch"]] = self.handle_switch_statement
        return handlers

    def interpret(self, program):
        lines = program.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line:
                if not line.endswith('.') and not line.endswith('{') and line != "}":
                    print("Syntax Error: Statements must end with a period.")
                    return
                statement = line[:-1].strip() if line.endswith('.') else line
                tokens = self.tokenize(statement)
                matched = False

                for keyword, handler in self.handlers.items():
                    if tokens[0] == keyword or (len(tokens) > 1 and tokens[1] == keyword):
                        if self.validate_syntax(tokens, keyword):
                            if keyword == self.config["for"]:
                                i = self.handle_for_loop(tokens, lines, i)
                            elif keyword == self.config["if"]:
                                i = self.handle_if_statement(tokens, lines, i)
                            elif keyword == self.config["switch"]:
                                i = self.handle_switch_statement(tokens, lines, i)
                            else:
                                handler(tokens)
                        matched = True
                        break

                if not matched:
                    print(f"Syntax Error: Unknown statement '{statement}'.")

            i += 1

    def tokenize(self, statement):
        
        # This method splits the statement into tokens while preserving quoted strings as single tokens
        return re.findall(r'\".*?\"|\S+', statement)

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
        elif keyword == self.config["for"]:
            if len(tokens) < 5 or tokens[2] != "in" or tokens[3] != "range" or not re.match(r'\d+', tokens[4]) or not tokens[-1].endswith("{"):
                print("Syntax Error: Invalid 'for' loop syntax.")
                return False
        elif keyword in [self.config["print"]]:  
            if len(tokens) < 2:
                print(f"Syntax Error: '{keyword}' statement must have an expression.")
                return False
        elif keyword == self.config["if"]:
            if len(tokens) < 4 or not tokens[-1].endswith("{"):
                print("Syntax Error: Invalid 'if' statement syntax.")
                return False
        elif keyword == self.config["switch"]:
            if len(tokens) < 2 or not tokens[-1].endswith("{"):
                print("Syntax Error: Invalid 'switch' statement syntax.")
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
            if not self.last_print_was_newline:
                print()  # Print a new line before printing the value
            print(value)
        self.last_print_was_newline = True  # Update flag
            
    def handle_print(self, tokens):
        expr_tokens = tokens[1:]
        value = self.evaluate_expression(expr_tokens)
        if value is not None:
            if not self.last_print_was_newline:
                print('', end='')  # Ensure no new line is printed
            print(value, end='')
        self.last_print_was_newline = False  # Update flag

    def handle_assignment(self, tokens):
        var_name = tokens[0]
        if var_name not in self.variables:
            print(f"Error: Variable '{var_name}' is used before being declared with '{self.config['declare']}'.")
            return
        expr = " ".join(tokens[2:])
        value = self.evaluate_expression(expr.split())
        self.variables[var_name] = value

    def handle_for_loop(self, tokens, lines, start_index):
        loop_var = tokens[1]
        range_value = int(tokens[4].strip("()"))

        loop_body = []
        i = start_index + 1
        nested_level = 1

        while i < len(lines):
            line = lines[i].strip()
            if line == "{":
                nested_level += 1
            elif line == "}":
                nested_level -= 1
                if nested_level == 0:
                    break
            loop_body.append(line)
            i += 1

        if nested_level != 0:
            print("Syntax Error: Mismatched braces in 'for' loop.")
            return start_index

        for j in range(range_value):
            self.variables[loop_var] = j
            self.interpret("\n".join(loop_body))
        
        return i

    def handle_if_statement(self, tokens, lines, start_index):
        condition_expr = " ".join(tokens[1:-1])
        condition = self.evaluate_expression(condition_expr.split())
        
        if_body = []
        else_body = []
        current_body = if_body
        i = start_index + 1
        nested_level = 1

        while i < len(lines):
            line = lines[i].strip()
            print("Debugging mode:")
            print(f"Processing line: {line}, nested_level: {nested_level}")
            
            if line == "{":
                nested_level += 1
            elif line == "}":
                nested_level -= 1
                if nested_level == 0:
                    break
            elif line.startswith(self.config["else"]) and nested_level == 1:
                print("Switching to else body")
                current_body = else_body
                continue
            current_body.append(line)
            i += 1

        if nested_level != 0:
            print("Syntax Error: Mismatched braces in 'if' statement.")
            return start_index

        # Remove the 'else {' line from if_body
        if len(if_body) > 0 and if_body[-1] == self.config["else"] + " {":
            if_body.pop()
        
        print("If body:", if_body)
        print("Else body:", else_body)
        print("Output:\n")
        
        if condition:
            self.interpret("\n".join(if_body))
        else:
            self.interpret("\n".join(else_body))
        
        return i

    def handle_switch_statement(self, tokens, lines, start_index):
        switch_var = tokens[1]

        case_bodies = {}
        default_body = []
        current_case = None
        i = start_index + 1
        nested_level = 1

        while i < len(lines):
            line = lines[i].strip()
            if line == "{":
                nested_level += 1
            elif line == "}":
                nested_level -= 1
                if nested_level == 0:
                    break
            elif line.startswith(self.config["case"]):
                current_case = line.split()[1].strip(":")
                case_bodies[current_case] = []
            elif line.startswith(self.config["default"]):
                current_case = "default"
            elif current_case is not None:
                if current_case == "default":
                    default_body.append(line)
                else:
                    case_bodies[current_case].append(line)
            i += 1

        if nested_level != 0:
            print("Syntax Error: Mismatched braces in 'switch' statement.")
            return start_index

        if switch_var in self.variables:
            switch_value = self.variables[switch_var]
            if str(switch_value) in case_bodies:
                self.interpret("\n".join(case_bodies[str(switch_value)]))
            elif "default" in case_bodies:
                self.interpret("\n".join(case_bodies["default"]))
        else:
            print(f"Error: Variable '{switch_var}' is not defined.")
        
        return i

    def evaluate_expression(self, tokens):
        stack = []
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '>': 0, '<': 0, '>=': 0, '<=': 0, '==': 0, '!=': 0}

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
            elif operator == '>':
                values.append(left > right)
            elif operator == '<':
                values.append(left < right)
            elif operator == '>=':
                values.append(left >= right)
            elif operator == '<=':
                values.append(left <= right)
            elif operator == '==':
                values.append(left == right)
            elif operator == '!=':
                values.append(left != right)

        operators = []
        values = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.isdigit():
                values.append(int(token))
            elif re.match(r'^[a-zA-Z_]\w*$', token):
                if token in self.variables:
                    values.append(self.variables[token])
                else:
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
        "declare": ["grah", "hero"],   # Change this keyword to anything you want for variable declaration
        "display": ["display-"], # Change this keyword to anything you want for display
        "int": "int",         # Change this keyword to anything you want for integer type
        "string": "string",    # Change this keyword to anything you want for string type
        "for": "for",          # Change this keyword to anything you want for 'for' loop
        "if": "if",            # Change this keyword to anything you want for 'if' statement
        "else": "else",        # Change this keyword to anything you want for 'else' statement
        "print": "print",
        "switch": "switch",    # Add this keyword for 'switch' statement
        "case": "case",        # Add this keyword for 'case' statement
        "default": "default",  # Add this keyword for 'default' case
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
