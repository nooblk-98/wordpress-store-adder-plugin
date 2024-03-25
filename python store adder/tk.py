import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import requests
import time
import pandas as pd
import json
import tempfile
import os

class StoreImporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Store Importer')

        self.file_path = ''
        self.json_file_path = ''
        self.stop_flag = False

        self.create_widgets()

    def create_widgets(self):
        # Excel file selection
        self.excel_label = tk.Label(self.root, text='Excel File:')
        self.excel_path_label = tk.Label(self.root, text='No file selected')
        self.excel_button = tk.Button(self.root, text='Select Excel File', command=self.select_excel_file)

        self.excel_label.pack()
        self.excel_path_label.pack()
        self.excel_button.pack()

        # Sheet name input
        self.sheet_label = tk.Label(self.root, text='Sheet Name:')
        self.sheet_input = tk.Entry(self.root)

        self.sheet_label.pack()
        self.sheet_input.pack()

        # Convert button
        self.convert_button = tk.Button(self.root, text='Convert Excel to JSON', command=self.convert_excel_to_json)
        self.convert_button.pack()

        # Open JSON file button
        self.open_button = tk.Button(self.root, text='Open JSON File', command=self.open_json_file, state=tk.DISABLED)
        self.open_button.pack()


        # JSON file selection
        self.import_label = tk.Label(self.root, text='Import JSON File:')
        self.import_path_label = tk.Label(self.root, text='No file selected')
        self.import_button = tk.Button(self.root, text='Select JSON File', command=self.select_json_file)

        self.import_label.pack()
        self.import_path_label.pack()
        self.import_button.pack()


        # Import log
        self.import_log = tk.Text(self.root, height=10, width=50)
        self.import_log.pack()

        # Import progress
        self.progress_label = tk.Label(self.root, text='Progress:')
        self.progress_bar = tk.ttk.Progressbar(self.root, orient='horizontal', length=200, mode='determinate')
        self.progress_label.pack()
        self.progress_bar.pack()

        # Import stores button
        self.import_stores_button = tk.Button(self.root, text='Import Stores', command=self.import_stores)
        self.import_stores_button.pack()

        # Stop button
        self.stop_button = tk.Button(self.root, text='Stop Import', command=self.stop_import)
        self.stop_button.pack()

    def select_excel_file(self):
        self.file_path = filedialog.askopenfilename(title='Select Excel File', filetypes=[('Excel Files', '*.xlsx')])
        if self.file_path:
            self.excel_path_label.config(text=self.file_path)

    def select_json_file(self):
        self.json_file_path = filedialog.askopenfilename(title='Select JSON File', filetypes=[('JSON Files', '*.json')])
        if self.json_file_path:
            self.import_path_label.config(text=self.json_file_path)
            self.open_button.config(state=tk.NORMAL)

    def convert_excel_to_json(self):
        sheet_name = self.sheet_input.get()
        if self.file_path and sheet_name:
            df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            selected_columns = df[['NAMECUST', 'ADDRESS', 'CITY', 'DISTRICT']]
            renamed_columns = selected_columns.rename(columns={
                'NAMECUST': 'name',
                'ADDRESS': 'address',
                'CITY': 'city',
                'DISTRICT': 'state'
            })
            renamed_columns['country'] = 'SRILANKA'
            json_data = renamed_columns.to_json(orient='records', indent=4)

            temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
            with open(temp_file.name, 'w') as file:
                json.dump(json.loads(json_data), file, indent=4)

            self.json_file_path = temp_file.name
            self.import_path_label.config(text=self.json_file_path)
            self.open_button.config(state=tk.NORMAL)
        else:
            messagebox.showerror('Error', 'Please select an Excel file and enter a sheet name')

    def import_stores(self):
        if self.json_file_path:
            self.stop_flag = False
            with open(self.json_file_path, 'r') as file:
                stores = json.load(file)

            total_stores = len(stores)
            api_endpoint = 'https://demo-store.itsnooblk.xyz/wp-json/store-locator/v1/add-store'
            auth_credentials = ('admin', 'admin')

            self.progress_bar.config(maximum=total_stores, value=0)
            self.import_log.delete('1.0', tk.END)

            for idx, store in enumerate(stores, start=1):
                if self.stop_flag:
                    self.import_log.insert(tk.END, 'Import stopped\n')
                    break

                response = requests.post(api_endpoint, json=store, auth=auth_credentials)
                if response.status_code == 200:
                    self.import_log.insert(tk.END, f"Store added successfully: {store['name']}\n")
                else:
                    self.import_log.insert(tk.END, f"Failed to add store: {store['name']} - {response.text}\n")
                self.progress_bar.config(value=idx)
                self.progress_bar.update()  # Update the progress bar
                self.import_log.see(tk.END)  # Scroll to the end of the log
                self.root.update()  # Update the GUI to show the log
                time.sleep(1)  # Add a delay between requests for stability
        else:
            messagebox.showerror('Error', 'Please select a JSON file')

    def stop_import(self):
        self.stop_flag = True

    def open_json_file(self):
        if self.json_file_path:
            os.system('start ' + self.json_file_path)
        else:
            messagebox.showerror('Error', 'No JSON file selected')

if __name__ == '__main__':
    root = tk.Tk()
    app = StoreImporterApp(root)
    root.mainloop()
