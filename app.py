import streamlit as st
import pandas as pd
import datetime

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

# ---- Simple Matching Logic ----
def calculate_score(resume_text, jd_keywords):
    score = 0
    keywords = jd_keywords.lower().split(",")
    for word in keywords:
        if word.strip() in resume_text.lower():
            score += 1
    return int((score / len(keywords)) * 100) if keywords else 0

# ---- Dummy resume text (for demo) ----
resume_text = "sales banking insurance targets client relationship"

if st.button("Submit"):
    if uploaded_file and selected_jd:
        jd_keywords = st.session_state.jds[selected_jd]
        score = calculate_score(resume_text, jd_keywords)

        status = "Shortlisted" if score >= 75 else "Review" if score >= 50 else "Rejected"

        data = {
            "Date": datetime.datetime.now(),
            "File Name": uploaded_file.name,
            "JD": selected_jd,
            "Score": score,
            "Status": status
        }

        df = pd.DataFrame([data])

        st.success("Resume Submitted!")
        st.write(df)

        # Download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Report", csv, "report.csv", "text/csv")
