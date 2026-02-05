# Technical Architecture and Pipeline

## Overview
The Job Application Assistant addresses the context window and latency constraints common in Large Language Model (LLM) applications. The system implements a localized compression step to refine input data before reasoning.

## Pipeline Components

### 1. Data Ingestion Layer
* **Library:** `pdfplumber`
* **Functionality:** The system iterates through PDF pages, extracting text objects and joining them with newline characters. A sanitization pass removes excessive whitespace and non-text artifacts to ensure clean input for the model.

### 2. The Compression Layer (ScaleDown)
* **Module:** Local `scaledown.compressor`
* **Algorithm:** Semantic Extraction
* **Prompt Strategy:** The system utilizes a specific extraction directive: *"Extract key requirements, skills, and responsibilities."* This mandates the compressor to discard non-essential information (e.g., generic company boilerplate) while preserving technical requirements.
* **Performance:** The system targets a 50% reduction ratio (`ratio=0.5`), significantly reducing the payload size for the subsequent API call.

### 3. The Reasoning Layer (Google Gemini)
* **Model:** `gemini-2.5-flash`
* **Strategy:** Adaptive System Prompting.
    * The system evaluates the user intent and the selected operational mode (Coach vs. Hiring Manager).
    * **Scenario A (Standard Review):** Enforces a structured output format (Executive Summary, Strengths, Critical Gaps, Action Plan).
    * **Scenario B (Specific Inquiry):** Removes formatting constraints to allow for natural language responses.
    * **Scenario C (Interview Mode):** Adopts a persona-based system prompt to simulate a hostile or neutral interviewer.