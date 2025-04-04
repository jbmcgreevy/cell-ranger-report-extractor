# cell-ranger-report-extractor

A tool to extract basic quality-control data from 10x Cell Ranger HTML files and add it to a new spreadsheet.

## Features

- **HTML Parsing**: Uses BeautifulSoup to parse HTML files.
- **JSON Extraction**: Extracts JSON data embedded within `<script>` tags in the HTML.
- **Data Extraction**: Retrieves specific metrics from the JSON data.
- **File Processing**: Processes multiple HTML files from the `input-files` directory.
- **Output**: Saves the extracted data into CSV and Excel files.

## How It Works

1. **Extract JSON**: The `extract_json` function locates and extracts JSON data from a script tag in the HTML content.
2. **Extract Data from HTML**: The `extract_data_from_html` function sanitizes the file path, parses the HTML, extracts the JSON, and retrieves specific metrics.
3. **Get Metric Value**: The `get_metric_value` function searches for a specific metric in the JSON data and returns its value.
4. **Process Files**: The script processes all HTML files in the `input-files` directory, extracts the required data, and appends it to a list.
5. **Save Output**: The extracted data is saved into CSV and Excel files named `output.csv` and `output.xlsx`.

## Usage

1. Place your HTML files in the `input-files` directory.
2. Run the script.
```bash
    # Run the script
    python cellRangerReportExtractor.py
```
3. The script will generate `output.csv` and `output.xlsx` in the current directory.

## Dependencies

- BeautifulSoup
- pandas
- glob
- json
- re
- os