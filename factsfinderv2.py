import os
import pandas as pd
from datetime import datetime

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


def merge_csv_files(folder_path, csv_files):
    merged_df = pd.concat([pd.read_csv(os.path.join(folder_path, file)) for file in csv_files], ignore_index=True)
    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]  # Remove duplicate columns if any

    first_date = pd.to_datetime(merged_df.iloc[:, 0], errors='coerce').min().date()
    last_date = pd.to_datetime(merged_df.iloc[:, 0], errors='coerce').max().date()
    print(f"{len(merged_df)} entries from {len(csv_files)} file(s), ranging from {first_date} to {last_date}, have been loaded for analysis.")

    return merged_df, first_date, last_date


def get_date_range(first_date, last_date):
    while True:
        start_date_str = input("Enter start date in YYYYMMDD format: ").strip()
        try:
            start_date = datetime.strptime(start_date_str, '%Y%m%d').date()
            if start_date < first_date:
                print(f"Start date cannot be earlier than {first_date}. Please enter a valid start date.")
                continue
            if start_date > last_date:
                print(f"Start date cannot be later than {last_date}. Please enter a valid start date.")
                continue
            break
        except ValueError:
            print("Invalid date format. Please enter in YYYYMMDD format.")

    while True:
        end_date_str = input("Enter end date in YYYYMMDD format: ").strip()
        try:
            end_date = datetime.strptime(end_date_str, '%Y%m%d').date()
            if end_date < start_date:
                print("End date cannot be earlier than start date. Please enter a valid end date.")
                continue
            if end_date > last_date:
                print(f"End date cannot be later than {last_date}. Please enter a valid end date.")
                continue
            break
        except ValueError:
            print("Invalid date format. Please enter in YYYYMMDD format.")

    return start_date, end_date


def analyze_data(merged_df, start_date, end_date):
    merged_df['Date'] = pd.to_datetime(merged_df.iloc[:, 0], errors='coerce').dt.date
    filtered_df = merged_df[(merged_df['Date'] >= start_date) & (merged_df['Date'] <= end_date)]

    # Check if 'Hub Name' and 'Behaviour Name' columns exist
    if 'Hub Name' not in filtered_df.columns or 'Behaviour Name' not in filtered_df.columns:
        print("Error: Required columns 'Hub Name' or 'Behaviour Name' not found in the data.")
        return

    # Total entries per hub
    hub_counts = filtered_df['Hub Name'].value_counts()
    print("\nTotal entries per hub in the given time range:")
    for hub, count in hub_counts.items():
        print(f"{hub}: {count} entries")

    # Entries per behavior per hub (original)
    behaviors = filtered_df['Behaviour Name'].unique()
    print("\nEntries per behavior per hub in the given time range:")
    for behavior in behaviors:
        behavior_df = filtered_df[filtered_df['Behaviour Name'] == behavior]
        behavior_counts = behavior_df['Hub Name'].value_counts()
        print(f"\nBehavior: {behavior}")
        for hub, count in behavior_counts.items():
            print(f"{hub}: {count} entries")

    # Most frequent behavior per hub (original)
    print("\nMost frequent behavior per hub in the given time range:")
    most_frequent_behaviors = filtered_df.groupby('Hub Name')['Behaviour Name'].apply(lambda x: x.value_counts().head(1))
    for (hub, behavior), count in most_frequent_behaviors.items():
        print(f"{hub}: {behavior} ({count} times)")

    # Additional insights:
    # For each Hub, show total entries, and for each behaviour within that Hub
    # show count and percentage of the Hub's total, sorted from most to least.
    print("\nAdditional Insights:")
    hubs = filtered_df['Hub Name'].unique()
    for hub in hubs:
        hub_df = filtered_df[filtered_df['Hub Name'] == hub]
        hub_total = len(hub_df)
        behaviour_counts = hub_df['Behaviour Name'].value_counts()

        print(f"\nHub: {hub}")
        print(f"  Total entries: {hub_total}")
        print("  Behaviours (most to least frequent):")
        for behaviour, bcount in behaviour_counts.items():
            percentage = (bcount / hub_total) * 100
            print(f"    {behaviour}: {bcount} entries ({percentage:.2f}% of {hub})")

def main():
    root_folder = "data_input"
    os.makedirs(root_folder, exist_ok=True)

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
                merged_df, first_date, last_date = merge_csv_files(folder_path, csv_files)
                start_date, end_date = get_date_range(first_date, last_date)
                analyze_data(merged_df, start_date, end_date)
                break
            else:
                continue
        else:
            continue

if __name__ == "__main__":
    main()
