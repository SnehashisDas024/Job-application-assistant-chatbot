# Job Application Assistant Chatbot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange)
![ScaleDown](https://img.shields.io/badge/Compression-ScaleDown%20Local-green)

A smart career assistant that helps candidates tailor their resumes to specific job descriptions. It leverages **Local Prompt Compression** (ScaleDown) to process large documents cost-effectively and **Google Gemini 2.5** for high-reasoning career advice.

## Key Features
* ** PDF Parsing**: Automatically extracts and sanitizes text from PDF resumes.
* ** Semantic Compression**: Uses a local `ScaleDown` module to reduce job description token usage by ~40-60% without losing context.
* ** Adaptive AI**: Switches intelligence modes:
    * *Analysis Mode*: Detailed gap analysis, strengths, and actionable tips.
    * *Direct Mode*: Answers specific user questions (e.g., "What salary should I ask for?").
* ** Interview Prep Mode**: (Creative Feature) Can switch roles to become a hiring manager and conduct a mock interview.

## Architecture
The app follows a 3-stage intelligence pipeline:
1.  **Ingestion**: `pdfplumber` extracts raw text from user uploads.
2.  **Optimization**: The local `scaledown` module analyzes the Job Description (JD) and removes non-essential tokens using a "Resume Match" extraction prompt.
3.  **Reasoning**: The compressed context is sent to **Gemini 2.5 Flash**, which generates the final strategic advice.

## Quick Start

### Prerequisites
* Python 3.10+
* Google AI Studio API Key

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/job-application-assistant-chatbot.git](https://github.com/your-username/job-application-assistant-chatbot.git)
    cd job-application-assistant-chatbot
    ```

2.  **Install Dependencies**
    ```bash
    pip install streamlit google-genai pdfplumber
    ```
    *(Note: The `scaledown` module is included locally in the repo)*

3.  **Configure Keys**
    Create a file named `.streamlit/secrets.toml`:
    ```toml
    GEMINI_API_KEY = "your_key_here"
    SCALEDOWN_API_KEY = "any_string_works_locally"
    ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```
## Acknowledgments
This project utilizes the **ScaleDown** library for semantic text compression. We credit the original authors for their work on the compression algorithms used in the local module:
* **ScaleDown Repository:** [https://github.com/scaledown-team/scaledown](https://github.com/scaledown-team/scaledown)

## License
MIT License
