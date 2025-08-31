# -*- coding: utf-8 -*-

import re
import fitz  # PyMuPDF
import docx
import spacy
from typing import Dict, List, Tuple

#download spacy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")

#skill categories
SKILL_CATEGORIES = {
    "Languages": ["c","c++","python","java","javascript","typescript","go","php","ruby"],
    "Frameworks": ["flask","django","fastapi","spring","react","angular","vue","express"],
    "Databases": ["mysql","postgresql","sqlite","mongodb","redis"],
    "ML/AI": ["numpy","pandas","matplotlib","scikit-learn","tensorflow","pytorch","spacy","transformers","opencv","nlp"],
    "Cloud/DevOps": ["aws","gcp","azure","docker","kubernetes","linux","git","github","gitlab","ci","cd"]
}

SKILLS_MASTER = sorted({s for lst in SKILL_CATEGORIES.values() for s in lst})

# degree keywords
DEGREE_KEYWORDS = [
    "b.tech","btech","b.e","be","bsc","b.sc","bca","bachelor",
    "m.tech","mtech","m.e","me","msc","m.sc","mca","master","mba","phd"
]

# function to extract text from a PDF file
def extract_text_from_pdf(file_path: str) -> str:
  
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# function to extract text from a DOCX file
def extract_text_from_docx(file_path: str) -> str:
  
    d = docx.Document(file_path)
    return "\n".join([p.text for p in d.paragraphs])

# function to clean text
def clean_text(txt: str) -> str:
  
    lines = [re.sub(r'\s+', ' ', ln).strip() for ln in txt.splitlines()]
    return "\n".join([ln for ln in lines if ln])

# function to extract contact information
def extract_contact_info(text: str) -> Tuple[str, str]:
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text, flags=re.I)
    phone_match = re.search(r'(\+?\d[\d\-\s]{8,15}\d)', text)
    email = email_match.group(0) if email_match else None
    phone = phone_match.group(0) if phone_match else None
    return email, phone

# function to guess name from lines
def guess_name_from_lines(lines: List[str]) -> str:

    # 1) Check for all-uppercase names in the first 10 lines
    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        if any(skill in line.lower() for skill in SKILLS_MASTER) or any(char.isdigit() for char in line):
            continue
        if line.isupper() and 2 <= len(line.split()) <= 4 and re.match(r'^[A-Z\s]+$', line):
            return line.title()

    # 2) Check for title-case names in the first 10 lines
    for i in range(min(10, len(lines))):
        line = lines[i].strip()
        if any(skill in line.lower() for skill in SKILLS_MASTER) or any(char.isdigit() for char in line):
            continue
        if 2 <= len(line.split()) <= 4 and re.match(r'^[A-Z][a-z]+(\s[A-Z][a-z]+)+$', line):
            return line

    return None

# function to extract name from text
def extract_name(text: str) -> str:

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    name = guess_name_from_lines(lines)
    if name:
        return name

    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
            return ent.text

    return None

# function to match keywords found in text against a given list of keywords
def match_keywords(text: str, keywords: List[str]) -> List[str]:
   
    found = []
    low = text.lower()
    for k in keywords:
        if k.lower() in low:
            found.append(k.title())
    return sorted(list(set(found)))

# function to categorize skills
def categorize_skills(text: str) -> Dict[str, List[str]]:
   
    low = text.lower()
    categorized = {}
    for cat, skills in SKILL_CATEGORIES.items():
        hits = [s.title() for s in skills if s in low]
        if hits:
            categorized[cat] = sorted(list(set(hits)))
    return categorized

# extract education information
def extract_education(text: str) -> List[str]:
    found = match_keywords(text, DEGREE_KEYWORDS)
    lines = text.splitlines()
    edu_lines = []
    for ln in lines:
        if any(d.lower() in ln.lower() for d in DEGREE_KEYWORDS) and re.search(r'(20|19)\\d{2}', ln):
            edu_lines.append(ln.strip())
    return list(set(found + edu_lines))

# function to extract years of experience
def extract_experience_years(text: str) -> float:
   
    years = 0.0
    for m in re.finditer(r'(\d+(?:\.\d+)?)\s*\+?\s*years?', text.lower()):
        try:
            years = max(years, float(m.group(1)))
        except:
            pass
    return years if years > 0 else None

# function to extract resume keywords
def extract_resume_keywords(text: str) -> List[str]:
   
    doc = nlp(text)
    tokens = [t.lemma_.lower() for t in doc if t.pos_ in ("NOUN","PROPN") and t.is_alpha]
    uniq = []
    for t in tokens:
        if len(t) >= 3 and t not in uniq:
            uniq.append(t)
    return uniq[:120]

# function to highlight job description keywords in resume text
def highlight_jd_keywords(resume_text: str, jd_text: str) -> str:
   
    if not jd_text:
        return resume_text.replace("\n", "<br>")
    tokens = sorted({w.lower() for w in re.findall(r'[a-zA-Z]{3,}', jd_text)}, key=len, reverse=True)
    html = resume_text
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for t in tokens[:200]:
        html = re.sub(fr'(?i)\b({re.escape(t)})\b', r'<mark>\1</mark>', html)
    html = html.replace("\n", "<br>")
    return html

# function to compute ATS score
def compute_ats_score(resume_skills: List[str], resume_keywords: List[str], jd_text: str) -> Dict[str, float]:
   
    if not jd_text:
        return {"score": 0.0, "skills_overlap": 0, "keywords_overlap": 0}
    jd_low = jd_text.lower()
    jd_tokens = set([w for w in re.findall(r'[a-zA-Z]+', jd_low) if len(w) >= 3])
    skill_overlap = len(set([s.lower() for s in resume_skills]) & jd_tokens)
    keyword_overlap = len(set(resume_keywords) & jd_tokens)
    score = 0.0
    if jd_tokens:
        score = min(100.0, (skill_overlap * 6 + keyword_overlap * 4) / max(1, len(jd_tokens)) * 100)
    return {"score": round(score, 2), "skills_overlap": skill_overlap, "keywords_overlap": keyword_overlap}

# function to parse resume text
def parse_resume_text(text: str) -> Dict:
    
    cleaned = clean_text(text)
    name = extract_name(cleaned)
    email, phone = extract_contact_info(cleaned)
    flat_skills = match_keywords(cleaned, SKILLS_MASTER)
    skill_cats = categorize_skills(cleaned)
    education = extract_education(cleaned)
    years = extract_experience_years(cleaned)
    keywords = extract_resume_keywords(cleaned)
    return {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Skills": flat_skills,
        "SkillCategories": skill_cats,
        "Education": education,
        "ExperienceYears": years,
        "Keywords": keywords,
        "RawText": cleaned
    }