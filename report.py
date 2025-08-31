# -*- coding: utf-8 -*-

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# function
def generate_report_pdf(output_path: str, data: dict, charts: dict = None):
 
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 2*cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, "Smart Resume Parser Report")
    y -= 1.2*cm

    c.setFont("Helvetica", 11)

    # pull key-value pairs
    def draw_kv(k, v):
        nonlocal y

        if y < 3*cm:
            c.showPage()
            y = height - 2*cm
            c.setFont("Helvetica", 11)
        c.drawString(2*cm, y, f"{k}: {v}")
        y -= 0.7*cm

    # draw candidate information
    draw_kv("Name", data.get("Name") or "-")
    draw_kv("Email", data.get("Email") or "-")
    draw_kv("Phone", data.get("Phone") or "-")
    draw_kv("Experience (years)", data.get("ExperienceYears") or "-")
    draw_kv("Skills", ", ".join(data.get("Skills") or []) or "-")
    draw_kv("Education", "; ".join(data.get("Education") or []) or "-")

    # ATS 
    ats = data.get("ATS", {})
    if ats:
        y -= 0.3*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, "ATS Match")
        y -= 0.8*cm
        c.setFont("Helvetica", 11)
        draw_kv("Score (%)", ats.get("score"))
        draw_kv("Skills Overlap", ats.get("skills_overlap"))
        draw_kv("Keywords Overlap", ats.get("keywords_overlap"))

    # draw charts
    if charts:
        for title, path in charts.items():
            if path and os.path.exists(path):
            
                if y < 8*cm:
                    c.showPage()
                    y = height - 2*cm
                c.setFont("Helvetica-Bold", 12)
                c.drawString(2*cm, y, title.replace("_", " ").title())
                y -= 0.8*cm
                img = ImageReader(path)
                c.drawImage(img, 2*cm, y-8*cm, width=12*cm, height=8*cm, preserveAspectRatio=True, anchor='sw')
                y -= 9*cm

    # save PDF
    c.showPage()
    c.save()
    return output_path