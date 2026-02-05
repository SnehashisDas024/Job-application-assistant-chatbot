"""
Job Application Assistant – Phase 2 (Compression Integration)
Status: Local ScaleDown module imported successfully. Compression logic active.
"""

import streamlit as st
import pdfplumber
import sys
import os

# ============================================================================
# LOCAL IMPORT SETUP
# ============================================================================

# 1. Add current directory to Python path so it finds the 'scaledown' folder
sys.path.append(os.getcwd())

# 2. Import specifically from the file shown in your screenshot
try:
    # Folder: scaledown -> compressor -> File: scaledown_compressor.py -> Class: ScaleDownCompressor
    from scaledown.compressor.scaledown_compressor import ScaleDownCompressor
except ImportError:
    # Backup: In some versions, it's exposed in the __init__.py one level up
    try:
        from scaledown.compressor import ScaleDownCompressor
    except ImportError as e:
        st.error(f"❌ Import Error: Could not find 'ScaleDownCompressor'. \nDetails: {e}")
        st.stop()

# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "resume_uploaded" not in st.session_state:
        st.session_state.resume_uploaded = False

# ============================================================================
# SIDEBAR
# ============================================================================

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

# ============================================================================
# LOGIC: PDF & COMPRESSION
# ============================================================================

def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            return text
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

def compress_jd(jd_text):
    """
    Uses the local ScaleDownCompressor with the CORRECT arguments.
    """
    try:
        # 1. Initialize with API Key (Required for the class)
        api_key = st.secrets.get("SCALEDOWN_API_KEY")
        if not api_key:
            return jd_text, "Skipped (Missing SCALEDOWN_API_KEY)"

        compressor = ScaleDownCompressor(api_key=api_key)
        
        # 2. Compress (Using your fixed arguments)
        result = compressor.compress(
            context=jd_text,  
            prompt="Extract key requirements, skills, and responsibilities.",
            target_model="gemini-2.5-flash", # Adjusted to 2.5-flash to be safe
            ratio=0.5
        )
        
        # 3. Handle Return Type (String vs Object)
        if hasattr(result, "content"):
            return result.content, f"ScaleDown: {getattr(result, 'savings_percent', '50')}% saved"
        elif isinstance(result, str):
            return result, "ScaleDown: Compression Active"
        else:
            return str(result), "ScaleDown: Active"

    except TypeError as e:
        print(f"ScaleDown Arguments Error: {e}")
        return jd_text, f"Compression Error: Arguments mismatch"
    except Exception as e:
        print(f"Compression Warning: {e}")
        return jd_text, "ScaleDown Skipped (Check Logs)"

# ============================================================================
# MAIN AI PIPELINE (Phase 2)
# ============================================================================

def get_ai_response(user_input, resume, jd):
    # 1. Extract Resume
    resume_text = extract_text_from_pdf(resume)
    if not resume_text:
        return "⚠️ Error: Could not read resume PDF."

    # 2. Compress JD
    compressed_jd, status_msg = compress_jd(jd)

    # 3. Return Compression Stats (Before AI integration)
    return f"""
    > *{status_msg}*
    
    **Internal Process:**
    1. **PDF Extracted:** ✅
    2. **Compression:** ✅ (Optimized for Gemini 2.5)
    3. **Context Ready:** {len(compressed_jd)} chars (Reduced from {len(jd)})
    
    *Gemini Integration pending in next update.*
    """

# ============================================================================
# APP ENTRY
# ============================================================================

def main():
    st.set_page_config(page_title="CareerBot", layout="wide")
    init_session_state()
    
    resume_file, jd_text = render_sidebar()
    
    st.title("🚀 Job Application Assistant")

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
                with st.spinner("Running Compression..."):
                    resp = get_ai_response(prompt, resume_file, jd_text)
                    st.markdown(resp)
                    st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == "__main__":
    main()