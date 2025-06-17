import tkinter as tk
from tkinter import ttk, messagebox

class SpellCheckDialog(tk.Toplevel):
    def __init__(self, parent, misspelled_word, suggestions):
        super().__init__(parent)
        self.transient(parent) # Make it modal over the parent
        self.grab_set() # Capture all events
        self.title("Spell Check")
        
        self.misspelled_word = misspelled_word
        self.suggestions = suggestions
        self.result = None # To store the action chosen by the user
        self.selected_suggestion = tk.StringVar()

        tk.Label(self, text=f"Misspelled Word:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(self, text=misspelled_word, font=("Arial", 10, "bold"), foreground="red").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self, text="Suggestions:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        
        if self.suggestions:
            self.suggestions_listbox = tk.Listbox(self, selectmode=tk.SINGLE, exportselection=False, height=5)
            for sugg in self.suggestions:
                self.suggestions_listbox.insert(tk.END, sugg)
            self.suggestions_listbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            if self.suggestions:
                 self.suggestions_listbox.select_set(0) # Select the first suggestion by default
                 self.selected_suggestion.set(self.suggestions_listbox.get(0))
            self.suggestions_listbox.bind('<<ListboxSelect>>', self.on_suggestion_select)
        else:
            tk.Label(self, text="No suggestions found.").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Replace", command=self.on_replace).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Ignore Once", command=self.on_ignore_once).pack(side=tk.LEFT, padx=5)
        #ttk.Button(button_frame, text="Ignore All (Word)", command=self.on_ignore_all).pack(side=tk.LEFT, padx=5)
        #ttk.Button(button_frame, text="Add to Dictionary", command=self.on_add_to_dictionary).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel) # Handle window close button
        
        # Center the dialog on the parent window
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        center_x = parent_x + (parent_width - dialog_width) // 2
        center_y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"+{center_x}+{center_y}")

        self.wait_window(self) # Crucial for modal behavior

    def on_suggestion_select(self, event=None):
        if not self.suggestions_listbox.curselection():
            return
        idx = self.suggestions_listbox.curselection()[0]
        self.selected_suggestion.set(self.suggestions_listbox.get(idx))

    def on_replace(self):
        if not self.suggestions:
            messagebox.showwarning("No Suggestion", "No suggestions available to replace with.", parent=self)
            return
        if not self.selected_suggestion.get():
            messagebox.showwarning("No Selection", "Please select a suggestion to replace with.", parent=self)
            return
        self.result = ("replace", self.misspelled_word, self.selected_suggestion.get())
        self.destroy()

    def on_ignore_once(self):
        self.result = ("ignore_once", self.misspelled_word)
        self.destroy()

    # def on_ignore_all(self):
    #     self.result = ("ignore_all", self.misspelled_word)
    #     self.destroy()

    # def on_add_to_dictionary(self):
    #     self.result = ("add_to_dictionary", self.misspelled_word)
    #     self.destroy()

    def on_cancel(self):
        self.result = ("cancel", None)
        self.destroy()

if __name__ == '__main__':
    # Example usage (for testing the dialog independently)
    root = tk.Tk()
    root.title("Main Application Window")
    root.geometry("600x400")

    def open_spell_dialog():
        # Test data
        word = "mispeled"
        suggestions = ["misspelled", "misspell", "misapplied"]
        
        dialog = SpellCheckDialog(root, word, suggestions)
        print(f"Dialog result: {dialog.result}")

    ttk.Button(root, text="Open Spell Check Dialog", command=open_spell_dialog).pack(pady=20)
    root.mainloop()
