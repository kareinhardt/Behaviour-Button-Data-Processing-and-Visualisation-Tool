import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.colors import to_rgb


pd.options.mode.chained_assignment = None  # Suppress SettingWithCopyWarning

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

def list_csv_files(folder_path, print_files=True):
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    if print_files:
        for idx, file in enumerate(csv_files, 1):
            print(f"---- ({idx}) {file}")
    return csv_files

def confirm_selection(folder_name, file_count):
    while True:
        confirmation = input(f"Folder \"{folder_name}\" is selected and contains {file_count} file(s). Enter Y to continue or N to go back to selection: ").strip().upper()
        if confirmation in ['Y', 'N']:
            return confirmation == 'Y'
        else:
            print("Invalid input, please enter Y or N.")

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
    
    # Assuming the 'Timestamp' column is present and contains both date and time
    merged_df['Timestamp'] = pd.to_datetime(merged_df['Timestamp'])
    merged_df['Date'] = merged_df['Timestamp'].dt.date
    merged_df['Time'] = merged_df['Timestamp'].dt.time
    first_date = merged_df['Date'].min()
    last_date = merged_df['Date'].max()
    return merged_df, first_date, last_date

def get_date_range(first_date, last_date):
    print(f"Available data range: {first_date} to {last_date}")
    while True:
        try:
            start_date = pd.to_datetime(input("Enter start date (YYYY-MM-DD): ")).date()
            end_date = pd.to_datetime(input("Enter end date (YYYY-MM-DD): ")).date()
            if first_date <= start_date <= last_date and first_date <= end_date <= last_date and start_date <= end_date:
                return start_date, end_date
            else:
                print("Invalid date range. Please enter dates within the available range.")
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

def confirm_date_selection(start_date, end_date):
    while True:
        confirmation = input(f"You selected a date range from {start_date} to {end_date}. Enter Y to continue or N to reselect: ").strip().upper()
        if confirmation in ['Y', 'N']:
            return confirmation == 'Y'
        else:
            print("Invalid input, please enter Y or N.")

def create_data_vis_folder():
    export_folder_name = f"DataVis_Export_on_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    export_path = os.path.join('data_output', export_folder_name)
    os.makedirs(export_path, exist_ok=True)
    return export_path

def generate_heatmap(df, hub_name, behavior_name, export_path, start_date, end_date):
    # Prepare data for the heatmap
    df = df.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Extract date and weekday
    df['Date'] = df['Timestamp'].dt.date
    df['Weekday'] = df['Timestamp'].dt.strftime('%a')
    df['Date_with_Weekday'] = df['Date'].astype(str) + ' (' + df['Weekday'] + ')'
    
    # Create half-hour intervals by flooring the time to the nearest 30 minutes
    df['Half Hour'] = df['Timestamp'].dt.floor('30min').dt.strftime('%H:%M')
    
    # Create a date range and time slots to ensure the chart includes all dates and times
    date_range = pd.date_range(start=start_date, end=end_date)
    date_labels = date_range.strftime('%Y-%m-%d (%a)').tolist()
    weekdays = date_range.strftime('%a').tolist()
    time_slots = [f'{hour:02d}:{minute:02d}' for hour in range(24) for minute in [0, 30]]
    
    # Pivot the DataFrame to create a matrix for the heatmap
    pivot_df = df.pivot_table(
        index='Date_with_Weekday',
        columns='Half Hour',
        values='Button ID',
        aggfunc='count',
        fill_value=0
    )
    pivot_df = pivot_df.reindex(index=date_labels, columns=time_slots, fill_value=0)
    
    data = pivot_df.values
    num_rows, num_columns = data.shape

    # Calculate figure size to make cells square
    cell_size = 0.5  # Cell size in inches
    fig_width = cell_size * num_columns
    # We'll calculate fig_height after determining total_height

    # Calculate spacing and adjusted cell size
    spacing_ratio = 0.15  # 15% spacing between cells
    spacing = spacing_ratio
    adjusted_cell_size = 1 - spacing

    # Calculate linewidth in points (5% of cell height)
    linewidth_in_points = cell_size * 0.05 * 72  # 1 inch = 72 points

    # Calculate extra spacing between specific days
    extra_spacing_ratio = 0.5  # 50% of cell height
    extra_spacing = extra_spacing_ratio  # In data units

    # Create y_positions for each row
    y_positions = []
    y = 0
    for i in range(num_rows):
        y_positions.append(y)
        # Decide on extra spacing after this row
        if i < num_rows - 1:
            current_weekday = weekdays[i]
            next_weekday = weekdays[i + 1]
            if (current_weekday == 'Fri' and next_weekday == 'Sat') or \
               (current_weekday == 'Sun' and next_weekday == 'Mon'):
                y += adjusted_cell_size + spacing + extra_spacing
            else:
                y += adjusted_cell_size + spacing
        else:
            # For the last row, just add the cell height and spacing
            y += adjusted_cell_size + spacing

    total_height = y  # The total height including extra spacings
    fig_height = cell_size * total_height

    # Create the figure and axes
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Define the colors for values from 1 to 5 and '5+'
    value_colors = {
        1: '#FFFFE0',   # Light Yellow
        2: '#FFDAB9',   # Peach Puff
        3: '#FFA07A',   # Light Salmon
        4: '#FF7F50',   # Coral
        5: '#FF4500',   # Orange Red
        '5+': '#8B0000' # Dark Red
    }

    # Create the list of colors in order
    colors = [
        value_colors[1],
        value_colors[2],
        value_colors[3],
        value_colors[4],
        value_colors[5],
        value_colors['5+']
    ]

    # Define the boundaries for the norm
    bounds = [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5]  # Replaced np.inf with 6.5

    # Create the colormap and norm
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(bounds, cmap.N)

    # Calculate scale factor from data units to inches
    scale_factor = fig_height / total_height

    # Calculate cell height in inches and points
    cell_height_in_inches = adjusted_cell_size * scale_factor
    cell_height_in_points = cell_height_in_inches * 72  # Convert inches to points

    # Adjust font size to 55% of cell height
    font_size = cell_height_in_points * 0.45  # 55% of cell height in points

    # Draw the heatmap cells with rounded corners and spacing
    for (i, j), value in np.ndenumerate(data):
        # Calculate positions with spacing and extra offsets
        x = j + spacing / 2
        y_cell = y_positions[i] + spacing / 2

        time_label = pivot_df.columns[j]
        facecolor = None
        edgecolor = None
        linewidth = 0

        if value == 0:
            facecolor = 'none'  # No background color
            linewidth = linewidth_in_points

            if time_label.endswith(':00'):
                edgecolor = '#E6E7E6'  # Border color for '00' minutes
            elif time_label.endswith(':30'):
                edgecolor = '#C4C4C4'  # Border color for '30' minutes
            else:
                edgecolor = 'black'  # Default edge color if time format is unexpected
        else:
            # Determine the appropriate color based on the value
            if value <= 5:
                color_index = int(value) - 1  # Indices start from 0
            else:
                color_index = 5  # '5+' color
            facecolor = cmap.colors[color_index]
            edgecolor = None
            linewidth = 0

        # Draw the cell
        rect = FancyBboxPatch(
            (x, y_cell),
            adjusted_cell_size,
            adjusted_cell_size,
            boxstyle=f"round,pad=0,rounding_size={adjusted_cell_size * 0.25}",
            linewidth=linewidth,
            edgecolor=edgecolor,
            facecolor=facecolor
        )
        ax.add_patch(rect)

        # Add the data value as text in the center of the cell with padding
        if value != 0:
            # Convert facecolor to RGB tuple
            r, g, b = to_rgb(facecolor)  # Returns values between 0 and 1

            # Calculate text color based on cell background color
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b  # Relative luminance
            text_color = 'black' if luminance > 0.6 else 'white'

            # Position of the text (center of the cell)
            x_text = x + adjusted_cell_size / 2
            y_text = y_cell + adjusted_cell_size / 2

            # Add text
            ax.text(
                x_text,
                y_text,
                int(value),
                ha='center',
                va='center',
                color=text_color,
                fontsize=font_size,
                clip_on=False
            )

    # Set the limits, labels, and ticks
    ax.set_xlim(0, num_columns)
    ax.set_ylim(0, total_height)
    # No need to invert y-axis

    # Set x-ticks
    ax.set_xticks(np.arange(num_columns) + 0.5)
    ax.set_xticklabels(pivot_df.columns, rotation=90)

    # Adjust y-ticks to account for extra spacing
    y_tick_positions = [y_positions[i] + adjusted_cell_size / 2 for i in range(num_rows)]
    ax.set_yticks(y_tick_positions)
    ax.set_yticklabels(pivot_df.index)
    ax.set_xlabel("Time of Day (Half-Hour Intervals)")
    ax.set_ylabel("Date (Weekday)")
    plt.title(f"{hub_name} - {behavior_name}")

    # Remove the spines and set aspect ratio
    ax.set_aspect('equal')
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Add a colorbar with custom ticks and labels
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Adjust the colorbar to handle the finite bounds
    cbar = plt.colorbar(sm, ax=ax, boundaries=bounds, ticks=[1, 2, 3, 4, 5, 6])
    cbar.set_label('Count')
    cbar.ax.set_yticklabels(['1', '2', '3', '4', '5', '5+'])

    # Save the heatmap as a PNG file
    export_file_name = f"{hub_name}-{behavior_name}.png"
    plt.savefig(os.path.join(export_path, export_file_name), format='png', bbox_inches='tight')
    plt.close()

def analyze_and_generate_charts(merged_df, start_date, end_date):
    # Filter data based on the selected date range
    filtered_df = merged_df[(merged_df['Date'] >= start_date) & (merged_df['Date'] <= end_date)]
    
    # Get unique hubs and behaviors
    hubs = filtered_df['Hub Name'].unique()
    behaviors = filtered_df['Behaviour Name'].unique()

    # Create a folder for exporting the charts
    export_path = create_data_vis_folder()

    # Generate charts for each hub and each behavior
    for hub in hubs:
        for behavior in behaviors:
            behavior_df = filtered_df[(filtered_df['Hub Name'] == hub) & (filtered_df['Behaviour Name'] == behavior)]
            generate_heatmap(behavior_df, hub, behavior, export_path, start_date, end_date)

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
                if confirm_date_selection(start_date, end_date):
                    analyze_and_generate_charts(merged_df, start_date, end_date)
                break
            else:
                continue
        else:
            continue

if __name__ == "__main__":
    main()
