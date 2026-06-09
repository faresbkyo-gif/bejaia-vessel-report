import streamlit as st
from bejaia_port import get_tables, build_pdf

st.title("Port of Bejaia Vessel Situation")

tables = get_tables()

for section, df in tables.items():

    st.subheader(section)

    st.metric(
        "Vessels",
        len(df)
    )

    st.dataframe(
        df,
        use_container_width=True
    )

if st.button("Generate PDF"):

    pdf_file = build_pdf(tables)

    with open(pdf_file, "rb") as f:

        st.download_button(
            "Download PDF",
            f,
            file_name=pdf_file.name,
            mime="application/pdf"
        )
