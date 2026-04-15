import streamlit as st
import pandas as pd
import datetime
import re

# For PDF reading
import PyPDF2

# For DOCX reading
import docx

# For Image OCR
import pytesseract
from PIL import Image

st.set_page_config(page_title="Resume Screener - GIC", layout="wide")

st.title("📄 Global India Consultants - Resume Screener")

# ---- JD Section ----
st.sidebar.header("📋 Job Descriptions")

if "jds" not in st.session_state:
    st.session_state.jds = {}

jd_name = st.sidebar.text_input("Enter JD Name")
jd_text = st.sidebar.text_area("Enter JD Keywords (comma separated)")

if st.sidebar.button("Save JD"):
    if jd_name and jd_text:
        st.session_state.jds[jd_name] = jd_text
        st.sidebar.success("JD Saved!")

# ---- Upload Section ----
st.header("📤 Upload Resume")

uploaded_file = st.file_uploader("Upload Resume (PDF/DOC/Image)")

if st.session_state.jds:
    selected_jd = st.selectbox("Select Job Role", list(st.session_state.jds.keys()))
else:
    st.warning("Please add at least one JD from sidebar")
    selected_jd = None

# ---- Extract Text ----
def extract_text(file):
    text = ""
    
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text
    
    elif "image" in file.type:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    
    return text.lower()

# ---- Score ----
def calculate_score(resume_text, jd_keywords):
    score = 0
    keywords = jd_keywords.lower().split(",")
    for word in keywords:
        if word.strip() in resume_text:
            score += 1
    return int((score / len(keywords)) * 100) if keywords else 0

# ---- Experience Check ----
def check_experience(resume_text):
    if "sales" not in resume_text:
        return "No relevant sales experience."

    years = re.findall(r'(\d+)\s*year', resume_text)
    
    if years:
        max_year = max([int(y) for y in years])
        if max_year < 1:
            return "Insufficient sales experience."
        else:
            return "OK"
    else:
        return "Insufficient sales experience."

# ---- Submit ----
if st.button("Submit"):
    if uploaded_file and selected_jd:
        
        with st.spinner("Processing..."):
            resume_text = extract_text(uploaded_file)

            score = calculate_score(resume_text, st.session_state.jds[selected_jd])
            exp_status = check_experience(resume_text)

            if exp_status != "OK":
                status = "Rejected"
                reason = exp_status
            else:
                status = "Shortlisted" if score >= 75 else "Review" if score >= 50 else "Rejected"
                reason = "Profile not matching job requirements." if status == "Rejected" else ""

        st.success("Resume Submitted!")

        st.write(f"Score: {score}% | Status: {status}")

        if status == "Rejected":
            st.write(f"❌ Reason: {reason}")
