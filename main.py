from Interpreter import Interpreter

def main():
    interpreter = Interpreter()
    file_name = "hero.GRAH"

    try:
        with open(file_name, 'r') as file:
            code = file.read()
            interpreter.interpret(code)
    except FileNotFoundError:
        print("File not found.")    

if __name__ == "__main__":
    main()