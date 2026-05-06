import json
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date
from PIL import Image as PILImage

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from app.db import run_select

OUT_DIR = Path("exports")
OUT_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo_dreptunghic.png")
LOGO_PREPARED_PATH = OUT_DIR / "_logo_prepared.png"

PINK_DARK = "#8B2252"
PINK_MID = "#C2185B"
PINK_HEADER_BG = "#880E4F"
PINK_LIGHT = "#F8BBD0"
PINK_GRID = "#E91E8C"
PINK_PIE = ["#880E4F", "#AD1457", "#C2185B", "#D81B60", "#E91E63", "#F06292"]


def normalize(v):
    if isinstance(v, Decimal):
        x = float(v)
        return int(x) if x.is_integer() else x
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v


def get_reports_config():
    return {
        "abonamente_2026": {
            "title": "Abonamente Active in 2026",
            "table_name": "Abonamente",
            "sql": (
                "SELECT s.Tip_pilates as Eticheta, COUNT(a.ID_abonament) as Valoare "
                "FROM Abonamente a JOIN Sesiuni s ON a.fk_idSesiuneA = s.ID_sesiune "
                "WHERE a.Activ = 'DA' GROUP BY s.Tip_pilates"
            ),
            "columns": ["Tip Sesiune", "Nr. Abonamente"],
            "chart_type": "bar",
        },
        "top_echipamente": {
            "title": "Top Echipamente cu Starea 'Conform'",
            "table_name": "Echipamente",
            "sql": (
                "SELECT Denumire as Eticheta, COUNT(ID_echipament) as Valoare "
                "FROM Echipamente WHERE Stare_echipament = 'conform' "
                "GROUP BY Denumire ORDER BY Valoare DESC"
            ),
            "columns": ["Echipament", "Unitati"],
            "chart_type": "pie",
        },
        "programari_2026": {
            "title": "Top Programari Confirmate in 2026",
            "table_name": "Programari",
            "sql": (
                "SELECT COALESCE(s.Tip_pilates, 'Sesiune Nespecificată') as Eticheta, COUNT(p.ID_programare) as Valoare "
                "FROM Programari p "
                "LEFT JOIN Sesiuni s ON p.fk_idSesiunePr = s.ID_sesiune "
                "WHERE p.Status_confirmare = 'confirmata' "
                "AND YEAR(p.Data_si_ora) = 2026 "
                "GROUP BY s.Tip_pilates "
                "ORDER BY Valoare DESC"
            ),
            "columns": ["Tip Sesiune", "Nr. Confirmari"],
            "chart_type": "line",
        },
    }

def prepare_logo():
    if not LOGO_PATH.exists():
        return None
    if LOGO_PREPARED_PATH.exists():
        return LOGO_PREPARED_PATH
    img = PILImage.open(str(LOGO_PATH)).convert("RGBA")
    background = PILImage.new("RGBA", img.size, (255, 255, 255, 255))
    background.paste(img, mask=img.split()[3])
    background.convert("RGB").save(str(LOGO_PREPARED_PATH), "PNG")
    return LOGO_PREPARED_PATH


def get_logo_image(width_inch=1.5):
    logo_path = prepare_logo()
    if logo_path:
        return Image(str(logo_path), width=width_inch * inch, height=width_inch * inch)
    return None

def fetch_data(sql):
    rows = run_select(sql)
    return [{"label": normalize(r[0]), "value": normalize(r[1])} for r in rows]


def export_csv(report_id, data, columns):
    path = OUT_DIR / f"{report_id}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for d in data:
            writer.writerow([d["label"], d["value"]])


def export_json(report_id, data):
    path = OUT_DIR / f"{report_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_chart(report_id, data, title, chart_type):
    labels = [str(d["label"]) for d in data]
    values = [d["value"] for d in data]
    path = OUT_DIR / f"{report_id}_chart.png"
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("#FFF0F5")
    ax.set_facecolor("#FFF0F5")
    if chart_type == "bar":
        bars = ax.bar(labels, values, color=PINK_DARK, edgecolor=PINK_MID)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(int(bar.get_height())),
                    ha='center', va='bottom', color=PINK_DARK, fontweight='bold')
    elif chart_type == "line":
        ax.plot(labels, values, marker="o", color=PINK_DARK, linewidth=2.5)
        ax.fill_between(range(len(labels)), values, alpha=0.15, color=PINK_DARK)
    elif chart_type == "pie":
        ax.pie(values, labels=labels, colors=PINK_PIE, autopct="%1.1f%%", startangle=140)
    ax.set_title(title, fontsize=14, color=PINK_HEADER_BG, fontweight="bold", pad=20)
    if chart_type != "pie":
        plt.xticks(rotation=45, ha="right", color=PINK_HEADER_BG, fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.3, color=PINK_GRID)
    plt.tight_layout()
    plt.savefig(str(path), dpi=150)
    plt.close()
    return path

def generate_pdf(report_id, data, config, chart_path):
    pdf_path = OUT_DIR / f"{report_id}.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, topMargin=0.5 * inch)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="TitleStyle", parent=styles["Heading1"], fontSize=20,
        textColor=colors.HexColor(PINK_HEADER_BG), alignment=0
    )
    logo_width = 3.7 * inch
    logo_height = 1.2 * inch
    if LOGO_PATH.exists():
        logo_img = Image(str(LOGO_PATH), width=logo_width, height=logo_height)
        logo_img.hAlign = 'CENTER'
        elements.append(logo_img)
        elements.append(Spacer(1, 10))
    title_para = Paragraph(config["title"], title_style)
    elements.append(title_para)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor(PINK_MID), spaceAfter=15))
    info_text = (
        f"Raportul generat reprezinta o resursa folositoare in analiza in adancime "
        f"a performantelor firmei in anul 2026. Acesta este focusat pe datele "
        f"apartinand tabelului <b>{config['table_name']}</b>. "
        f"Raportul a fost generat la data de <b>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</b>."
    )
    elements.append(Paragraph(info_text, styles["Normal"]))
    elements.append(Spacer(1, 20))
    table_data = [config["columns"]] + [[str(d["label"]), str(d["value"])] for d in data]
    tbl = Table(table_data, colWidths=[doc.width * 0.7, doc.width * 0.25])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PINK_HEADER_BG)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(PINK_MID)),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(PINK_LIGHT)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tbl)
    if chart_path and chart_path.exists():
        elements.append(Spacer(1, 30))
        elements.append(Image(str(chart_path), width=6 * inch, height=3.5 * inch))
    doc.build(elements)


def main():
    configs = get_reports_config()
    for r_id, config in configs.items():
        print(f"Generare: {config['title']}...")
        data = fetch_data(config["sql"])
        if data:
            export_csv(r_id, data, config["columns"])
            export_json(r_id, data)
            c_path = generate_chart(r_id, data, config["title"], config["chart_type"])
            generate_pdf(r_id, data, config, c_path)
        else:
            print(f"Nu s-au gasit date pentru {r_id}.")


if __name__ == "__main__":
    main()