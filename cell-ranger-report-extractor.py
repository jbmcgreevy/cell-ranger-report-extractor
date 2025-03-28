from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import glob
import json
import re
import os

class CellRangerReportExtractor:

    def extract_json(script_content):
        start_marker = "const data = {"
        end_marker = '}],"_resources":{}}'  # This marks the end of the JSON

        start_index = script_content.find(start_marker)
        if start_index == -1:
            print("Could not find 'const data = {' in the script tag.")
            return None

        start_index += len("const data = ")  # Move past 'const data = ' to start at '{'

        # Find the exact end of JSON
        end_index = script_content.find(end_marker, start_index)
        if end_index == -1:
            print("Could not find the end marker of the JSON.")
            return None

        end_index += len(end_marker)  # Include the last '}}'

        return script_content[start_index:end_index]

    # Function to extract required data
    def extract_data_from_html(file_path):
        # Sanitize file path
        file_path = os.path.abspath(file_path)
        if not file_path.startswith(os.path.abspath("input-files")):
            print(f"Invalid file path: {file_path}")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Extract JSON blob from <script> tag
        script_tag = soup.find("script", string=re.compile("const data ="))

        # Default values
        extracted_data = {
            "Run ID": "Unknown",
            "Sample ID": "Unknown",
            "Total Singlets": "Unknown",
            "Confidently Mapped Reads in Cells": "Unknown",
            "Median Genes Per Singlet": "Unknown",
            "Median UMI Per Singlet": "Unknown",
            "Total Genes Detected": "Unknown",
            "Reads From Cells Assigned to Sample": "Unknown"
        }

        if script_tag:
            print("found script")
            # Extract JSON safely
            json_string = CellRangerReportExtractor.extract_json(script_tag.string)

            if json_string:
                try:
                    json_data = json.loads(json_string)
                    extracted_data["Run ID"] = json_data.get("library", {}).get("data", {}).get("header_info", {}).get("Run ID", "Unknown")
                    extracted_data["Sample ID"] = json_data.get("sample", {}).get("id", "Unknown")
                    extracted_data["Total Singlets"] = CellRangerReportExtractor.get_metric_value(json_data, "total_singlets")
                    extracted_data["Confidently Mapped Reads in Cells"] = CellRangerReportExtractor.get_metric_value(json_data, "confidently_mapped_reads_in_cells")
                    extracted_data["Median Genes Per Singlet"] = CellRangerReportExtractor.get_metric_value(json_data, "median_genes_per_singlet")
                    extracted_data["Median UMI Per Singlet"] = CellRangerReportExtractor.get_metric_value(json_data, "median_umi_per_singlet")
                    extracted_data["Total Genes Detected"] = CellRangerReportExtractor.get_metric_value(json_data, "total_genes_detected")
                    extracted_data["Reads From Cells Assigned to Sample"] = CellRangerReportExtractor.get_metric_value(json_data, "reads_from_cells_assigned_to_sample")
                    print("Successfully parsed JSON!")
                except json.JSONDecodeError as e:
                    print("JSON parsing error:", e)
            else:
                print("Failed to extract JSON.")

        return extracted_data

    def get_metric_value(json_obj, key_name):
        """Search for a metric by key and return its value."""
        if "per_sample" in json_obj and isinstance(json_obj["per_sample"], list):
            sample_data = json_obj["per_sample"][0]  # First sample

            # Ensure metrics exist and are a list
            if "metrics" in sample_data and isinstance(sample_data["metrics"], list):
                for metric in sample_data["metrics"]:
                    if metric.get("key") == key_name:
                        return metric.get("value", "Unknown")  # Return value or "Unknown" if missing
        
        return "Not Found"  # Return if key is not found

# Process multiple HTML files (including subfolders)
data_list = []
html_files = glob.glob("input-files/*.html", recursive=False)

for file in html_files:
    data = CellRangerReportExtractor.extract_data_from_html(file)
    if data:
        data_list.append(data)

# Convert to DataFrame and Save
current_date = datetime.now().strftime("%m-%d-%Y")

# Ensure the output directory exists
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

df = pd.DataFrame(data_list)
df.to_csv(os.path.join(output_dir, f"cell-ranger-stats-{current_date}.csv"), index=False)
df.to_excel(os.path.join(output_dir, f"cell-ranger-stats-{current_date}.xlsx"), index=False)

print("Data extraction complete. Saved as output.csv and output.xlsx.")