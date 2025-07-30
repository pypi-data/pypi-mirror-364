#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd

# Reference
# https://docs.kanaries.net/topics/Streamlit/streamlit-upload-file
# https://docs.streamlit.io/develop/api-reference/layout/st.columns
# https://docs.streamlit.io/develop/api-reference/navigation/st.navigation

st.set_page_config(layout="wide")
st.title("SWIFT Payment ISO 20022 Toolbox v1.0")

# Sidebar for navigation
page = st.sidebar.radio(
    "Select a page",
    ("CSV Upload", "XML Upload", "Aggregate Excel Metadata", "Extract XSD Metadata")
)

if page == "CSV Upload":
    st.header("CSV File Upload")
    uploaded_file = st.file_uploader("Upload a CSV file", type=['csv'])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, sep=',')
        data_transpose = data.transpose()
        st.write(data_transpose)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg")
    with col2:
        st.header("A dog")
        st.image("https://static.streamlit.io/examples/dog.jpg")
    with col3:
        st.header("An owl")
        st.image("https://static.streamlit.io/examples/owl.jpg")

elif page == "XML Upload":
    st.header("XML File Upload")
    uploaded_xml = st.file_uploader("Upload an XML file", type=['xml'])
    if uploaded_xml is not None:
        st.write(f"Uploaded file name: {uploaded_xml.name}")
        from swift_iso20022_toolbox import xml_to_xpath
        import tempfile
        import pandas as pd
        import io
        import xlsxwriter

        # Save uploaded file to a temporary file (since xml_to_xpath expects a path)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            tmp_file.write(uploaded_xml.read())
            tmp_file_path = tmp_file.name

        # Parse XML and get results
        results, xsd, msgid, fr, to, credt, bizmsgidr, bizsvc = xml_to_xpath.parse_xml_to_xpath_and_value(tmp_file_path)
        # Prepare DataFrame
        columns = ["XPath", "XPath_strip", "Value", "File Path", "File Name", "XSD", "MsgId", "Fr", "To", "Credt", "BizMsgIdr", "BizSvc"]
        df = pd.DataFrame([
            list(row) + [xsd, msgid, fr, to, credt, bizmsgidr, bizsvc]
            for row in results
        ], columns=columns)
        # Let the user choose which columns to display
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display:",
            options=all_columns,
            default=all_columns
        )
        st.dataframe(df[selected_columns])

        # Download options
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_buffer.getvalue(),
            file_name="xml_xpaths.csv",
            mime="text/csv"
        )
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        st.download_button(
            label="Download as Excel",
            data=excel_buffer.getvalue(),
            file_name="xml_xpaths.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif page == "Aggregate Excel Metadata":
    st.header("Aggregate ISO20022 XSD Compact View (Excel Files)")
    import os
    from swift_iso20022_toolbox import aggregate_metadata
    import tempfile
    import shutil
    # List baseline files
    baseline_dir = os.path.join("data", "sample_xsd_excel_baseline")
    try:
        baseline_files = os.listdir(baseline_dir)
        baseline_files = [f for f in baseline_files if f.endswith('.xlsx')]
    except Exception:
        baseline_files = []

    st.markdown("""
    This feature allows you to aggregate metadata from multiple ISO20022 Swift Payment Messages Excel documentation files.
    """)
    with st.expander("**Baseline:**"):
        st.write("""
          The baseline aggregated file below was produced from the following files in `./data/sample_xsd_excel_baseline`:
        """)
        for f in baseline_files:
            st.markdown(f"- `{f}`")
    st.markdown("""
    - Use the baseline as a reference. Your custom aggregation will NOT overwrite the baseline.
    
    **Custom Aggregation:**
    - Upload your own Excel files below and run aggregation. The result will be saved as `CBPRPlus_SR2025_Metadata_Aggregated_custom.xlsx` and offered as a separate download.
    """)

    # Baseline download
    aggregated_file_path = os.path.join("data", "CBPRPlus_SR2025_Metadata_Aggregated.xlsx")
    if os.path.exists(aggregated_file_path):
        with open(aggregated_file_path, "rb") as f:
            st.download_button(
                label="Download Baseline Aggregated Metadata Excel (CBPRPlus_SR2025 Baseline 15 files)",
                data=f,
                file_name="CBPRPlus_SR2025_Metadata_Aggregated.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No baseline aggregated file found yet.")

    # Custom output download
    custom_agg_file = os.path.join("data", "CBPRPlus_SR2025_Metadata_Aggregated_custom.xlsx")
    if os.path.exists(custom_agg_file):
        with open(custom_agg_file, "rb") as f:
            st.download_button(
                label="Download Custom Aggregated Metadata Excel (your upload)",
                data=f,
                file_name="CBPRPlus_SR2025_Metadata_Aggregated_custom.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    uploaded_excels = st.file_uploader(
        "Upload one or more Excel files for aggregation:",
        type=["xlsx"],
        accept_multiple_files=True
    )
    if uploaded_excels:
        st.write("Uploaded files:")
        for f in uploaded_excels:
            st.write(f.name)
        if st.button("Run Aggregation"):
            with st.spinner("Aggregating metadata..."):
                # Save uploaded files to a temp dir
                with tempfile.TemporaryDirectory() as temp_dir:
                    for file in uploaded_excels:
                        file_path = os.path.join(temp_dir, file.name)
                        with open(file_path, "wb") as out_f:
                            out_f.write(file.read())
                    # Ensure output directory exists
                    os.makedirs("data", exist_ok=True)
                    # Run aggregation, output to custom file
                    try:
                        aggregate_metadata.aggregate_excel_folder(temp_dir)
                        # Move result to ./data/ with custom name
                        if os.path.exists("CBPRPlus_SR2025_Metadata_Aggregated.xlsx"):
                            shutil.move(
                                "CBPRPlus_SR2025_Metadata_Aggregated.xlsx",
                                custom_agg_file
                            )
                        st.success("Custom aggregation complete! Download your result above.")
                    except Exception as e:
                        st.error(f"Aggregation failed: {e}")

elif page == "Extract XSD Metadata":
    st.header("Extract ISO20022 XSD Metadata (XSD Files)")
    import os
    from swift_iso20022_toolbox import extract_xsd_versions
    import tempfile
    import shutil
    # List baseline files
    baseline_dir = os.path.join("data", "sample_xsd_plain_baseline")
    try:
        baseline_files = os.listdir(baseline_dir)
        baseline_files = [f for f in baseline_files if f.endswith('.xsd')]
    except Exception:
        baseline_files = []

    st.markdown("""
    This feature allows you to extract metadata from ISO20022 XSD files and generate a compact Excel reference.
    """)
    with st.expander("**Baseline:**"):
        st.write("""
          The baseline metadata file below was produced from the following files in `./data/sample_xsd_plain_baseline`:
        """)
        for f in baseline_files:
            st.markdown(f"- `{f}`")

    # Baseline download
    baseline_xsd_metadata = os.path.join("data", "CBPRPlus_SR2025_xsd_reference_baseline.xlsx")
    if os.path.exists(baseline_xsd_metadata):
        with open(baseline_xsd_metadata, "rb") as f:
            st.download_button(
                label="Download Baseline XSD Metadata Excel",
                data=f,
                file_name="CBPRPlus_SR2025_xsd_reference_baseline.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No baseline XSD metadata file found yet.")

    # Custom output download
    custom_xsd_metadata = os.path.join("data", "CBPRPlus_SR2025_xsd_reference_custom.xlsx")
    if os.path.exists(custom_xsd_metadata):
        with open(custom_xsd_metadata, "rb") as f:
            st.download_button(
                label="Download Custom XSD Metadata Excel (your upload)",
                data=f,
                file_name="CBPRPlus_SR2025_xsd_reference_custom.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    uploaded_xsds = st.file_uploader(
        "Upload one or more XSD files for metadata extraction:",
        type=["xsd"],
        accept_multiple_files=True
    )
    if uploaded_xsds:
        st.write("Uploaded files:")
        for f in uploaded_xsds:
            st.write(f.name)
        if st.button("Run XSD Metadata Extraction"):
            with st.spinner("Extracting XSD metadata..."):
                # Save uploaded files to a temp dir
                with tempfile.TemporaryDirectory() as temp_dir:
                    for file in uploaded_xsds:
                        file_path = os.path.join(temp_dir, file.name)
                        with open(file_path, "wb") as out_f:
                            out_f.write(file.read())
                    # Ensure output directory exists
                    os.makedirs("data", exist_ok=True)
                    # Run extraction, output to custom file
                    try:
                        extract_xsd_versions.extract_metadata_and_save(temp_dir, 100, custom_xsd_metadata)
                        st.success("Custom XSD metadata extraction complete! Download your result above.")
                    except Exception as e:
                        st.error(f"XSD metadata extraction failed: {e}")

st.sidebar.markdown("---")
st.sidebar.info("You can hide this sidebar using the arrow above.")


def main():
    import os
    import sys

    # Check for our custom flag to avoid streamlit from relaunching
    if os.environ.get("ISO20022_TOOLBOX_RUNNING") == "1":
        print("DEBUG: Already running, not launching subprocess")
        return

    # Only launch streamlit if not already running as a Streamlit script
    if not any("streamlit" in arg for arg in sys.argv[0:2]) and not any(k.startswith("STREAMLIT") for k in os.environ):
        script_path = os.path.abspath(__file__)
        print("DEBUG: Launching streamlit run", script_path)
        # Set the flag for the subprocess
        env = os.environ.copy()
        env["ISO20022_TOOLBOX_RUNNING"] = "1"
        import subprocess
        subprocess.run(["streamlit", "run", script_path], env=env)
    else:
        print("DEBUG: Not launching subprocess")

if __name__ == "__main__":
    main()
