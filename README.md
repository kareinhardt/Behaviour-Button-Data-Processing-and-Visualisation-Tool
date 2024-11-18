# **Behaviour Button Data Processing and Visualisation Tool**

## **Overview**
This project, developed by the NICA Design Team with the assistance of GPT-4, is tailored for the **Voice® November Pilot 2024** study. While it has been tested with the pilot data, it may contain logical errors and is intended for internal use only.

The tool simplifies data processing, analysis, and visualisation, primarily to support the **Design** and **Insight** teams in generating reports for **Voice® Member feedback** and preparing project documentation. It automates repetitive tasks, provides insights into behavioural patterns, and creates detailed visualisations that facilitate impactful reporting.

---

## **Installation Instructions**

### 1. Set Up a Virtual Environment (Recommended)
- **Windows**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 2. Install Required Dependencies
Run the following command to install dependencies:
```bash
pip install pandas matplotlib numpy
```

### 3. Prepare the Directory Structure
Ensure the following folder structure is in place:
- **`data_input/`**: Subfolders containing CSV data files.
- **`data_output/`**: Folder for the merged data and visualisation outputs.
- Place the Python scripts (`chartmaker.py`, `mergecsv.py`, `factsfinder.py`) in the root directory.

---

## **File Descriptions**

### 1. `chartmaker.py`
- **Purpose**: Generates heatmaps from the pilot study data.
- **Input**:
  - CSV format: `"Timestamp", "Hub Name", "Behaviour Name", "Button ID"`.
  - Merged dataset created by `mergecsv.py`.
- **Output**:
  - Heatmaps saved as PNG files in the `data_output/` folder.

### 2. `mergecsv.py`
- **Purpose**: Merges multiple pilot study CSV files into one dataset.
- **Input**:
  - Subfolder in `data_input/` containing multiple CSV files in the specified format.
- **Output**:
  - Merged CSV file saved in `data_output/`.
  - Provides date range (`Timestamp`) and entry statistics.

### 3. `factsfinder.py`
- **Purpose**: Provides insights into the merged dataset.
- **Features**:
  - Counts total entries per `Hub Name` and `Behaviour Name`.
  - Identifies the most frequent behaviours.
- **Input**:
  - Merged CSV file in the required format.
- **Output**:
  - Console output summarising data insights.

---

## **Usage Instructions**

### **Step 1: Prepare Input Data**
1. Organise data in subfolders within the `data_input/` folder.
2. Ensure CSV files follow the format:
   ```csv
   "Timestamp","Hub Name","Behaviour Name","Button ID"
   ```

### **Step 2: Merge Data**
1. Run `mergecsv.py`:
   ```bash
   python mergecsv.py
   ```
2. Select the appropriate subfolder containing the CSV files.
3. Confirm your selection to merge the files.

### **Step 3: Analyse Data**
1. Run `factsfinder.py`:
   ```bash
   python factsfinder.py
   ```
2. Select the merged CSV file folder.
3. Specify the desired date range (`Timestamp`) for analysis.
4. Review the output in the console.

### **Step 4: Generate Heatmaps**
1. Run `chartmaker.py`:
   ```bash
   python chartmaker.py
   ```
2. Select the dataset and options as prompted.
3. Heatmaps will be saved in the `data_output/` folder as PNG files.

---

## **Output Details**

### **Merged CSV File**
- Saved in `data_output/` with a timestamped filename, e.g., `merged_file_on_YYYY-MM-DD_HH-MM-SS.csv`.

### **Data Analysis**
- Console output includes:
  - Total entries per `Hub Name`.
  - Entries per `Behaviour Name`.
  - Most frequent behaviours per hub.

### **Visualisations**
- Heatmaps illustrate behavioural patterns and trends, saved as PNG files in `data_output/`.

---

## **Recommendations**
- Use a virtual environment (`venv`) to avoid dependency conflicts.
- Ensure CSV files adhere strictly to the format:
  ```csv
  "Timestamp","Hub Name","Behaviour Name","Button ID"
  ```
- Organise files in the `data_input/` folder for streamlined processing.

---

## **Troubleshooting**

### Common Issues
1. **No CSV Files Found**:
   - Verify that `.csv` files are in the correct subfolder within `data_input/`.
2. **Date Parsing Errors**:
   - Ensure the `Timestamp` column is formatted as `YYYY-MM-DD HH:MM:SS`.
3. **Missing Columns**:
   - Check that columns match the specified format exactly.

---

## **License and Author Info**
- **Author**: NICA Design Team (with GPT-4 assistance)
- **License**: Restricted to NICA's internal use for the Behaviour Button Public Pilot study.
