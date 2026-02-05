"""
Job Application Assistant – Phase 1 (Frontend & Structure)
Status: UI Layout complete. PDF Parsing logic added. AI/Compression Pending.
"""

import streamlit as st
import pdfplumber
import sys
import os

# SESSION STATE

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "resume_uploaded" not in st.session_state:
        st.session_state.resume_uploaded = False

# SIDEBAR

def render_sidebar():
    with st.sidebar:
        st.title("Configuration")

        resume_file = st.file_uploader(
            "Upload Resume (PDF)", type=["pdf"],
            help="Upload your resume in PDF format"
        )

        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the job description text here...",
            height=200
        )

        if resume_file and job_description.strip():
            st.success("✓ Ready!")
            st.session_state.resume_uploaded = True
        else:
            st.session_state.resume_uploaded = False

    return resume_file, job_description

# LOGIC: PDF EXTRACTION

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            return text
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

# MAIN AI PIPELINE (Placeholder for Phase 1)

def get_ai_response(user_input, resume, jd):
    # 1. Extract Resume
    resume_text = extract_text_from_pdf(resume)
    if not resume_text:
        return "⚠️ Error: Could not read resume PDF."

    # 2. Mock Response (Frontend Test)
    return f"""
    > *System Status: Frontend Online. PDF Parsed ({len(resume_text)} chars).*
    
    **Simulation Response:**
    I have received your query: "{user_input}"
    
    The UI is fully functional. 
    - **Resume:** Loaded
    - **JD:** Loaded
    """

# APP ENTRY

def main():
    st.set_page_config(page_title="CareerBot", layout="wide")
    init_session_state()
    
    resume_file, jd_text = render_sidebar()
    
    st.title("Job Application Assistant")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Analyze my resume..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if not st.session_state.resume_uploaded:
            err = "⚠️ Please upload a resume and JD first."
            st.chat_message("assistant").markdown(err)
            st.session_state.messages.append({"role": "assistant", "content": err})
        else:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing (Simulation)..."):
                    resp = get_ai_response(prompt, resume_file, jd_text)
                    st.markdown(resp)
                    st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == "__main__":
    main()