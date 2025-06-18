import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from utils.spell_checker import SpellCheckerUtil
from utils.text_analysis import find_space_around_period_anomalies, parse_line_ranges
from ui.spell_dialog import SpellCheckDialog
from ui.color_chooser_dialog import ColorChooserDialog
from ui.advanced_space_delete_dialog import AdvancedSpaceDeleteDialog # Import new dialog

class TextEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Text Editor")
        self.geometry("800x600")

        self.highlight_spaces_active = tk.BooleanVar(value=False)
        self.period_spacing_highlight_active = tk.BooleanVar(value=False)
        self.space_highlight_color = tk.StringVar(value="lightgray") # Default color

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
        # Space Highlighting Submenu
        space_highlight_menu = tk.Menu(edit_menu, tearoff=0)
        space_highlight_menu.add_checkbutton(
            label="Enable/Disable",
            variable=self.highlight_spaces_active,
            command=self.apply_or_clear_space_highlighting # Renamed/refactored method
        )
        space_highlight_menu.add_command(label="Set Highlight Color...", command=self.set_space_highlight_color)
        edit_menu.add_cascade(label="Space Highlighting", menu=space_highlight_menu)

        edit_menu.add_separator()
        edit_menu.add_command(label="Delete All Spaces in Document", command=self.delete_all_spaces)
        edit_menu.add_command(label="Delete Spaces in Selected Lines", command=self.delete_spaces_in_selected_lines)
        edit_menu.add_separator()
        edit_menu.add_checkbutton(
            label="Highlight Period Spacing",
            onvalue=True, offvalue=False,
            variable=self.period_spacing_highlight_active,
            command=self.apply_or_clear_period_spacing_highlight
        )
        edit_menu.add_separator()
        edit_menu.add_command(label="Advanced Space Deletion...", command=self.show_advanced_space_delete_dialog)


    def _create_text_area(self):
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        # Configure a tag for highlighting misspelled words
        self.text_area.tag_configure("misspelled", background="yellow", foreground="red")
        # Configure a tag for highlighting spaces - initial configuration
        self.text_area.tag_configure("space", background=self.space_highlight_color.get())
        # Configure a tag for format anomalies (e.g., space around period)
        self.text_area.tag_configure("format_anomaly", foreground="blue", underline=True)
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

    def apply_or_clear_space_highlighting(self): # Renamed from toggle_highlight_spaces
        if self.highlight_spaces_active.get():
            self._apply_space_highlighting_logic()
        else:
            self._remove_space_highlighting_logic()

    def _apply_space_highlighting_logic(self):
        # This method assumes the "space" tag is already configured with the desired color.
        # It just adds the tag to the characters.
        # It's important to remove old "space" tags first if applying to entire document,
        # or if text could have changed.
        self._remove_space_highlighting_logic() # Clear before applying to prevent duplicates on re-call

        content = self.text_area.get("1.0", tk.END)
        start_index = "1.0"
        space_char = " "

        while True:
            pos = self.text_area.search(space_char, start_index, stopindex=tk.END)
            if not pos:
                break
            line, char = map(int, pos.split('.'))
            end_pos = f"{line}.{char + 1}"
            self.text_area.tag_add("space", pos, end_pos)
            start_index = end_pos

        # Interaction with other highlights (e.g., spell_check_text re-applying space highlights)
        # needs to be considered if this logic is called from multiple places.
        # For now, spell_check_text calls its own _apply_space_highlighting if active.
        # This might need to be harmonized to _apply_space_highlighting_logic.
        # Let's rename the old _apply_space_highlighting in spell_check_text context
        # to avoid confusion or make it call this one.
        # For now, this method is self-contained for space highlighting feature.

    def _remove_space_highlighting_logic(self):
        self.text_area.tag_remove("space", "1.0", tk.END)

    def set_space_highlight_color(self):
        dialog = ColorChooserDialog(self, title="Set Space Highlight Color", initialvalue=self.space_highlight_color.get())
        if dialog.result:
            # Basic validation: ensure the color string is not empty.
            # More advanced validation could try to use it and catch TclError.
            if dialog.result.strip():
                self.space_highlight_color.set(dialog.result.strip())
                # Re-configure the tag with the new color
                try:
                    self.text_area.tag_configure("space", background=self.space_highlight_color.get())
                    # If highlighting is active, re-apply to show the new color
                    if self.highlight_spaces_active.get():
                        self._apply_space_highlighting_logic()
                except tk.TclError as e:
                    messagebox.showerror("Invalid Color", f"The color '{self.space_highlight_color.get()}' is not valid: {e}", parent=self)
                    # Optionally revert to a default or previous valid color
                    # self.space_highlight_color.set("lightgray") # Revert to default
                    # self.text_area.tag_configure("space", background=self.space_highlight_color.get())
            else:
                messagebox.showwarning("Invalid Color", "Color cannot be empty.", parent=self)


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

    def apply_or_clear_period_spacing_highlight(self):
        self.text_area.tag_remove("format_anomaly", "1.0", tk.END)

        if not self.period_spacing_highlight_active.get():
            return

        current_text = self.text_area.get("1.0", tk.END)
        # Guard against processing if text area is effectively empty (contains only newline)
        if current_text.strip() == "":
            return

        anomalies = find_space_around_period_anomalies(current_text)

        for start_char_idx, end_char_idx in anomalies:
            try:
                # Convert character offsets to Tkinter text indices
                # The Text widget's "1.0 + N chars" index is robust for this.
                tk_start_idx = self.text_area.index(f"1.0 + {start_char_idx} chars")
                tk_end_idx = self.text_area.index(f"1.0 + {end_char_idx} chars")

                # Ensure start is before end, and both are valid within the text content
                if self.text_area.compare(tk_start_idx, "<", tk_end_idx) and \
                   self.text_area.compare(tk_start_idx, ">=", "1.0") and \
                   self.text_area.compare(tk_end_idx, "<=", tk.END + "-1c"): # tk.END includes a newline
                    self.text_area.tag_add("format_anomaly", tk_start_idx, tk_end_idx)
                else:
                    # This might happen if text is modified while highlighting, or issues with index conversion
                    # on complex text structures (though less likely with char offset method).
                    print(f"Skipping anomaly (invalid range): {start_char_idx}-{end_char_idx} -> {tk_start_idx}-{tk_end_idx}")
            except tk.TclError as e:
                # This can happen if indices are out of bounds, e.g. "1.0 + 10000 chars" in a short text
                print(f"Error applying tag for anomaly at char offsets {start_char_idx}-{end_char_idx}: {e}")

    def show_advanced_space_delete_dialog(self):
        dialog = AdvancedSpaceDeleteDialog(self, title="Advanced Space Deletion")
        if dialog.result:
            line_input_str, delete_type, specific_chars = dialog.result
            if line_input_str is None: # User cancelled or input was invalid in dialog
                # Dialog's apply method now sets result to None for empty line_input or char_input
                # We can provide more specific feedback here based on what was None if desired
                # For now, just a general message or do nothing.
                # messagebox.showwarning("Input Error", "Invalid input provided in the dialog.", parent=self)
                return
            self.process_advanced_space_deletion(line_input_str, delete_type, specific_chars)

    def process_advanced_space_deletion(self, line_input_str, delete_type, specific_chars):
        try:
            # Get total lines. Note: .index(tk.END) returns line AFTER the last line of text,
            # so if there's text "Line1\nLine2", END is "3.0".
            # If text area is empty, END is "1.0". If "Line1", END is "2.0".
            # total_lines should be the actual number of lines with content.
            content = self.text_area.get("1.0", tk.END + "-1c") # -1c to exclude final automatic newline
            if not content:
                total_lines_count = 0
            else:
                total_lines_count = len(content.splitlines())
                if content.endswith('\n'): # If the content ends with a newline, splitlines might give one less than expected by 1-indexed user.
                                         # However, total_lines_count from splitlines is accurate for 0-indexed processing.
                    pass # total_lines_count is correct here for 0-indexed.

            if total_lines_count == 0 and line_input_str.lower() != "all":
                 if any(char.isdigit() for char in line_input_str): # If user typed line numbers for empty doc
                    messagebox.showerror("Error", "Document is empty. No lines to process.", parent=self)
                    return

            target_lines_0_indexed = parse_line_ranges(line_input_str, total_lines_count)

        except ValueError as e:
            messagebox.showerror("Line Input Error", str(e), parent=self)
            return

        if not target_lines_0_indexed and total_lines_count > 0 : # Valid parse but resulted in no lines (e.g. "all" for empty doc was handled by parse_line_ranges)
            messagebox.showinfo("Info", "No lines selected for processing based on input.", parent=self)
            return
        if not target_lines_0_indexed and total_lines_count == 0: # e.g. "all" for empty doc
            messagebox.showinfo("Info", "Document is empty, no lines to process.", parent=self)
            return


        if delete_type == "all_on_lines":
            # Iterate in reverse to avoid index shifting issues when deleting/inserting line by line
            for line_idx in sorted(target_lines_0_indexed, reverse=True):
                tk_line_start = f"{line_idx + 1}.0"
                tk_line_end = f"{line_idx + 1}.end" # .end includes the newline char if present

                line_text = self.text_area.get(tk_line_start, tk_line_end)

                # Preserve newline if it exists, remove spaces from the rest
                ends_with_newline = line_text.endswith('\n')
                text_to_modify = line_text.rstrip('\n') if ends_with_newline else line_text

                modified_text_part = text_to_modify.replace(" ", "")

                # Re-append newline if it was there
                modified_line_text = modified_text_part + ('\n' if ends_with_newline else '')

                if modified_line_text != line_text:
                    self.text_area.delete(tk_line_start, tk_line_end)
                    self.text_area.insert(tk_line_start, modified_line_text)

            messagebox.showinfo("Success", "Deleted all spaces on specified lines.", parent=self)

        elif delete_type == "before_char":
            messagebox.showinfo("Not Implemented", "Deletion of spaces before specific character(s) is not yet implemented.", parent=self)

        # Consider re-applying highlights if active
        if self.highlight_spaces_active.get():
            self._apply_space_highlighting_logic()
        if self.period_spacing_highlight_active.get():
            self.apply_or_clear_period_spacing_highlight() # This one clears then applies


if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()
