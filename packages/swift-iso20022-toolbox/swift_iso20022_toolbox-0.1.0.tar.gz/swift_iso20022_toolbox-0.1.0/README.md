# SWIFT Payment ISO 20022 Toolbox

## Overview

This project is a Streamlit-based web application for uploading, analyzing, and aggregating payment files and schemas in the context of SWIFT ISO 20022 standards. It provides a multi-tool GUI for:
- Uploading and viewing CSV and XML files
- Aggregating metadata from Excel documentation files
- Extracting metadata from XSD schema files

The toolbox is designed for maintainability, transparency, and extensibility, supporting both baseline reference data and user-driven custom analysis.

---

## Features

### 1. CSV Upload
- Upload a CSV file and view its transposed content.

### 2. XML Upload
- Upload an ISO 20022 XML file.
- Extracts all XPaths, values, and relevant ISO 20022 metadata (MsgId, BizMsgIdr, etc.).
- Lets you select which columns to display.
- Download extracted data as CSV or Excel.

### 3. Aggregate Excel Metadata
- Aggregate metadata from multiple ISO20022 Swift Payment Messages Excel documentation files.
- Download a **baseline** aggregated file (produced from files in `./data/sample_xsd_excel_baseline`).
- Upload your own Excel files for custom aggregation and download the result.
- Baseline is never overwritten.

### 4. Extract XSD Metadata
- Extracts structured metadata from XSD files in a directory and exports the results to Excel.
- Download a **baseline** XSD metadata file (from `./data/sample_xsd_plain_baseline`).
- Upload your own `.xsd` files for custom extraction and download the result.
- Baseline is never overwritten.

---

## How to Use

### 1. Install Requirements

Python 3.7+ is recommended. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the App

From your project directory:
```bash
streamlit run iso20022_toolbox.py
```

### 3. Using the GUI
- Select the desired tool/page from the sidebar menu.
- Follow on-screen instructions for uploading files and downloading results.
- Baseline reference files are always available for download.

---

## Script Descriptions

### `extract_xsd_versions.py`
```
XSD Metadata Extractor
---------------------
Extracts structured metadata from XSD files in a directory and exports the results to CSV and XLSX formats.

Features:
- Parametrized input directory (`--folder`) and number of header lines to scan (`--lines`).
- Extracts fields such as Group, Collection, Usage Guideline, Base Message, Date of publication, URL, <xs:schema ...> tag, and more.
- Outputs a reference DataFrame and saves as both CSV and Excel.
```

### `xml_to_xpath.py`
```
ISO20022 XML XPath Extractor
---------------------------
Parses ISO 20022 XML files and extracts all XPaths, values, and key metadata (XSD, MsgId, AppHdr fields, etc.).
Supports CSV/Excel export for downstream analysis.
```

---

## Requirements
- streamlit
- pandas
- openpyxl
- xlsxwriter

(See `requirements.txt` for the full list.)

---

## Notes
- Baseline reference files are never overwritten by user uploads.
- All features are accessible from the sidebar menu.
- The toolbox is modular and easy to extend for new analysis or conversion tools.

For more information, see the docstrings in each script or contact the project maintainer.
