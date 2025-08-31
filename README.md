# 🧠 Smart Resume Parser (ATS + Streamlit)

A Python-powered **Smart Resume Parser** with **ATS score calculator** and **interactive dashboard** built using Streamlit.  
It parses resumes (PDF/DOCX), extracts structured details (Name ,skills, experience, contact info), highlights JD keywords, and generates professional reports.

---

## 🚀 Features

- 📂 **Multi-format parsing**: Supports PDF and DOCX resumes  
- 🧠 **NLP-powered extraction** using spaCy + regex  
- 🎯 **ATS Score Calculator** against Job Descriptions  
- 📊 **Interactive Dashboard** with charts (Streamlit + Matplotlib)  
- 📑 **Automated PDF Reports** generated via ReportLab  
- ⚡ **Fast & Lightweight** with modular parser  

---

## 🗂️ Project Structure
```
project-2-smart-resume-parser/
├── app.py # Streamlit app (UI + flow)
├── parser.py # Resume parsing logic (spaCy + regex + PyMuPDF + docx)
├── report.py # PDF report generator
├── requirements.txt # Dependencies
└── README.md # Project documentation
```

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/sandipmk/2.project--smart-resume-parser.git
cd 2.project--smart-resume-parser

# Create a virtual environment (recommended)
python -m venv .venv
# Activate (Windows)
.venv\Scripts\activate
# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the app
streamlit run app.py
```

---
## 🏃 Usage
Run Streamlit 
```bash
streamlit run app.py
```
 - This will open a browser window where you can:

 - Upload resumes (PDF/DOCX)

 - Paste job description text

 - View extracted details (skills, experience, contact, etc.)

 - See ATS score + keyword highlights

 - Generate a detailed PDF report

---

## 📊 Example Workflow

1. Upload resume.pdf

2. Paste a Job Description

3. Parser extracts fields: Name, Email, Phone, Skills, Experience, Education

4. ATS Score is calculated by JD keyword match

5. Visual results shown in dashboard (charts)

6. Export professional PDF report

---

## 🧱 Tech Stack

   - Python 3.9+

   - Streamlit — UI

   - spaCy — NLP

   - PyMuPDF (fitz) — PDF text extraction

   - python-docx — DOCX parsing

   - ReportLab — Report generation

   - Matplotlib + Pandas — Data analysis & visualization

---
