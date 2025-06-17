# FirstProject
this is my first project

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

#Features include:
- File opening for .txt, .html, .json, and other text-based files.
- English spell checking with suggestions and options to replace or ignore misspellings one by one. Misspelled words are highlighted.
- Space highlighting to make all space characters visible.
- Space deletion tools:
    - Delete all spaces in the document.
    - Delete spaces in selected lines.

#The application structure includes:
- `main.py`: Core application logic, UI setup using Tkinter.
- `utils/spell_checker.py`: Handles spell checking logic using the `pyspellchecker` library.
- `ui/spell_dialog.py`: Provides the dialog for interactive spell checking.
- `tests/`: Contains unit tests.
    - `test_spell_checker.py`: Unit tests for the spell checking utility. (Unit tests for UI components in `main.py` were not feasible due to `tkinter` limitations in the testing environment).

#The spell check functionality allows you to iterate through misspelled words, view suggestions, replace words, or ignore them for the current session. Space highlighting can be toggled, and space deletion provides fine-grained control over whitespace
