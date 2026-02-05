# Job Application Assistant

An AI-powered tool to help job seekers tailor their resumes to specific job descriptions. Built with **Streamlit**, **Google Gemini**, and **ScaleDown**.

## Features
* **PDF Parsing:** Extracts text from resume PDFs automatically.
* **Smart Compression:** Uses local `ScaleDown` library to reduce token usage by ~50%.
* **AI Analysis:** Uses **Gemini 2.5 Flash** to identify strengths, missing keywords, and actionable tips.
* **Adaptive Chat:** Switches between "Full Review" and "Specific Q&A" modes.
