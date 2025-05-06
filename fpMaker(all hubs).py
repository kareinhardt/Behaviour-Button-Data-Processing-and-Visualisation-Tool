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
            start_input = input(f"Enter start date (YYYY-MM-DD) [default: {first_date}]: ").strip()
            if start_input:
                start_date = pd.to_datetime(start_input).date()
            else:
                start_date = first_date

            end_input = input(f"Enter end date (YYYY-MM-DD) [default: {last_date}]: ").strip()
            if end_input:
                end_date = pd.to_datetime(end_input).date()
            else:
                end_date = last_date
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
    
    # Create a date range and time slots to ensure the chart includes all dates and times , added [::-1] to invert
    date_range = pd.date_range(start=start_date, end=end_date)
    date_labels = date_range.strftime('%Y-%m-%d (%a)').tolist()[::-1]
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

def generate_consolidated_chart(df, export_path, start_date, end_date):
    # Prepare data for the chart
    df = df.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date
    df['Hour'] = df['Timestamp'].dt.hour

    # Create a date range to ensure all dates are included
    date_range = pd.date_range(start=start_date, end=end_date).date
    data_matrix = pd.DataFrame(index=date_range, columns=range(24), data=0)

    # Mark hours with logged behavior as 1
    for date, hour in zip(df['Date'], df['Hour']):
        if date in data_matrix.index:
            data_matrix.loc[date, hour] = 1

    # Convert to numpy array for easier plotting
    data = data_matrix.values
    num_rows, num_columns = data.shape

    # Set up figure dimensions
    cell_size = 0.5  # Cell size in inches
    fig_width = cell_size * num_columns
    fig_height = cell_size * num_rows

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Define colors for cells
    has_data_color = '#9700FF'
    no_data_color = '#3C0066'

    # Draw the chart
    for (i, j), value in np.ndenumerate(data):
        color = has_data_color if value == 1 else no_data_color
        rect = FancyBboxPatch(
            (j, num_rows - i - 1),  # Reverse y-axis for proper date sorting
            1,
            1,
            boxstyle="square,pad=0",
            facecolor=color,
            edgecolor='none'
        )
        ax.add_patch(rect)

    # Adjust axis limits and aspect ratio
    ax.set_xlim(0, num_columns)
    ax.set_ylim(0, num_rows)
    ax.set_aspect('equal')

    # Remove ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Save the chart
    export_file_name = f"Consolidated_Chart_{start_date}_to_{end_date}.png"
    plt.savefig(os.path.join(export_path, export_file_name), format='png', bbox_inches='tight')
    plt.close()

def generate_styled_consolidated_chart(df, export_path, start_date, end_date):

    # Prepare data for the chart
    df = df.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date
    df['Hour'] = df['Timestamp'].dt.hour

    # Create a date range to ensure all dates are included
    date_range = pd.date_range(start=start_date, end=end_date).date
    data_matrix = pd.DataFrame(index=date_range, columns=range(24), data=0)

    # Mark hours with logged behavior as 1
    for date, hour in zip(df['Date'], df['Hour']):
        if date in data_matrix.index:
            data_matrix.loc[date, hour] = 1

    # Convert to numpy array for easier plotting
    data = data_matrix.values
    num_rows, num_columns = data.shape

    # Style settings
    cell_size = 20  # px
    corner_radius = 4  # px
    spacing = 8  # px
    has_data_color = '#9700FF'
    no_data_color = '#3C0066'
    background_color = '#FFFFFF'  # White background

    # Calculate figure dimensions (convert px to inches: 1 inch = 72px)
    fig_width = (cell_size + spacing) * num_columns / 72
    fig_height = (cell_size + spacing) * num_rows / 72

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    # Draw the chart
    for (i, j), value in np.ndenumerate(data):
        x = j * (cell_size + spacing) / 72
        y = (num_rows - i - 1) * (cell_size + spacing) / 72
        color = has_data_color if value == 1 else no_data_color
        rect = FancyBboxPatch(
            (x, y),  # Position
            cell_size / 72,  # Width
            cell_size / 72,  # Height
            boxstyle=f"round,pad=0,rounding_size={corner_radius / 72}",  # Rounded corners
            facecolor=color,
            edgecolor='none'  # Remove border
        )
        ax.add_patch(rect)

    # Adjust axis limits to make the outer ring the edge of the chart
    ax.set_xlim(0, num_columns * (cell_size + spacing) / 72)
    ax.set_ylim(0, num_rows * (cell_size + spacing) / 72)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.invert_yaxis()  # Match the order with dates from top to bottom

    # Save the chart
    export_file_name = f"Styled_Consolidated_Chart_{start_date}_to_{end_date}.png"
    plt.savefig(os.path.join(export_path, export_file_name), format='png', dpi=300, bbox_inches='tight')
    plt.close()


def analyze_and_generate_consolidated_chart(merged_df, start_date, end_date):
    # Filter data based on the selected date range
    filtered_df = merged_df[(merged_df['Date'] >= start_date) & (merged_df['Date'] <= end_date)]

    # Create a folder for exporting the chart
    export_path = create_data_vis_folder()

    # Generate the consolidated chart
    generate_consolidated_chart(filtered_df, export_path, start_date, end_date)


def analyze_and_generate_styled_consolidated_chart(merged_df, start_date, end_date):
    # Filter data based on the selected date range
    filtered_df = merged_df[(merged_df['Date'] >= start_date) & (merged_df['Date'] <= end_date)]

    # Create a folder for exporting the chart
    export_path = create_data_vis_folder()

    # Generate the styled consolidated chart
    generate_styled_consolidated_chart(filtered_df, export_path, start_date, end_date)
    
def generate_transparent_chart(df, export_path, start_date, end_date):
    # Prepare data for the chart
    df = df.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date
    df['Hour'] = df['Timestamp'].dt.hour

    # Create a date range to ensure all dates are included
    date_range = pd.date_range(start=start_date, end=end_date).date
    data_matrix = pd.DataFrame(index=date_range, columns=range(24), data=0)

    # Mark hours with logged behavior as 1
    for date, hour in zip(df['Date'], df['Hour']):
        if date in data_matrix.index:
            data_matrix.loc[date, hour] = 1

    # Convert to numpy array for easier plotting
    data = data_matrix.values
    num_rows, num_columns = data.shape

    # Style settings
    cell_size = 20  # px
    corner_radius = 4  # px
    spacing = 8  # px
    has_data_color = '#9700FF'
    no_data_color = '#3C0066'

    # Calculate figure dimensions (convert px to inches: 1 inch = 72px)
    fig_width = (cell_size * num_columns + spacing * (num_columns - 1)) / 72
    fig_height = (cell_size * num_rows + spacing * (num_rows - 1)) / 72

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_alpha(0)  # Transparent figure background
    ax.set_alpha(0)  # Transparent axis background

    # Draw the chart
    for (i, j), value in np.ndenumerate(data):
        x = j * (cell_size + spacing) / 72
        y = (num_rows - i - 1) * (cell_size + spacing) / 72
        color = has_data_color if value == 1 else no_data_color
        rect = FancyBboxPatch(
            (x, y),  # Position
            cell_size / 72,  # Width
            cell_size / 72,  # Height
            boxstyle=f"round,pad=0,rounding_size={corner_radius / 72}",  # Rounded corners
            facecolor=color,
            edgecolor='none'  # No border
        )
        ax.add_patch(rect)

    # Remove axis spines (black border lines)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Adjust axis limits to perfectly match the grid
    ax.set_xlim(0, num_columns * (cell_size + spacing) / 72 - spacing / 72)
    ax.set_ylim(0, num_rows * (cell_size + spacing) / 72 - spacing / 72)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.invert_yaxis()  # Match the order with dates from top to bottom

    # Save the chart with transparent background and no margins
    export_file_name = f"Transparent_Styled_Consolidated_Chart_{start_date}_to_{end_date}.png"
    plt.savefig(
        os.path.join(export_path, export_file_name),
        format='png',
        dpi=300,
        bbox_inches='tight',  # No extra margin
        pad_inches=0,  # Remove all padding
        transparent=True  # Transparent background
    )
    plt.close()




# --- New function: generate_heatmaps_by_behavior
def generate_heatmaps_by_behavior(df, hub_name, export_path, start_date, end_date):
    """
    Generate a heatmap for each unique behavior type (Behaviour Name) in the data.
    """
    # Get unique behavior identifiers
    behaviors = df['Behaviour Name'].unique()
    for behavior in behaviors:
        # Filter data for this behavior
        filtered_df = df[df['Behaviour Name'] == behavior]
        # Use the behavior ID as the name in the title/file
        behavior_name = str(behavior)
        generate_heatmap(
            filtered_df,
            hub_name,
            behavior_name,
            export_path,
            start_date,
            end_date
        )

# --- New function: generate_consolidated_by_behavior

def generate_consolidated_by_behavior(df, hub_name, export_path, start_date, end_date):
    """
    Generate a transparent styled consolidated chart for each unique behavior type (Behaviour Name) over the time period.
    """
    behaviors = df['Behaviour Name'].unique()
    for behavior in behaviors:
        # Filter data for this behavior
        filtered_df = df[df['Behaviour Name'] == behavior]
        # Generate the transparent styled consolidated chart for this behavior
        generate_transparent_chart(filtered_df, export_path, start_date, end_date)
        # Rename the generated file to include the behavior
        old_file = f"Transparent_Styled_Consolidated_Chart_{start_date}_to_{end_date}.png"
        new_file = f"{behavior}_Transparent_Styled_Consolidated_Chart_{start_date}_to_{end_date}.png"
        os.rename(
            os.path.join(export_path, old_file),
            os.path.join(export_path, new_file)
        )

# --- New function: generate_behavior_mix_chart
def generate_behavior_mix_chart(df, export_path, start_date, end_date):
    """
    Generate a transparent chart where each non‑empty hour cell is divided vertically into equal
    slices representing the behaviours present in that hour (Cooking fresh, Eating Out,
    Re‑Heating Food, Snacking, Take Away). Unknown behaviours are ignored.
    """
    # Prepare data
    df = df.copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date
    df['Hour'] = df['Timestamp'].dt.hour

    # Behaviour order and colours
    behaviour_order = [
        "Cooking fresh",
        "Eating Out",
        "Re-Heating Food",
        "Snacking",
        "Take Away",
    ]
    colour_map = {
        "Cooking fresh": "#FF085A",
        "Eating Out": "#FFB1CE",
        "Re-Heating Food": "#D29FF5",
        "Snacking": "#9700FF",
        "Take Away": "#FBE8E0",
    }
    no_data_color = "#3C0066"

    # Build grid axes
    date_range = pd.date_range(start=start_date, end=end_date).date
    hours = range(24)

    # Style constants (match transparent chart)
    cell_size = 20  # px
    spacing = 8    # px
    corner_radius = 4  # px (same as Transparent Chart)
    fig_width = (cell_size * len(hours) + spacing * (len(hours) - 1)) / 72
    fig_height = (cell_size * len(date_range) + spacing * (len(date_range) - 1)) / 72

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_alpha(0)
    ax.set_alpha(0)

    for i, date in enumerate(reversed(date_range)):
        for j, hr in enumerate(hours):
            x0 = j * (cell_size + spacing) / 72
            y0 = i * (cell_size + spacing) / 72

            # Determine which of the 5 behaviours appear in this cell
            present = (
                df[(df['Date'] == date) & (df['Hour'] == hr)]['Behaviour Name']
                .dropna()
                .unique()
                .tolist()
            )
            present = [b for b in behaviour_order if b in present]
            n = len(present)

            if n == 0:
                # Empty cell
                rect = FancyBboxPatch(
                    (x0, y0), cell_size / 72, cell_size / 72,
                    boxstyle=f"round,pad=0,rounding_size={corner_radius/72}",
                    facecolor=no_data_color,
                    edgecolor='none'
                )
                ax.add_patch(rect)
            else:
                # Create a rounded cell path for clipping the slices
                cell_patch = FancyBboxPatch(
                    (x0, y0),
                    cell_size/72,
                    cell_size/72,
                    boxstyle=f"round,pad=0,rounding_size={corner_radius/72}",
                    facecolor="none",
                    edgecolor="none"
                )
                ax.add_patch(cell_patch)

                cell_unit = cell_size / 72  # full cell width in inches
                ideal_slice_w = cell_unit / n
                for k, beh in enumerate(present):
                    if k < n - 1:
                        width = ideal_slice_w
                    else:
                        # last slice takes the remainder to avoid gaps due to float rounding
                        width = cell_unit - ideal_slice_w * (n - 1)
                    sx = x0 + k * ideal_slice_w
                    slice_rect = plt.Rectangle(
                        (sx, y0),
                        width,
                        cell_unit,
                        facecolor=colour_map[beh],
                        edgecolor='none',
                        antialiased=False,
                        clip_path=cell_patch,
                        clip_on=True
                    )
                    ax.add_patch(slice_rect)

    # Show full grid without clipping edges
    ax.set_xlim(0, fig_width)
    ax.set_ylim(0, fig_height)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.invert_yaxis()
    # Remove axis spines (transparent style)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Save
    export_file = f"Behaviour_Mix_Chart_{start_date}_to_{end_date}.png"
    plt.savefig(
        os.path.join(export_path, export_file),
        format='png', dpi=300,
        bbox_inches='tight', pad_inches=0, transparent=True
    )
    plt.close()


# --- New function: generate_weekly_behavior_heatmaps
def generate_weekly_behavior_heatmaps(df, export_path, start_date, end_date):
    """
    For each Behaviour Name and for each calendar week in the date range,
    generate a 2×24 heatmap (row 1 = weekdays, row 2 = weekend) of event counts per hour.
    Uses 5‑level discrete gradient: 0→#3C0066, 1→#53008C, 2→#6A00B2,
    3→#8100D9, >=4→#9700FF. Transparent background.
    """
    import numpy as _np
    from matplotlib.colors import ListedColormap, BoundaryNorm
    # Prepare data
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'])
    df2['Date'] = df2['Timestamp'].dt.date
    df2['Hour'] = df2['Timestamp'].dt.hour
    df2['Year'] = df2['Timestamp'].dt.isocalendar().year
    df2['Week'] = df2['Timestamp'].dt.isocalendar().week

    # Colour gradient
    colors = ['#3C0066', '#53008C', '#6A00B2', '#8100D9', '#9700FF']
    cmap = ListedColormap(colors)
    norm = BoundaryNorm([0,1,2,3,4,5], len(colors))

    behaviours = df2['Behaviour Name'].dropna().unique()
    for beh in behaviours:
        beh_df = df2[df2['Behaviour Name']==beh]
        # group by year-week
        for (yr, wk), group in beh_df.groupby(['Year','Week']):
            # filter to only days within start/end
            subset = group[(group['Date']>=start_date)&(group['Date']<=end_date)]
            if subset.empty:
                continue
            # build 2×24 matrix: weekdays (Mon–Fri), weekends (Sat–Sun)
            mat = _np.zeros((2,24), dtype=int)
            # weekday mask: weekday <5
            wd = subset[subset['Timestamp'].dt.weekday<5]
            we = subset[subset['Timestamp'].dt.weekday>=5]
            for df_seg, row in ((wd,0),(we,1)):
                counts = df_seg.groupby('Hour').size()
                for h,c in counts.items():
                    mat[row, h] = c
            # draw heatmap
            cell_size=20; spacing=8; corner=4
            weeks = [f"{yr}-W{wk:02d}"]
            fig_w = (cell_size*24 + spacing*23)/72
            fig_h = (cell_size*2 + spacing)/72
            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            fig.patch.set_alpha(0); ax.set_alpha(0)
            for i in range(2):
                for j in range(24):
                    x=j*(cell_size+spacing)/72; y=(1-i)*(cell_size+spacing)/72
                    val=mat[i,j]
                    idx = val if val<4 else 4
                    rect = FancyBboxPatch(
                        (x,y), cell_size/72, cell_size/72,
                        boxstyle=f"round,pad=0,rounding_size={corner/72}",
                        facecolor=colors[idx], edgecolor='none'
                    )
                    ax.add_patch(rect)
            ax.set_xlim(0, fig_w); ax.set_ylim(0, fig_h)
            ax.set_xticks([]); ax.set_yticks([])
            ax.invert_yaxis()
            for spine in ax.spines.values(): spine.set_visible(False)
            # Compute min/max for filename
            min_val = int(mat.min())
            max_val = int(mat.max())
            fname = f"{beh}_{yr}-W{wk}_heatmap(min_{min_val}_max_{max_val})_{start_date}_to_{end_date}.png"
            plt.savefig(os.path.join(export_path, fname), format='png', dpi=300,
                        bbox_inches='tight', pad_inches=0, transparent=True)
            plt.close()

# --- New function: generate_overall_behavior_heatmaps
def generate_overall_behavior_heatmaps(df, export_path, start_date, end_date):
    """
    For each Behaviour Name, generate a 2×24 heatmap (row 0=weekdays, row 1=weekend)
    aggregated across the entire date range. Uses the same 5-level discrete gradient
    (#3C0066, #53008C, #6A00B2, #8100D9, #9700FF) and transparent background.
    """
    import numpy as _np
    from matplotlib.colors import ListedColormap, BoundaryNorm
    # Prepare data
    df2 = df.copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'])
    df2['Date'] = df2['Timestamp'].dt.date
    df2['Hour'] = df2['Timestamp'].dt.hour
    
    # Colour gradient
    colors = ['#3C0066', '#53008C', '#6A00B2', '#8100D9', '#9700FF']
    cmap = ListedColormap(colors)
    norm = BoundaryNorm([0,1,2,3,4,5], len(colors))
    
    behaviours = df2['Behaviour Name'].dropna().unique()
    for beh in behaviours:
        subset = df2[(df2['Behaviour Name']==beh) &
                     (df2['Date']>=start_date) & (df2['Date']<=end_date)]
        if subset.empty:
            continue
        # build 2×24 matrix
        mat = _np.zeros((2,24), dtype=int)
        wd = subset[subset['Timestamp'].dt.weekday < 5]
        we = subset[subset['Timestamp'].dt.weekday >= 5]
        for grp, row in ((wd,0),(we,1)):
            counts = grp.groupby('Hour').size()
            for h,c in counts.items():
                mat[row,h] = c
        # draw heatmap
        cell_size=20; spacing=8; corner=4
        fig_w = (cell_size*24 + spacing*23)/72
        fig_h = (cell_size*2 + spacing)/72
        fig, ax = plt.subplots(figsize=(fig_w, fig_h))
        fig.patch.set_alpha(0); ax.set_alpha(0)
        for i in range(2):
            for j in range(24):
                x=j*(cell_size+spacing)/72; y=(1-i)*(cell_size+spacing)/72
                val=mat[i,j]
                idx = val if val<4 else 4
                rect = FancyBboxPatch(
                    (x,y), cell_size/72, cell_size/72,
                    boxstyle=f"round,pad=0,rounding_size={corner/72}",
                    facecolor=colors[idx], edgecolor='none'
                )
                ax.add_patch(rect)
        ax.set_xlim(0, fig_w); ax.set_ylim(0, fig_h)
        ax.set_xticks([]); ax.set_yticks([])
        ax.invert_yaxis()
        for spine in ax.spines.values(): spine.set_visible(False)
        # Compute min/max for filename
        min_val = int(mat.min())
        max_val = int(mat.max())
        filename = f"{beh}_overall_heatmap(min_{min_val}_max_{max_val})_{start_date}_to_{end_date}.png"
        plt.savefig(
            os.path.join(export_path, filename),
            format='png', dpi=300,
            bbox_inches='tight', pad_inches=0, transparent=True
        )
        plt.close()


def main():
    root_folder = "data_input"  # Define the root folder where input data is stored
    os.makedirs(root_folder, exist_ok=True)  # Create the folder if it doesn't exist

    while True:  # Start the main loop
        subfolders = list_folders(root_folder)  # List all subfolders in the root folder
        selected_folder = get_folder_selection(subfolders)  # Prompt the user to select a folder
        folder_path = os.path.join(root_folder, selected_folder)  # Build the path to the selected folder
        
        # Get all CSV files in the folder without immediately printing them
        csv_files = list_csv_files(folder_path, print_files=False)
        if not csv_files:  # If no CSV files are found, prompt the user to choose another folder
            print("No CSV files found in the selected folder. Please choose another folder.")
            continue

        # Confirm the user's folder selection
        if confirm_selection(selected_folder, len(csv_files)):
            print(f"---[{subfolders.index(selected_folder) + 1}] {selected_folder}---")
            
            # Now print the CSV file list for the user to review
            list_csv_files(folder_path)  # Default is to print the file list
            if confirm_file_list():  # If the user confirms the file list
                # Merge all CSV files into a single DataFrame
                merged_df, first_date, last_date = merge_csv_files(folder_path, csv_files)
                
                # Prompt the user to select a date range
                start_date, end_date = get_date_range(first_date, last_date)
                
                # Confirm the date range selection
                if confirm_date_selection(start_date, end_date):
                    # Ask the user which visualization to generate
                    print("Select visualization type to generate:")
                    print("[1] Heatmap")
                    print("[2] Transparent Chart")
                    print("[3] All")
                    print("[4] Consolidated Charts by Behavior")
                    print("[5] Behaviour Mix Chart")
                    print("[6] Weekly Behaviour Heatmaps")
                    choice = input("Enter the number of your choice: ").strip()
                    export_path = create_data_vis_folder()
                    if choice == '1':
                        generate_heatmap(merged_df, selected_folder, "Behavior", export_path, start_date, end_date)
                    elif choice == '2':
                        generate_transparent_chart(merged_df, export_path, start_date, end_date)
                    elif choice == '3':
                        generate_heatmap(merged_df, selected_folder, "Behavior", export_path, start_date, end_date)
                        generate_transparent_chart(merged_df, export_path, start_date, end_date)
                    elif choice == '4':
                        generate_consolidated_by_behavior(
                            merged_df,
                            selected_folder,
                            export_path,
                            start_date,
                            end_date
                        )
                    elif choice == '5':
                        generate_behavior_mix_chart(merged_df, export_path, start_date, end_date)
                    elif choice == '6':
                        generate_weekly_behavior_heatmaps(merged_df, export_path, start_date, end_date)
                        generate_overall_behavior_heatmaps(merged_df, export_path, start_date, end_date)
                    else:
                        print("Invalid choice. No visualization generated.")
                    break  # Exit the main loop after processing user selection
            else:
                continue  # Restart the folder selection process
        else:
            continue  # Restart the folder selection process

# Entry point of the script
if __name__ == "__main__":
    main()
