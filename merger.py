import csv
import xml.etree.ElementTree as ET

# This script will merge two data sheets into one.
# It will support both CSV and XML file formats.

def read_csv(file_path):
    """Reads a CSV file and returns a list of dictionaries."""
    data = []
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

def read_xml(file_path):
    """Reads an XML file and returns a list of dictionaries."""
    data = []
    tree = ET.parse(file_path)
    root = tree.getroot()
    for item in root:
        row = {}
        for child in item:
            row[child.tag] = child.text
        data.append(row)
    return data

import argparse
import os

def merge_data(data1, data2):
    """Merges two lists of dictionaries."""
    return data1 + data2

def write_csv(data, file_path):
    """Writes a list of dictionaries to a CSV file."""
    if not data:
        return
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(description='Merge two data sheets into one.')
    parser.add_argument('file1', help='Path to the first input file (CSV or XML)')
    parser.add_argument('file2', help='Path to the second input file (CSV or XML)')
    parser.add_argument('output', help='Path to the output CSV file')
    args = parser.parse_args()

    # Read the first file
    file1_ext = os.path.splitext(args.file1)[1].lower()
    if file1_ext == '.csv':
        data1 = read_csv(args.file1)
    elif file1_ext == '.xml':
        data1 = read_xml(args.file1)
    else:
        print(f"Unsupported file format for {args.file1}")
        return

    # Read the second file
    file2_ext = os.path.splitext(args.file2)[1].lower()
    if file2_ext == '.csv':
        data2 = read_csv(args.file2)
    elif file2_ext == '.xml':
        data2 = read_xml(args.file2)
    else:
        print(f"Unsupported file format for {args.file2}")
        return

    # Merge the data
    merged_data = merge_data(data1, data2)

    # Write the output file
    write_csv(merged_data, args.output)
    print(f"Successfully merged {args.file1} and {args.file2} into {args.output}")

if __name__ == '__main__':
    main()
