import streamlit as st
import pandas as pd
import re
import PyPDF2
import docx

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

# ---- Upload Resume ----
st.header("📤 Upload Resume")

uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)")

if st.session_state.jds:
    selected_jd = st.selectbox("Select Job Role", list(st.session_state.jds.keys()))
else:
    st.warning("Please add at least one JD")
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

    return text.lower()

# ---- Score ----
def calculate_score(resume_text, jd_keywords):
    keywords = jd_keywords.lower().split(",")
    match = sum(1 for word in keywords if word.strip() in resume_text)
    return int((match / len(keywords)) * 100) if keywords else 0

# ---- Experience Check ----
def check_experience(resume_text):
    if "sales" not in resume_text:
        return "No sales experience"

    years = re.findall(r'(\d+)\s*year', resume_text)
    if years:
        if max(map(int, years)) < 1:
            return "Less experience"
        else:
            return "OK"
    return "Less experience"

# ---- Submit ----
if st.button("Submit"):
    if uploaded_file and selected_jd:
        with st.spinner("Processing..."):
            text = extract_text(uploaded_file)
            score = calculate_score(text, st.session_state.jds[selected_jd])
            exp = check_experience(text)

            if exp != "OK":
                status = "Rejected"
                reason = exp
            else:
                if score >= 75:
                    status = "Shortlisted"
                    reason = ""
                elif score >= 50:
                    status = "Review"
                    reason = ""
                else:
                    status = "Rejected"
                    reason = "Profile not matching"

        st.success("Done")

        st.write(f"Score: {score}%")
        st.write(f"Status: {status}")

        if status == "Rejected":
            st.error(f"Reason: {reason}")
