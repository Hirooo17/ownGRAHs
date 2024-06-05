import tkinter as tk
from tkinter import scrolledtext, Toplevel
from tkinter import ttk
from PIL import Image, ImageTk
from interpreter import Interpreter
import re

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        if not self.textwidget:
            return
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, font=("Consolas", 10, "bold"))
            i = self.textwidget.index("%s+1line" % i)

class CustomText(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        scrolledtext.ScrolledText.__init__(self, *args, **kwargs)

        self.linenumbers = None
        self.bind("<<Change>>", self._on_change)
        self.bind("<Configure>", self._on_change)
        self.bind("<KeyRelease>", self._on_key_release)

        self.tag_configure("integer", foreground="red")
        self.tag_configure("string", foreground="yellow")
        self.tag_configure("error", background="lightcoral")

    def attach(self, linenumbers):
        self.linenumbers = linenumbers
        self.linenumbers.attach(self)

    def _on_change(self, event):
        if self.linenumbers:
            self.linenumbers.redraw()
        self.highlight_syntax()

    def _on_key_release(self, event):
        self.event_generate("<<Change>>", when="tail")

    def highlight_syntax(self):
        self.remove_tags()
        code = self.get("1.0", tk.END)

        # Highlight integers
        for match in re.finditer(r'\b\d+\b', code):
            start, end = match.span()
            start_index = self.index(f"1.0 + {start}c")
            end_index = self.index(f"1.0 + {end}c")
            self.tag_add("integer", start_index, end_index)

        # Highlight strings
        for match in re.finditer(r'".*?"', code):
            start, end = match.span()
            start_index = self.index(f"1.0 + {start}c")
            end_index = self.index(f"1.0 + {end}c")
            self.tag_add("string", start_index, end_index)

    def remove_tags(self):
        self.tag_remove("integer", "1.0", tk.END)
        self.tag_remove("string", "1.0", tk.END)
        self.tag_remove("error", "1.0", tk.END)

    def highlight_error(self, line_num):
        start_index = f"{line_num}.0"
        end_index = f"{line_num}.end"
        self.tag_add("error", start_index, end_index)

class IDE:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.interpreter = Interpreter(config)
        self.root.title("Custom Programming Language IDE")
        self.create_widgets()
        self.dark_mode = False

    def create_widgets(self):
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12, 'bold'))
        style.configure('TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TCanvas', background='#f0f0f0')

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.logo_frame = ttk.Frame(main_frame)
        self.logo_frame.grid(row=0, column=0, sticky="w", pady=30, padx=10)
        self.logo_image = Image.open("path_to_logo.png")  # Change the path to your logo image
        self.logo_image = self.logo_image.resize((100, 100), Image.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ttk.Label(self.logo_frame, image=self.logo_photo)
        self.logo_label.pack()

        self.editor_frame = ttk.Frame(main_frame)
        self.editor_frame.grid(row=1, column=0, sticky="nsew")

        self.linenumbers = TextLineNumbers(self.editor_frame, width=30, background='#f0f0f0')
        self.linenumbers.grid(row=0, column=0, sticky="ns")

        self.editor = CustomText(self.editor_frame, width=80, height=20, font=("Consolas", 12, "bold"))
        self.editor.grid(row=0, column=1, sticky="nsew")
        self.editor.attach(self.linenumbers)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(10, 0))

        self.run_button = ttk.Button(button_frame, text="Run", command=self.run_code)
        self.run_button.grid(row=0, column=0, padx=(0, 5))

        self.doc_button = ttk.Button(button_frame, text="Documentation", command=self.show_documentation)
        self.doc_button.grid(row=0, column=1, padx=(0, 5))

        self.dark_mode_button = ttk.Button(button_frame, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.grid(row=0, column=2)

        self.output_frame = ttk.Frame(main_frame)
        self.output_frame.grid(row=3, column=0, sticky="nsew")

        self.output = scrolledtext.ScrolledText(self.output_frame, width=80, height=10, state='disabled', font=("Consolas", 12, "bold"))
        self.output.grid(row=0, column=0, pady=(10, 0))

        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = '#2e2e2e' if self.dark_mode else '#f0f0f0'
        fg_color = '#ffffff' if self.dark_mode else '#000000'
        self.root.configure(background=bg_color)
        self.editor.configure(background=bg_color, foreground=fg_color, insertbackground=fg_color)
        self.linenumbers.configure(background=bg_color)
        self.output.configure(background=bg_color, foreground=fg_color)
        self.logo_frame.configure(background=bg_color)
        self.editor_frame.configure(background=bg_color)
        self.output_frame.configure(background=bg_color)

    def run_code(self):
        code = self.editor.get("1.0", tk.END)
        self.output.config(state='normal')
        self.output.delete("1.0", tk.END)
        self.editor.remove_tags()

        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        try:
            self.interpreter.interpret(code)
            output = mystdout.getvalue()
            self.output.insert(tk.END, output)
        except SyntaxError as e:
            line_num = self.extract_line_number(str(e))
            self.editor.highlight_error(line_num)
            self.output.insert(tk.END, f"Syntax Error: {e}\n")
        except Exception as e:
            self.output.insert(tk.END, f"Error: {e}\n")
        finally:
            sys.stdout = old_stdout

        self.output.config(state='disabled')

    def extract_line_number(self, error_message):
        match = re.search(r'line (\d+)', error_message)
        if match:
            return match.group(1)
        return '1'

    def show_documentation(self):
        doc_window = Toplevel(self.root)
        doc_window.title("Documentation")
        doc_text = scrolledtext.ScrolledText(doc_window, width=80, height=20, font=("Consolas", 12, "bold"))
        doc_text.pack(pady=10, padx=10)
        doc_text.insert(tk.END, self.get_documentation())
        doc_text.config(state='disabled')

    def get_documentation(self):
        return (
            "Custom Programming Language Documentation\n\n"
            "Variable Declarations:\n"
            f"  {self.config['declare'][0]} {self.config['int']} <variable_name> = <integer>.\n"
            f"  {self.config['declare'][0]} {self.config['string']} <variable_name> = <string>.\n\n"
            "Display Statements:\n"
            f"  {self.config['display'][0]} <expression>.\n\n"
            "For Loops:\n"
            f"  {self.config['for']} <variable> in range (<integer>):\n"
            f"    <statements>\n"
            f"  {self.config['endfor']}.\n"
        )















# CONFIF OF SYNTAXES


def main():
    config = {
        "declare": ["grah", "hero"],   # Change this keyword to anything you want for variable declaration
        "display": ["display-"], # Change this keyword to anything you want for display
        "int": "int",         # Change this keyword to anything you want for integer type
        "string": "string",    # Change this keyword to anything you want for string type
        "for": "for",          # Change this keyword to anything you want for 'for' loop
        "endfor": "endfor"     # Change this keyword to anything you want for ending the 'for' loop
    }

    root = tk.Tk()
    ide = IDE(root, config)
    root.mainloop()

if __name__ == "__main__":
    main()
