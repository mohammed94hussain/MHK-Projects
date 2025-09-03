import csv
import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar

# --- Data Reading Functions ---

def read_csv(file_path):
    """Reads a CSV file and returns a list of dictionaries."""
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file {os.path.basename(file_path)}:\n{e}")
    return data

def read_xml(file_path):
    """Reads an XML file and returns a list of dictionaries."""
    data = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        for item in root:
            row = {}
            for child in item:
                row[child.tag] = child.text
            data.append(row)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read XML file {os.path.basename(file_path)}:\n{e}")
    return data

# --- GUI Application ---

class MergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Merger")
        self.root.geometry("500x400")

        self.file_list = []

        # --- Widgets ---
        # Frame for the listbox and scrollbar
        list_frame = tk.Frame(root)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.listbox = Listbox(list_frame, selectmode="extended")
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Frame for the buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5, padx=10, fill="x")

        add_button = tk.Button(button_frame, text="Add File(s)", command=self.add_files)
        add_button.pack(side="left", expand=True, fill="x", padx=5)

        remove_button = tk.Button(button_frame, text="Remove Selected", command=self.remove_selected)
        remove_button.pack(side="left", expand=True, fill="x", padx=5)

        merge_button = tk.Button(button_frame, text="Merge Files", command=self.merge_files)
        merge_button.pack(side="right", expand=True, fill="x", padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select files to merge",
            filetypes=(("CSV files", "*.csv"), ("XML files", "*.xml"), ("All files", "*.*"))
        )
        if files:
            for file in files:
                if file not in self.file_list:
                    self.file_list.append(file)
                    self.listbox.insert(tk.END, os.path.basename(file))
            self.status_var.set(f"Added {len(files)} file(s). Total: {len(self.file_list)}")

    def remove_selected(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            self.status_var.set("No files selected to remove.")
            return

        # Remove from the end to avoid index shifting issues
        for i in sorted(selected_indices, reverse=True):
            self.listbox.delete(i)
            del self.file_list[i]

        self.status_var.set(f"Removed files. Total: {len(self.file_list)}")

    def merge_files(self):
        # Placeholder for now. The full logic will be implemented in the next steps.
        if len(self.file_list) < 2:
            messagebox.showwarning("Not enough files", "Please select at least two files to merge.")
            return
        if len(self.file_list) < 2:
            messagebox.showwarning("Not enough files", "Please select at least two files to merge.")
            return

        all_data = []
        all_headers = set()

        self.status_var.set("Starting merge...")
        self.root.update_idletasks()

        for file_path in self.file_list:
            file_ext = os.path.splitext(file_path)[1].lower()
            data = []
            if file_ext == '.csv':
                data = read_csv(file_path)
            elif file_ext == '.xml':
                data = read_xml(file_path)

            if data:
                all_data.extend(data)
                for row in data:
                    all_headers.update(row.keys())

        if not all_data:
            messagebox.showerror("Error", "No data could be read from the selected files.")
            self.status_var.set("Merge failed. No data found.")
            return

        # Normalize data - ensure all rows have all headers
        normalized_data = []
        for row in all_data:
            normalized_row = {header: row.get(header, '') for header in all_headers}
            normalized_data.append(normalized_row)

        # Ask user for output file location
        output_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            title="Save Merged File As..."
        )

        if not output_path:
            self.status_var.set("Save cancelled.")
            return

        # Write the merged data to the selected file
        success = write_csv(normalized_data, output_path, all_headers)

        if success:
            messagebox.showinfo("Success", f"Successfully merged {len(self.file_list)} files and saved to:\n{output_path}")
            self.status_var.set("Merge and save complete!")
        else:
            # Error message is shown by write_csv
            self.status_var.set("Failed to save the file.")


def write_csv(data, file_path, fieldnames):
    """Writes a list of dictionaries to a CSV file."""
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(list(fieldnames)))
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write output file:\n{e}")
        return False

if __name__ == '__main__':
    root = tk.Tk()
    app = MergerApp(root)
    root.mainloop()
