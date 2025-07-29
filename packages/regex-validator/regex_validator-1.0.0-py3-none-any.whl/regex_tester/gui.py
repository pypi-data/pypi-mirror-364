import tkinter as tk
import re

def run_gui():
    def test():
        pattern = entry_pattern.get()
        text = entry_text.get()
        try:
            result = re.findall(pattern, text)
            output.set(f"Matches: {result}")
        except re.error as e:
            output.set(f"Invalid regex: {e}")

    root = tk.Tk()
    root.title("Regex Tester")

    tk.Label(root, text="Pattern:").pack()
    entry_pattern = tk.Entry(root, width=50)
    entry_pattern.pack()

    tk.Label(root, text="Text:").pack()
    entry_text = tk.Entry(root, width=50)
    entry_text.pack()

    output = tk.StringVar()
    tk.Button(root, text="Test", command=test).pack()
    tk.Label(root, textvariable=output).pack()

    root.mainloop()

if __name__ == "__main__":
    run_gui()
