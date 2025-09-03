# GUI Data Merger

This application provides a graphical user interface (GUI) to merge multiple data sheets into a single CSV file. It supports both CSV and XML file formats for the input files.

## Features

- **Graphical User Interface:** Easy to use interface for selecting and managing files.
- **Multi-File Support:** Merge two or more files at once.
- **Mixed Format Support:** Combine CSV and XML files in the same merge operation.
- **Column Normalization:** Automatically combines columns from all files. If a row from one file doesn't have a column that exists in another, it will be given a blank value for that column in the output.

## How to Use

1.  **Run the application:**
    -   You can run the script directly using Python: `python merger.py`
    -   Alternatively, you can build an executable.
2.  **Add Files:** Click the "Add File(s)" button to open a file browser. You can select multiple CSV or XML files.
3.  **Manage Files:** The selected files will appear in the list. To remove a file, select it in the list and click "Remove Selected". You can select multiple files to remove by holding `Ctrl` or `Shift`.
4.  **Merge:** Once you have at least two files in the list, click the "Merge Files" button.
5.  **Save:** A "save as" dialog will appear. Choose a name and location for your merged CSV file and click "Save".
6.  A confirmation message will appear when the merge is complete.

## How to Build an Executable

This script can be packaged into a standalone executable (`.exe` on Windows) so you can run it without needing to have Python installed.

### Prerequisites

You need `pyinstaller`. You can install it using pip:
```bash
pip install -r requirements.txt
```

### Build Command

To build the executable, run the following command in your terminal from the project directory:

```bash
pyinstaller --onefile --windowed --name "FileMerger" merger.py
```

- `--onefile`: Packages everything into a single executable file.
- `--windowed`: Prevents the command prompt from appearing when you run the application.
- `--name "FileMerger"`: Sets the name of the output executable.

After the command finishes, you will find the executable file inside a new `dist` folder. You can move this file anywhere on your computer and run it.
