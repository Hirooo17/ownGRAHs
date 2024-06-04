class Interpreter:
    def __init__(self):
        self.variables = {}  # Dictionary to store variable assignments
        self.undefined_variables = set()  # Set to track undefined variables

    def interpret(self, program):
        # Split the program into lines and execute each line
        lines = program.split('\n')
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                if not line.endswith('.'):
                    print("Syntax Error: Statements must end with a period.")
                    return
                self.execute(line[:-1].strip())  # Remove the trailing period before executing

    def execute(self, statement):
        # Split the statement into tokens
        tokens = statement.split()

        # Check if it's a variable declaration statement with "grah" keyword
        if tokens[0] == "grah":
            if len(tokens) < 4 or tokens[2] != "=":  # Check for correct syntax
                print("Syntax Error: Invalid variable declaration.")
                return
            var_name = tokens[1]  # Get the variable name
            expr = " ".join(tokens[3:])  # Get the expression to evaluate
            value = self.evaluate_expression(expr.split())
            self.variables[var_name] = value
            self.undefined_variables.discard(var_name)
        # Check if it's a print statement
        elif tokens[0] == "display-":
            # Evaluate the expression and print the result
            expr_tokens = tokens[1:]
            value = self.evaluate_expression(expr_tokens)
            if value is not None:  # Add a check to ensure value is not None
                print(value)
            
        # Check if it's a variable assignment statement
        elif len(tokens) >= 3 and tokens[1] == "=":  # Adjust condition to check for assignment
            # Extract variable name and expression
            var_name = tokens[0]
            # Check if the variable is declared before
            if var_name not in self.variables:
                print(f"Error: Variable '{var_name}' is used before being declared with 'grah'.")
                return
            expr = " ".join(tokens[2:])
            # Evaluate the expression and assign the value to the variable
            value = self.evaluate_expression(expr.split())
            self.variables[var_name] = value
        else: 
            print("Syntax Error: Unknown statement.")    

    def evaluate_expression(self, tokens):
        # Stack to hold intermediate results
        stack = []

        # Operator precedence
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

        # Function to apply an operator to two operands
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

        # Shunting-yard algorithm to parse and evaluate the expression
        operators = []
        values = []

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token.isdigit():
                values.append(int(token))
            elif token.startswith('"') and token.endswith('"'):
                values.append(token.strip('"'))
            elif token in self.variables:
                values.append(self.variables[token])
            elif token in precedence:
                while (operators and operators[-1] in precedence and
                       precedence[operators[-1]] >= precedence[token]):
                    apply_operator(operators, values)
                operators.append(token)
            else:
                print(f"Syntax Error: Unrecognized token '{token}'.")
                print(f"Syntax Error: add spaces '{token}'.")
                return None
            i += 1

        while operators:
            apply_operator(operators, values)

        if len(values) != 1:
            print("Error: Invalid expression.")
            return None
        return values[0]

def main():
    interpreter = Interpreter()
    file_name = "agams.GRAH"

    try:
        with open(file_name, 'r') as file:
            code = file.read()
            interpreter.interpret(code)
    except FileNotFoundError:
        print("File not found.")

if __name__ == "__main__":
    main()
