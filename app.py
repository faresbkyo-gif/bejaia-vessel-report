import streamlit as st
import requests
from bs4 import BeautifulSoup

URL = "https://www.portdebejaia.dz/situation-des-navires/"

st.set_page_config(
    page_title="Bejaia Port Debug",
    layout="wide"
)

st.title("Port of Bejaia - Connection Test")

if st.button("Test Website Access"):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/"
    }

    try:

        with st.spinner("Connecting..."):

            response = requests.get(
                URL,
                headers=headers,
                timeout=30
            )

        st.success("Request completed")

        st.subheader("Status Code")
        st.code(response.status_code)

        st.subheader("Response Headers")
        st.json(dict(response.headers))

        st.subheader("First 3000 Characters")
        st.text(response.text[:3000])

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        tables = soup.find_all("table")

        st.subheader("Tables Found")
        st.write(len(tables))

        if tables:
            st.success(
                f"Found {len(tables)} table(s)"
            )
        else:
            st.warning(
                "No tables detected"
            )

    except Exception as e:

        st.error("Exception occurred")

        st.code(str(e))
