import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from utils.spell_checker import SpellCheckerUtil
from ui.spell_dialog import SpellCheckDialog # Import the new dialog

class TextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Text Editor")
        self.geometry("800x600")

        self.highlight_spaces_active = tk.BooleanVar(value=False) # Variable for checkbutton state

        self._create_menu()
        self._create_text_area()

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=self.cut_text)
        edit_menu.add_command(label="Copy", command=self.copy_text)
        edit_menu.add_command(label="Paste", command=self.paste_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="Spell Check", command=self.spell_check_text)
        edit_menu.add_checkbutton(label="Highlight Spaces", onvalue=True, offvalue=False, variable=self.highlight_spaces_active, command=self.toggle_highlight_spaces)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete All Spaces in Document", command=self.delete_all_spaces)
        edit_menu.add_command(label="Delete Spaces in Selected Lines", command=self.delete_spaces_in_selected_lines)

    def _create_text_area(self):
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        # Configure a tag for highlighting misspelled words
        self.text_area.tag_configure("misspelled", background="yellow", foreground="red")
        # Configure a tag for highlighting spaces
        self.text_area.tag_configure("space", background="lightgray")
        self.text_area.pack(expand=True, fill="both")

    def new_file(self):
        # Placeholder for new file functionality
        print("New file action")

    def open_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, content)
            self.title(f"Simple Text Editor - {filepath}")
        except Exception as e:
            # Handle potential errors like file not found or permission issues
            # For now, just print to console, but a dialog would be better
            print(f"Error opening file: {e}")
            # Optionally, show an error message in a dialog
            # messagebox.showerror("Error", f"Could not open file: {e}")


    def save_file(self):
        # Placeholder for save file functionality
        print("Save file action")

    def cut_text(self):
        # Placeholder for cut text functionality
        print("Cut text action")

    def copy_text(self):
        # Placeholder for copy text functionality
        print("Copy text action")

    def paste_text(self):
        # Placeholder for paste text functionality
        print("Paste text action")

    def spell_check_text(self):
        self.text_area.tag_remove("misspelled", "1.0", tk.END) # Clear previous general highlights

        if self.highlight_spaces_active.get():
            self._apply_space_highlighting()

        content = self.text_area.get("1.0", tk.END)
        if not hasattr(self, 'spell_checker_util'):
            self.spell_checker_util = SpellCheckerUtil()

        # misspelled_info is a list of dicts: [{"word": word, "suggestions": [...]}, ...]
        # These are unique misspelled words. We need to find all occurrences of them.
        unique_misspelled_details = self.spell_checker_util.find_misspelled(content)

        if not unique_misspelled_details:
            messagebox.showinfo("Spell Check", "No misspelled words found.", parent=self)
            return

        self.text_area.config(state=tk.DISABLED) # Disable text area during interactive spell check

        # Store all instances of misspelled words: (word, start_pos, end_pos, suggestions)
        self.current_misspellings_list = []

        # First, find and tag all instances without immediate interaction
        for item in unique_misspelled_details:
            misspelled_word = item["word"]
            suggestions = item["suggestions"]
            start_index = "1.0"
            while True:
                pos = self.text_area.search(misspelled_word, start_index, stopindex=tk.END, nocase=False, regexp=False, count=tk.IntVar())
                if not pos:
                    break

                line, char = map(int, pos.split('.'))
                end_pos = f"{line}.{char + len(misspelled_word)}"

                # Basic whole word check (can be improved)
                is_whole_word = True
                if char > 0 and self.text_area.get(f"{line}.{char-1}", pos).isalnum():
                    is_whole_word = False
                text_end_index = self.text_area.index(tk.END + "-1c")
                if self.text_area.compare(end_pos, "<", text_end_index) and self.text_area.get(end_pos, f"{end_pos}+1c").isalnum():
                    is_whole_word = False

                if is_whole_word:
                    self.text_area.tag_add("misspelled", pos, end_pos)
                    # Store instance for interactive correction
                    self.current_misspellings_list.append({
                        "word": misspelled_word,
                        "start": pos,
                        "end": end_pos,
                        "suggestions": suggestions
                    })
                start_index = end_pos

        if not self.current_misspellings_list:
            messagebox.showinfo("Spell Check", "No instances of misspelled words found (after whole word check).", parent=self)
            self.text_area.config(state=tk.NORMAL)
            return

        # Sort by position in text
        self.current_misspellings_list.sort(key=lambda x: list(map(int, x["start"].split('.'))))

        self.current_misspelling_index = 0
        self._process_next_misspelling()

    def _process_next_misspelling(self):
        if self.current_misspelling_index >= len(self.current_misspellings_list):
            messagebox.showinfo("Spell Check", "Spell check complete.", parent=self)
            self.text_area.config(state=tk.NORMAL)
            self.text_area.tag_remove("current_misspelling", "1.0", tk.END) # Remove current highlight
            # Optionally re-highlight all remaining general "misspelled" tags if any were ignored.
            return

        item = self.current_misspellings_list[self.current_misspelling_index]
        misspelled_word = item["word"]
        start_pos = item["start"]
        end_pos = item["end"]
        suggestions = item["suggestions"]

        # Ensure the word at start_pos, end_pos is still the one we expect
        current_word_in_text = self.text_area.get(start_pos, end_pos)
        if current_word_in_text != misspelled_word:
            # Text was changed by a previous correction, skip this one or re-evaluate
            self.current_misspelling_index += 1
            self._process_next_misspelling()
            return

        self.text_area.tag_remove("current_misspelling", "1.0", tk.END) # Clear previous "current" highlight
        self.text_area.tag_add("current_misspelling", start_pos, end_pos)
        self.text_area.tag_config("current_misspelling", background="orange", foreground="black")
        self.text_area.see(start_pos) # Scroll to the word

        dialog = SpellCheckDialog(self, misspelled_word, suggestions)
        # Dialog result: (action, word, [replacement_word]) or (action, word) or (action, None)

        self.text_area.tag_remove("current_misspelling", start_pos, end_pos) # Remove specific highlight

        if dialog.result:
            action, word, *opt_replacement = dialog.result
            replacement = opt_replacement[0] if opt_replacement else None

            if action == "replace":
                # Important: check if the word at start_pos, end_pos is still the original misspelled_word
                # This is to handle cases where prior replacements might have shifted indices or changed the word.
                # A more robust way is to adjust indices, but for now, re-check:
                actual_word_at_location = self.text_area.get(start_pos, end_pos)
                if actual_word_at_location == word: # word is misspelled_word from dialog
                    self.text_area.config(state=tk.NORMAL) # Enable for modification
                    self.text_area.delete(start_pos, end_pos)
                    self.text_area.insert(start_pos, replacement)
                    self.text_area.config(state=tk.DISABLED) # Disable again

                    # Remove the general "misspelled" tag for this corrected instance
                    self.text_area.tag_remove("misspelled", start_pos, f"{start_pos}+{len(replacement)}c")

                    # Adjust indices of subsequent misspellings
                    # This is a complex part. For now, we might invalidate subsequent items or try a simple adjustment.
                    # Simple adjustment:
                    diff = len(replacement) - len(word)
                    if diff != 0:
                        for i in range(self.current_misspelling_index + 1, len(self.current_misspellings_list)):
                            m_item = self.current_misspellings_list[i]
                            # Naive check if on same line and after corrected word
                            m_start_line, m_start_char = map(int, m_item["start"].split('.'))
                            s_line, s_char = map(int, start_pos.split('.'))
                            if m_start_line == s_line and m_start_char > s_char :
                                m_item["start"] = f"{m_start_line}.{m_start_char + diff}"
                                m_item["end"] = f"{m_start_line}.{map(int, m_item['end'].split('.'))[1] + diff}"
                        # Re-sort might be needed if changes are complex
                        # self.current_misspellings_list.sort(key=lambda x: list(map(int, x["start"].split('.'))))


                else:
                    print(f"Word at {start_pos} changed from '{word}' to '{actual_word_at_location}', skipping replacement.")
                self.current_misspelling_index += 1
                self._process_next_misspelling()

            elif action == "ignore_once":
                self.text_area.tag_remove("misspelled", start_pos, end_pos) # Remove highlight for this instance
                self.current_misspelling_index += 1
                self._process_next_misspelling()

            # elif action == "ignore_all":
            #     # Add to a session ignore list, remove all highlights for this word
            #     # self.session_ignored_words.add(word)
            #     # self.text_area.tag_remove("misspelled", "1.0", tk.END, word) # This needs custom logic to find all 'word'
            #     self.current_misspelling_index += 1
            #     self._process_next_misspelling()

            # elif action == "add_to_dictionary":
            #     # self.spell_checker_util.spell.add(word)
            #     # self.text_area.tag_remove("misspelled", "1.0", tk.END, word) # custom logic
            #     self.current_misspelling_index += 1
            #     self._process_next_misspelling()

            elif action == "cancel":
                self.text_area.config(state=tk.NORMAL)
                messagebox.showinfo("Spell Check", "Spell check cancelled.", parent=self)
        else: # Dialog closed without action (e.g. WM_DELETE_WINDOW)
            self.text_area.config(state=tk.NORMAL)
            messagebox.showinfo("Spell Check", "Spell check cancelled.", parent=self)

    def toggle_highlight_spaces(self):
        if self.highlight_spaces_active.get():
            self._apply_space_highlighting()
        else:
            self.text_area.tag_remove("space", "1.0", tk.END)
            # If spell check highlighting was active, it might be good to re-apply it here.
            # For now, this just removes space highlights.
            # Users might need to re-run spell check if they want its highlights back immediately.

    def _apply_space_highlighting(self):
        # It's important to remove old "space" tags first,
        # otherwise, if text is deleted, old highlights might remain.
        self.text_area.tag_remove("space", "1.0", tk.END)

        content = self.text_area.get("1.0", tk.END)
        start_index = "1.0"
        space_char = " " # The character to highlight

        while True:
            pos = self.text_area.search(space_char, start_index, stopindex=tk.END)
            if not pos:
                break

            # Define the end position for the tag (start + 1 character for a single space)
            line, char = map(int, pos.split('.'))
            end_pos = f"{line}.{char + 1}"

            self.text_area.tag_add("space", pos, end_pos)
            start_index = end_pos # Move to the end of the found space for the next search

        # After applying space highlights, ensure that misspelled word highlights are still visible
        # if spell check is active. This can be tricky due to tag overlaps.
        # One approach is to re-apply the "misspelled" tag to words that are already known to be misspelled.
        # Or, ensure "misspelled" tag has higher priority if Tkinter supports it directly (it doesn't simply).
        # For now, the current spell_check_text method already handles re-applying space highlights
        # if space highlighting is active when spell_check_text is called.
        # And toggle_highlight_spaces just focuses on space tags.

    def delete_all_spaces(self):
        current_content = self.text_area.get("1.0", tk.END)
        modified_content = current_content.replace(" ", "")
        if current_content != modified_content:
            # Preserve cursor position if possible (tricky after global replace)
            # For now, just replace all and let cursor go to end.
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", modified_content)
            # Clear existing highlights as they are now invalid
            self.text_area.tag_remove("misspelled", "1.0", tk.END)
            if not self.highlight_spaces_active.get(): # If space highlighting was off, ensure all space tags are gone
                self.text_area.tag_remove("space", "1.0", tk.END)
            elif self.highlight_spaces_active.get(): # If it was on, it's now off effectively as there are no spaces
                 # Or, one could argue to re-apply if there were non-space chars that had space tags (which shouldn't happen)
                 pass # No spaces left to highlight

            print("Deleted all spaces in the document.")
        else:
            print("No spaces found to delete in the document.")


    def delete_spaces_in_selected_lines(self):
        try:
            start_sel = self.text_area.index(tk.SEL_FIRST)
            end_sel = self.text_area.index(tk.SEL_LAST)

            # Get the line numbers for the selection
            start_line = int(start_sel.split('.')[0])
            end_line = int(end_sel.split('.')[0])

            # If the selection ends exactly at the beginning of a line (e.g., user selected full lines),
            # we want to include that last line. However, if it's mid-line, we only go up to that line.
            # The `text_area.get` for lines is exclusive for the end line index if column is 0.
            # So, we get text up to the line *after* end_line's line number, column 0.

            # Define the actual range to get and replace: entire lines from start_line to end_line
            start_of_selection_block = f"{start_line}.0"
            # For `get`, the end index is exclusive. For `delete`, it's inclusive for text widget.
            # We want to get text including the entire end_line.
            end_of_selection_block_for_get = f"{end_line + 1}.0"

            selected_lines_content = self.text_area.get(start_of_selection_block, end_of_selection_block_for_get)

            if not selected_lines_content.strip(): # Nothing to do if only whitespace or empty
                print("No content in selected lines to delete spaces from.")
                return

            modified_lines_content = selected_lines_content.replace(" ", "")

            if selected_lines_content != modified_lines_content:
                # Replace the original selected lines with the modified content
                # The end_sel for delete should be the actual end of content for these lines
                self.text_area.delete(start_of_selection_block, end_of_selection_block_for_get)
                self.text_area.insert(start_of_selection_block, modified_lines_content)

                # Clear highlights in the modified range.
                # This is a simplification. A more advanced approach might try to re-apply them.
                self.text_area.tag_remove("misspelled", start_of_selection_block, f"{start_line + (modified_lines_content.count(chr(10)))}.0")
                if not self.highlight_spaces_active.get():
                    self.text_area.tag_remove("space", start_of_selection_block, f"{start_line + (modified_lines_content.count(chr(10)))}.0")

                print(f"Deleted spaces in lines {start_line} to {end_line}.")
            else:
                print(f"No spaces found to delete in lines {start_line} to {end_line}.")

        except tk.TclError:
            print("No text selected, or selection is invalid for deleting spaces in lines.")
            # This occurs if SEL_FIRST or SEL_LAST don't exist (no selection)


if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()
