"""
Port of Bejaia - Vessel Situation PDF Report
--------------------------------------------

Requirements:

pip install requests beautifulsoup4 pandas reportlab lxml

Output:
    reports/Bejaia_Vessel_Situation_YYYY-MM-DD.pdf

"""

from pathlib import Path
from datetime import datetime

import requests
import pandas as pd
from bs4 import BeautifulSoup

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)


# ============================================================
# CONFIG
# ============================================================

URL = "https://www.portdebejaia.dz/situation-des-navires/"

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)

COMPANY_NAME = "PORT OF BEJAIA"
REPORT_TITLE = "VESSEL SITUATION REPORT"

# ============================================================
# SCRAPER
# ============================================================

def clean(txt):
    return " ".join(str(txt).strip().split())


def get_tables():

    response = requests.get(
        URL,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64)"
            )
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    tables = soup.select("table.datatable")

    table_names = [
        "Expected Arrivals",
        "Alongside",
        "Anchorage",
        "Car Ferries",
    ]

    result = {}

    for name, table in zip(table_names, tables):

        headers = [
            clean(th.get_text())
            for th in table.select("thead th")
        ]

        rows = []

        for tr in table.select("tbody tr"):

            row = []

            for td in tr.find_all("td"):
                row.append(clean(td.get_text(" ", strip=True)))

            if row:
                rows.append(row)

        result[name] = pd.DataFrame(
            rows,
            columns=headers
        )

    return result


# ============================================================
# PDF UTILITIES
# ============================================================

def build_pdf(tables):

    now = datetime.now()

    filename = (
        OUTPUT_DIR /
        f"Bejaia_Vessel_Situation_{now:%Y-%m-%d}.pdf"
    )

    doc = SimpleDocTemplate(
        str(filename),
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0B3D91")
    )

    subtitle_style = ParagraphStyle(
        "SubTitle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444")
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading1"],
        textColor=colors.HexColor("#0B3D91")
    )

    elements = []

    # ========================================================
    # COVER PAGE
    # ========================================================

    elements.append(
        Paragraph(COMPANY_NAME, title_style)
    )

    elements.append(
        Paragraph(REPORT_TITLE, title_style)
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Generated on {now:%d/%m/%Y %H:%M}",
            subtitle_style
        )
    )

    elements.append(Spacer(1, 30))

    total_expected = len(
        tables.get("Expected Arrivals", pd.DataFrame())
    )

    total_alongside = len(
        tables.get("Alongside", pd.DataFrame())
    )

    total_anchor = len(
        tables.get("Anchorage", pd.DataFrame())
    )

    total_ferries = len(
        tables.get("Car Ferries", pd.DataFrame())
    )

    summary = f"""
    <b>Expected Arrivals:</b> {total_expected}<br/>
    <b>Alongside:</b> {total_alongside}<br/>
    <b>At Anchorage:</b> {total_anchor}<br/>
    <b>Car Ferries:</b> {total_ferries}
    """

    elements.append(
        Paragraph(summary, styles["BodyText"])
    )

    elements.append(PageBreak())

    # ========================================================
    # TABLE SECTIONS
    # ========================================================

    for section_name, df in tables.items():

        elements.append(
            Paragraph(section_name, section_style)
        )

        elements.append(Spacer(1, 10))

        if df.empty:

            elements.append(
                Paragraph(
                    "No data available.",
                    styles["BodyText"]
                )
            )

            elements.append(PageBreak())
            continue

        pdf_data = [list(df.columns)]

        for _, row in df.iterrows():
            pdf_data.append(
                [str(x) for x in row.tolist()]
            )

        ncols = len(df.columns)

        page_width = 760

        col_widths = [
            page_width / ncols
        ] * ncols

        table = Table(
            pdf_data,
            repeatRows=1,
            colWidths=col_widths
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#0B3D91")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.whitesmoke,
                        colors.lightgrey
                    ]
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
            ])
        )

        elements.append(table)
        elements.append(PageBreak())

    # ========================================================
    # FOOTER
    # ========================================================

    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.drawRightString(
            800,
            15,
            f"Page {page_num}"
        )

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    return filename


# ============================================================
# MAIN
# ============================================================

def main():

    print("Fetching vessel situation...")

    tables = get_tables()

    print()

    for name, df in tables.items():
        print(
            f"{name:<20} : {len(df):>4} rows"
        )

    pdf_file = build_pdf(tables)

    print()
    print(f"PDF generated: {pdf_file}")


if __name__ == "__main__":
    main()
