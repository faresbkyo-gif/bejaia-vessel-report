import streamlit as st

from scraper import generate_report

st.set_page_config(
    page_title="Port of Bejaia",
    page_icon="🚢",
)

st.title("🚢 Port of Bejaia")

st.write(
    "Generate vessel situation report"
)

if st.button("Generate Report"):

    with st.spinner("Generating PDF..."):

        pdf_file = generate_report()

    with open(pdf_file, "rb") as f:

        st.download_button(
            label="Download PDF",
            data=f,
            file_name=pdf_file.name,
            mime="application/pdf"
        )
