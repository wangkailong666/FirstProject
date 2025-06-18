import tkinter as tk
from tkinter import simpledialog, ttk

class AdvancedSpaceDeleteDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Line Numbers/Ranges (e.g., 1-5, 7, 9-10, all):").grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        self.line_input_entry = tk.Entry(master, width=40)
        self.line_input_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")

        # Deletion Type Radiobuttons
        self.delete_type_var = tk.StringVar(value="all_on_lines")

        tk.Label(master, text="Deletion Type:").grid(row=2, column=0, columnspan=2, sticky="w", pady=(10,2))

        rb_all_on_lines = ttk.Radiobutton(master, text="Delete all spaces on specified lines",
                                          variable=self.delete_type_var, value="all_on_lines",
                                          command=self._toggle_char_input_state)
        rb_all_on_lines.grid(row=3, column=0, columnspan=2, sticky="w", padx=5)

        rb_before_char = ttk.Radiobutton(master, text="Delete spaces before specific character(s) on specified lines",
                                         variable=self.delete_type_var, value="before_char",
                                         command=self._toggle_char_input_state)
        rb_before_char.grid(row=4, column=0, columnspan=2, sticky="w", padx=5)

        # Specific Character Input
        self.char_input_label = tk.Label(master, text="Specific Character(s) (for 'before' option):")
        self.char_input_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10,2))
        self.char_input_entry = tk.Entry(master, width=20)
        self.char_input_entry.grid(row=6, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        self._toggle_char_input_state() # Initial state update

        return self.line_input_entry # Initial focus

    def _toggle_char_input_state(self):
        if self.delete_type_var.get() == "before_char":
            self.char_input_entry.config(state=tk.NORMAL)
            self.char_input_label.config(state=tk.NORMAL)
        else:
            self.char_input_entry.config(state=tk.DISABLED)
            self.char_input_label.config(state=tk.DISABLED)

    def apply(self):
        line_input = self.line_input_entry.get().strip()
        delete_type = self.delete_type_var.get()
        char_input = self.char_input_entry.get() # No strip, as spaces might be significant if user enters them

        if not line_input:
            # tk.messagebox.showwarning("Input Error", "Line numbers/ranges cannot be empty.", parent=self)
            # simpledialog.Dialog doesn't have messagebox easily available before it's destroyed.
            # Parent window can show it after dialog closes if self.result is None due to this.
            self.result = None
            return

        if delete_type == "before_char" and not char_input:
            # tk.messagebox.showwarning("Input Error", "Specific character(s) must be provided for 'before char' option.", parent=self)
            self.result = None
            return

        self.result = (line_input, delete_type, char_input)

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Hide main window

    def test_dialog():
        dialog = AdvancedSpaceDeleteDialog(root, title="Test Advanced Deletion")
        print(f"Dialog result: {dialog.result}")
        root.destroy()

    root.after(100, test_dialog)
    root.mainloop()
