Here's an updated and combined documentation for both `fpMaker(individuals_combine_activity.py)` and `fpMaker(individuals_each_behaviours.py)`:

---

# **Documentation for `fpMaker` Scripts**

This documentation covers the two scripts:
1. `fpMaker(individuals_combine_activity.py)` - Focuses on combining activity data across multiple files.
2. `fpMaker(individuals_each_behaviours.py)` - Focuses on analyzing behaviors per individual hub and generating more granular visualizations.

---

## **Overview**
Both scripts process and visualize behavioral data stored in CSV files. They aim to simplify data analysis through heatmaps and consolidated charts, with customizable options for date ranges and behavior-specific visualizations.

---

## **Shared Features**

### Folder and File Handling
- Lists and allows selection of folders containing data files.
- Merges multiple CSV files into a single DataFrame.
- Validates selections for proper user flow.

### Data Preprocessing
- Handles duplicate columns and standardizes column names.
- Extracts and parses timestamps into dates and times for easy manipulation.

### Date Range Selection
- Provides the earliest and latest available dates in the dataset for user input.
- Validates the selected range to ensure correctness.

### Visualization Export
- Automatically creates timestamped directories for saving charts.
- Generates visualizations tailored to user needs and exports them as PNG files.

---

## **Script-Specific Features**

### **1. `fpMaker(individuals_combine_activity.py)`**

This script combines data across files and focuses on creating general visualizations like:
- Heatmaps for behavioral data aggregated over half-hour intervals.
- Consolidated charts showing hourly activity across selected dates.
- Styled and transparent consolidated charts for presentation purposes.

**Key Functions**:
- `generate_heatmap()`: Creates heatmaps with weekday and time granularity.
- `generate_consolidated_chart()`: Produces basic hourly activity charts.
- `generate_styled_consolidated_chart()`: Offers visually enhanced charts with spacing, rounded corners, and custom color schemes.

---

### **2. `fpMaker(individuals_each_behaviours.py)`**

This script analyzes behaviors for each hub or device and generates individual charts. It includes:
- Heatmaps for specific hubs and behaviors.
- Transparent charts for behavior data, suitable for overlaying on other visualizations.
- Per-hub and per-behavior visualizations to provide granular insights.

**Key Functions**:
- `generate_transparent_chart()`: Produces charts with transparency, focusing on individual hubs and behaviors.
- `analyze_and_generate_transparent_charts_per_hub_and_behavior()`: Loops through hubs and behaviors to generate separate visualizations for each.

---

## **Recommended Setup Using `venv`**

To ensure a clean and reproducible environment, it is recommended to use Python's `venv` module for managing dependencies.

### Steps:
1. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install pandas matplotlib seaborn numpy
   ```

4. **Save Dependencies**
   ```bash
   pip freeze > requirements.txt
   ```

5. **Run the Scripts**
   ```bash
   python fpMaker(individuals_combine_activity.py)
   python fpMaker(individuals_each_behaviours.py)
   ```

6. **Deactivate the Virtual Environment**
   ```bash
   deactivate
   ```

---

## **Input and Output**

### **Input**
- CSV files with behavioral data. Ensure the following columns are included:
  - `Timestamp`
  - `Hub Name` (for `individuals_each_behaviours.py`)
  - `Behavior Name` (for behavior-specific visualizations)
  - `Button ID` (for aggregated counts)

### **Output**
- Heatmaps and consolidated charts saved in a timestamped directory under `data_output`.

---

## **Execution**

1. Place your CSV files in the `data_input` folder.
2. Run either script, following the on-screen prompts for:
   - Selecting a folder.
   - Confirming files.
   - Choosing a date range.
3. Visualizations will be saved in `data_output`.

---

## **Dependencies**

- `os`
- `pandas`
- `matplotlib`
- `seaborn`
- `numpy`
- `datetime`

Install required libraries using:
```bash
pip install pandas matplotlib seaborn numpy
```

---

## **Advanced Features**

### **1. Heatmaps**
- Aggregates data over half-hour intervals and displays activity intensity.

### **2. Consolidated Charts**
- Basic and styled options are available, offering flexibility for presentations.

### **3. Per-Hub and Behavior-Specific Charts**
- Unique to `fpMaker(individuals_each_behaviours.py)`, these charts are ideal for granular analysis.

---

By leveraging these scripts, users can efficiently analyze and visualize behavioral data across multiple dimensions, making them valuable tools for data-driven insights.
