import tkinter as tk
from tkinter import simpledialog, colorchooser # Using simpledialog.Dialog as a base

class ColorChooserDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, initialvalue=None):
        self.initialvalue = initialvalue
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Enter color (name or HEX #RRGGBB):").grid(row=0, sticky="w")
        self.entry = tk.Entry(master, width=30)
        self.entry.grid(row=1, padx=5, pady=5, sticky="ew")
        if self.initialvalue:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, tk.END)

        # Optional: Add a button to open the system's color chooser
        self.choose_button = tk.Button(master, text="Choose from Palette...", command=self._open_system_color_chooser)
        self.choose_button.grid(row=2, pady=5)

        return self.entry # Initial focus

    def _open_system_color_chooser(self):
        # colorchooser.askcolor returns a tuple: ((r,g,b), hex_color_string) or (None, None)
        color_info = colorchooser.askcolor(parent=self, initialcolor=self.entry.get())
        if color_info and color_info[1]: # If a color was chosen and hex string is available
            self.entry.delete(0, tk.END)
            self.entry.insert(0, color_info[1]) # Insert the hex string

    def apply(self):
        result = self.entry.get()
        if result: # Basic validation: not empty
            self.result = result
        else:
            # Or handle error, for now, None result means invalid/cancelled
            self.result = None # Or perhaps keep initialvalue if empty? For now, None.

# Example Usage (for testing the dialog independently)
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Hide main window for dialog test

    def test_dialog():
        # Test with an initial value
        dialog = ColorChooserDialog(root, title="Choose a Color", initialvalue="lightgray")
        print(f"Dialog result (with initial): {dialog.result}")

        # Test without an initial value
        dialog2 = ColorChooserDialog(root, title="Choose Another Color")
        print(f"Dialog result (no initial): {dialog2.result}")

        root.destroy()

    # Schedule the test dialog to run after mainloop starts for the hidden root
    root.after(100, test_dialog)
    root.mainloop()
