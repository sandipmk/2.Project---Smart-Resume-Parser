# -*- coding: utf-8 -*-

import os
import io
import json
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# parser.py
from parser import (
    extract_text_from_pdf, extract_text_from_docx, parse_resume_text,
    compute_ats_score, highlight_jd_keywords
)
from report import generate_report_pdf

# set a Streamlit page
st.set_page_config(page_title="Smart Resume Parser (ATS+Batch)", page_icon="🧠", layout="wide")

st.title("🧠 Smart Resume Parser — ATS Score + Batch Shortlisting")
st.caption("Upload one or more resumes, paste a Job Description .")

# sidebar options
with st.sidebar:
    st.header("⚙️ Options")
    top_n = st.number_input("Shortlist top N (by ATS score)", min_value=1, max_value=50, value=3, step=1)

col1, col2 = st.columns([1,1])
with col1:
    # file uploader for resumes
    uploads = st.file_uploader("Upload Resume(s) (PDF/DOCX)", type=["pdf","docx"], accept_multiple_files=True)
with col2:
    # text area for pasting job description
    jd_text = st.text_area("Paste Job Description (for ATS scoring & highlights)", height=220, placeholder="Paste JD text here...")

def parse_single_file(uploaded):
    with tempfile.NamedTemporaryFile(delete=False, suffix="."+uploaded.name.split(".")[-1]) as tmp:
        tmp.write(uploaded.read())
        temp_path = tmp.name
    if uploaded.name.lower().endswith(".pdf"):
        text = extract_text_from_pdf(temp_path)
    else:
        text = extract_text_from_docx(temp_path)
    os.remove(temp_path)
    return text

# save results
results = []
if uploads:
    for f in uploads:
        text = parse_single_file(f)
        parsed = parse_resume_text(text)
        ats = compute_ats_score(parsed.get("Skills", []), parsed.get("Keywords", []), jd_text or "")
        parsed["ATS"] = ats
        parsed["FileName"] = f.name
        parsed["JD_Highlighted_HTML"] = highlight_jd_keywords(parsed.get("RawText",""), jd_text or "")
        results.append(parsed)

if results:
    df = pd.DataFrame([{
        "File": r.get("FileName"),
        "Name": r.get("Name"),
        "Email": r.get("Email"),
        "Phone": r.get("Phone"),
        "ExperienceYears": r.get("ExperienceYears"),
        "ATS_Score": r["ATS"]["score"] if r.get("ATS") else 0,
        "Skills": ", ".join(r.get("Skills") or [])
    } for r in results]).sort_values(by="ATS_Score", ascending=False)

    st.subheader("📊 Summary (sorted by ATS score)")
    st.dataframe(df, use_container_width=True)

    # shortlist top N candidates
    shortlist = df.head(int(top_n))
    st.success(f"✅ Shortlisted Top {len(shortlist)} Candidate(s)")
    st.dataframe(shortlist, use_container_width=True)

    # download button for all candidates
    csv_bytes = df.to_csv(index=False).encode()
    st.download_button("⬇️ Download Master CSV", data=csv_bytes, file_name="all_candidates.csv", mime="text/csv")

    # candidate drill-down
    st.subheader("🔎 Candidate Drill‑Down")
    selected_file = st.selectbox("Select a candidate", df["File"].tolist())
    sel = next(r for r in results if r["FileName"] == selected_file)

    # display selected candidate's details
    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown("**Extracted Data**")
        # display extracted information in JSON format
        st.json({
            k: v for k, v in sel.items()
            if k in ["Name","Email","Phone","Skills","SkillCategories","Education","ExperienceYears","ATS"]
        })

    with c2:
        st.markdown("**JD Keyword Highlights in Resume**")
        # highlight job description keywords in resume
        st.markdown(sel.get("JD_Highlighted_HTML","(paste JD to enable highlights)"), unsafe_allow_html=True)

    # display visuals
    st.subheader("📈 Visuals")
    figs = {}

    # create skills pie chart
    if sel.get("Skills"):
        fig1, ax1 = plt.subplots()
        counts = [1]*len(sel["Skills"])
        ax1.pie(counts, labels=sel["Skills"], autopct="%1.0f%%", startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
        spath = os.path.join(tempfile.gettempdir(), "skills_pie.png")
        fig1.savefig(spath, bbox_inches='tight')
        figs["skills_pie"] = spath

    # create experience bar chart
    if sel.get("ExperienceYears"):
        fig2, ax2 = plt.subplots()
        ax2.bar(["Experience (years)"], [sel["ExperienceYears"]])
        st.pyplot(fig2)
        epath = os.path.join(tempfile.gettempdir(), "exp_bar.png")
        fig2.savefig(epath, bbox_inches='tight')
        figs["exp_bar"] = epath

    # download report section
    st.subheader("📥 Download Report")
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, f"{sel.get('Name') or sel.get('FileName')}_report.pdf")
    if st.button("Generate PDF Report for Selected"):
        # generate PDF report
        generate_report_pdf(pdf_path, sel, figs)
        with open(pdf_path, "rb") as f:
            # download button for PDF report
            st.download_button("Download Report (PDF)", f, file_name=os.path.basename(pdf_path), mime="application/pdf")

else:
    # display info message
    st.info("Upload one or more resumes to begin. Paste a JD for ATS scoring, highlights, and shortlisting.")