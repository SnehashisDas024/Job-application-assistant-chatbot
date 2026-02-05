"""
Job Application Assistant – Phase 3 (Final & Fixed)
Combines:
1. Correct Local ScaleDown import.
2. Adaptive Prompting (Fixes the "wasteful format" issue).
3. Inline Key Check (Fixes the "check_api_keys" NameError).
"""

import streamlit as st
import pdfplumber
from google import genai
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
# MAIN AI PIPELINE (Fixed & Adaptive)
# ============================================================================

def get_ai_response(user_input, resume, jd):
    # 1. Check Gemini Key (INLINE FIX: Removes dependence on check_api_keys)
    gemini_key = st.secrets.get("GEMINI_API_KEY")
    if not gemini_key:
        return "⚠️ Error: GEMINI_API_KEY is missing in .streamlit/secrets.toml"

    # 2. Extract Resume
    resume_text = extract_text_from_pdf(resume)
    if not resume_text:
        return "⚠️ Error: Could not read resume PDF."

    # 3. Compress JD
    compressed_jd, status_msg = compress_jd(jd)

    # 4. Call Gemini with ADAPTIVE PROMPT (Scenario A/B)
    try:
        client = genai.Client(api_key=gemini_key)
        
        prompt = f"""You are an expert technical recruiter with 15+ years of experience.

**CONTEXT:**
JOB DESCRIPTION (Optimised):
{compressed_jd}

CANDIDATE RESUME:
{resume_text}

**USER QUERY:**
"{user_input}"

**INSTRUCTIONS:**
Analyze the User Query and decide the best response format:

**SCENARIO A: If the user asks for a general Resume Review or Critique:**
Provide a comprehensive analysis using this exact structure:
1. **Executive Summary**: A 2-sentence verdict on fit.
2. **Strengths**: 3 bullet points specific to the resume.
3. **Critical Gaps**: 3 missing keywords/skills required by the JD.
4. **Action Plan**: 1 specific, high-impact fix.

**SCENARIO B: If the user asks a SPECIFIC question (e.g., "How do I fix X?", "List what to do"):**
- Answer **ONLY** that question directly.
- Be concise and tactical.
- **DO NOT** output the Strengths/Gaps/Action Plan structure unless specifically asked.

**TONE:** Professional, constructive, and direct.
"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        if response.text:
            return f"> *{status_msg}*\n\n" + response.text
        else:
            return "⚠️ Gemini returned no text."

    except Exception as e:
        return f"Gemini Error: {e}"

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
                with st.spinner("Analyzing..."):
                    resp = get_ai_response(prompt, resume_file, jd_text)
                    st.markdown(resp)
                    st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == "__main__":
    main()