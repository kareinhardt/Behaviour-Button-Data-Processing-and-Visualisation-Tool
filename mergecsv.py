import os
import sys
import pandas as pd
from datetime import datetime
import subprocess

def list_folders(root_folder):
    subfolders = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))]
    for idx, folder in enumerate(subfolders, 1):
        print(f"[{idx}] {folder}")
    return subfolders

def get_folder_selection(subfolders):
    while True:
        try:
            selection = int(input("Select a folder by number: "))
            if 1 <= selection <= len(subfolders):
                return subfolders[selection - 1]
            else:
                print("Invalid selection, please select a valid number.")
        except ValueError:
            print("Invalid input, please enter a number.")

def confirm_selection(folder_name, file_count):
    while True:
        confirmation = input(f"Folder \"{folder_name}\" is selected and contains {file_count} file(s). Enter Y to continue or N to go back to selection: ").strip().upper()
        if confirmation in ['Y', 'N']:
            return confirmation == 'Y'
        else:
            print("Invalid input, please enter Y or N.")

def list_csv_files(folder_path, print_files=True):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if print_files:
        for idx, file in enumerate(csv_files, 1):
            print(f"---- ({idx}) {file}")
    return csv_files


def confirm_file_list():
    while True:
        confirmation = input("Enter Y to continue, N to go back to folder selection: ").strip().upper()
        if confirmation in ['Y', 'N']:
            return confirmation == 'Y'
        else:
            print("Invalid input, please enter Y or N.")

def merge_csv_files(folder_path, csv_files, output_folder):
    merged_df = pd.concat([pd.read_csv(os.path.join(folder_path, file)) for file in csv_files], ignore_index=True)
    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]  # Remove duplicate columns if any

    output_filename = f"merged_file_on_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    output_path = os.path.join(output_folder, output_filename)
    merged_df.to_csv(output_path, index=False)

    first_date = pd.to_datetime(merged_df.iloc[:, 0], errors='coerce').min()
    last_date = pd.to_datetime(merged_df.iloc[:, 0], errors='coerce').max()
    print(f"{len(merged_df)} entries from {len(csv_files)} file(s), ranging from {first_date.date()} to {last_date.date()}, have been merged to file {output_filename}")

def main():
    root_folder = "data_input"
    output_folder = "data_output"
    os.makedirs(output_folder, exist_ok=True)

    while True:
        subfolders = list_folders(root_folder)
        selected_folder = get_folder_selection(subfolders)
        folder_path = os.path.join(root_folder, selected_folder)
        
        # Get CSV files without printing
        csv_files = list_csv_files(folder_path, print_files=False)
        if not csv_files:
            print("No CSV files found in the selected folder. Please choose another folder.")
            continue

        # Use the length of csv_files without printing again
        if confirm_selection(selected_folder, len(csv_files)):
            print(f"---[{subfolders.index(selected_folder) + 1}] {selected_folder}---")
            
            # Now print the CSV files
            list_csv_files(folder_path)  # Default is print_files=True
            if confirm_file_list():
                merge_csv_files(folder_path, csv_files, output_folder)
                break
            else:
                continue
        else:
            continue


if __name__ == "__main__":
    main()
