"""
XSD Metadata Extractor
---------------------
Extracts structured metadata from XSD files in a directory and exports the results to CSV and XLSX formats.

Features:
- Parametrized input directory (`--folder`) and number of header lines to scan (`--lines`).
- Extracts the following fields from each XSD file:
    - Group
    - Collection
    - Usage Guideline
    - Base Message
    - Date of publication
    - URL
    - <xs:schema ...> tag (full tag, wherever it appears)
    - xs_schema_xsd: the value between ':xsd:' and the next double-quote in the schema tag
- Outputs a reference DataFrame and saves it as both `xsd_reference.csv` and `xsd_reference.xlsx`.

Requirements:
- Python 3.7+
- pandas
- openpyxl (for Excel export)

Usage Example:
    python extract_xsd_versions.py --folder ./sample_xsd_plain --lines 100
"""
import os
import re
import pandas as pd
import argparse

# Fields to extract and their regex patterns
FIELDS = {
    'group': re.compile(r'^Group:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    'collection': re.compile(r'^Collection:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    'usage_guideline': re.compile(r'^Usage Guideline:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    'base_message': re.compile(r'^Base Message:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    'date_of_publication': re.compile(r'^Date of publication:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
    'url': re.compile(r'^URL:\s*(.+)$', re.MULTILINE | re.IGNORECASE),
}

def extract_metadata_from_xsd(folder: str = './sample_xsd_plain', n_lines: int = 100):
    records = []
    xs_schema_pattern = re.compile(r'<xs:schema[^>]*>', re.IGNORECASE)
    for fname in os.listdir(folder):
        if fname.lower().endswith('.xsd'):
            file_path = os.path.join(folder, fname)
            # Read first n_lines for metadata
            with open(file_path, encoding='utf-8', errors='replace') as f:
                lines = [next(f) for _ in range(n_lines)]
                content = ''.join(lines)
            record = {'file_name': fname}
            for key, pattern in FIELDS.items():
                match = pattern.search(content)
                record[key] = match.group(1).strip() if match else None
            # Try to find the <xs:schema ...> tag in first n_lines
            schema_line = None
            for line in lines:
                match = xs_schema_pattern.search(line)
                if match:
                    schema_line = match.group(0)
                    break
            # Fallback: if not found, read the whole file and try again
            if not schema_line:
                try:
                    with open(file_path, encoding='utf-8', errors='replace') as f:
                        file_content = f.read()
                except Exception:
                    file_content = ''
                match = xs_schema_pattern.search(file_content)
                if match:
                    schema_line = match.group(0)
            record['xs_schema_tag'] = schema_line
            records.append(record)
    df = pd.DataFrame(records)
    # Extract xs_schema_xsd from xs_schema_tag
    def extract_xsd(tag):
        if not tag:
            return None
        match = re.search(r':xsd:([^\"]+)', tag)
        return match.group(1) if match else None
    df.insert(0, 'xs_schema_xsd', df['xs_schema_tag'].apply(extract_xsd))
    return df

def extract_metadata_and_save(folder: str, n_lines: int, output_path: str):
    ref_df = extract_metadata_from_xsd(folder, n_lines)
    ref_df.to_excel(output_path, index=False)
    return ref_df

def main():
    parser = argparse.ArgumentParser(description="Extract metadata from XSD files.")
    parser.add_argument('--folder', type=str, default='./sample_xsd_plain', help='Folder containing XSD files')
    parser.add_argument('--lines', type=int, default=40, help='Number of header lines to read from each XSD file')
    parser.add_argument('--output', type=str, default='xsd_reference.xlsx', help='Output Excel file path')
    args = parser.parse_args()

    ref_df = extract_metadata_and_save(args.folder, args.lines, args.output)
    print(ref_df)
    ref_df.to_csv('xsd_reference.csv', index=False)

if __name__ == "__main__":
    main()

# Optionally, save to CSV:
# ref_df.to_csv('xsd_reference.csv', index=False)
