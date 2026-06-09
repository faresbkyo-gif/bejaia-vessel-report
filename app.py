import streamlit as st
from bejaia_port import get_tables, build_pdf

st.set_page_config(
    page_title="Port of Bejaia",
    layout="wide"
)

st.title("Port of Bejaia Vessel Situation")

st.write(
    "Generate the latest vessel situation report."
)

if st.button("Generate PDF Report"):

    with st.spinner("Fetching vessel data..."):

        tables = get_tables()

        pdf_file = build_pdf(tables)

    st.success("Report generated successfully")

    with open(pdf_file, "rb") as f:

        st.download_button(
            label="Download PDF",
            data=f,
            file_name=pdf_file.name,
            mime="application/pdf"
        )
