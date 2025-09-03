# Data Merger

This script merges two data sheets into one. It supports both CSV and XML file formats for the input files and outputs a single CSV file.

## Requirements

The script uses only standard Python libraries, so no external packages are required.

## Usage

To use the script, run `merger.py` from the command line, providing the paths to the two input files and the desired output file.

```bash
python merger.py <file1> <file2> <output.csv>
```

- `<file1>`: Path to the first input file (can be `.csv` or `.xml`).
- `<file2>`: Path to the second input file (can be `.csv` or `.xml`).
- `<output.csv>`: Path to the merged output file (will be in CSV format).

### Examples

**Merging two CSV files:**
```bash
python merger.py data1.csv data2.csv merged_csv.csv
```

**Merging a CSV and an XML file:**
```bash
python merger.py data1.csv data2.xml merged_mixed.csv
```

**Merging two XML files:**
```bash
python merger.py data1.xml data2.xml merged_xml.csv
```
