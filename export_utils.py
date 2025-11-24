# export_utils.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import os
from data_processing import get_dataframe, weekly_summary

def generate_pdf_report(path="habit_report.pdf"):
    """
    Simple PDF containing last 7 logs and a short summary.
    Requires reportlab.
    """
    df = get_dataframe()
    if df.empty:
        raise ValueError("No data to create report.")
    # create a temporary pdf
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, "Smart Habit & Productivity Report")
    c.setFont("Helvetica", 10)
    last7 = df.tail(7)[["date", "sleep_hours", "study_hours", "productivity_score"]]
    y = height - 80
    c.drawString(40, y, "Last 7 Days:")
    y -= 16
    for _, r in last7.iterrows():
        line = f"{r['date'].date()}  | sleep: {r['sleep_hours']}h  | study: {r['study_hours']}h  | score: {r['productivity_score']}"
        c.drawString(40, y, line)
        y -= 12
        if y < 80:
            c.showPage()
            y = height - 40
    # simple weekly summary
    ws = weekly_summary(df).reset_index().tail(4)
    c.showPage()
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 50, "Weekly Summary (last 4 weeks):")
    c.setFont("Helvetica", 10)
    y = height - 80
    for _, r in ws.iterrows():
        line = f"Week: {r['date'].date()} | avg sleep: {r['sleep_hours']} | total study: {r['study_hours']} | avg score: {r['productivity_score']}"
        c.drawString(40, y, line)
        y -= 14
    c.save()
    return os.path.abspath(path)
