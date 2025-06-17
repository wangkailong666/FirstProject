# FirstProject
this is my first project

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Building the Executable

To create a standalone executable from the source code, you can use PyInstaller.

### Prerequisites

1.  **Python:** Ensure you have Python installed (version 3.6 or newer recommended). You can download it from [python.org](https://www.python.org/downloads/).
2.  **PyInstaller:** Install PyInstaller using pip:
    ```bash
    pip install pyinstaller
    ```
3.  **(Optional) UPX:** The provided `main.spec` file is configured to use UPX to compress the executable, making it smaller. If you want to use this feature, you need to install UPX and ensure it's in your system's PATH. You can find UPX at [https://upx.github.io/](https://upx.github.io/). If you don't have UPX or don't want to use it, you can edit `main.spec` and change `upx=True` to `upx=False` in both the `exe` and `coll` sections.

### Build Steps

1.  **Navigate to the project directory:**
    Open your terminal or command prompt and change to the root directory of this project (where `main.spec` is located).

2.  **Run PyInstaller:**
    Execute the following command to build the executable using the spec file:
    ```bash
    pyinstaller main.spec
    ```

3.  **Find the executable:**
    After the build process completes, PyInstaller will create a directory named `dist/`. Inside `dist/`, you will find a folder named `TextEditorApp` (this name is based on the `name` parameter in your `main.spec` file).

    Navigate into this `dist/TextEditorApp` folder. The main executable (`TextEditorApp.exe` on Windows, or `TextEditorApp` on macOS/Linux) will be located here, along with other necessary files and DLLs.

   **Note on Output:** These instructions and the default `main.spec` configuration produce a one-folder bundle (the application along with its dependencies in a directory). This is generally more reliable for compatibility than single-file executables, especially when troubleshooting.
