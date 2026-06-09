from pathlib import Path
from datetime import datetime

import requests
import pandas as pd
from bs4 import BeautifulSoup

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)

from reportlab.lib.styles import getSampleStyleSheet

URL = "https://www.portdebejaia.dz/situation-des-navires/"


def get_tables():

    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    if response.status_code != 200:
    raise Exception(
        f"Status code: {response.status_code}"
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    tables = soup.select("table.datatable")

    return len(tables)


def build_pdf():

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    filename = (
        reports_dir /
        f"report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    )

    doc = SimpleDocTemplate(str(filename))

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Port of Bejaia Vessel Situation Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Generated: {datetime.now()}",
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Tables found: {get_tables()}",
            styles["BodyText"]
        )
    )

    doc.build(elements)

    return filename


def generate_report():
    return build_pdf()
