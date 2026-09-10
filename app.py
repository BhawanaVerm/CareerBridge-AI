import os
import time
import gradio as gr
from google import genai
from pypdf import PdfReader


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not configured."
    )

client = genai.Client(api_key=API_KEY)


# ============================================================
# RESUME PDF TEXT EXTRACTION
# ============================================================

def extract_resume_text(pdf_file):
    if pdf_file is None:
        return ""

    try:
        reader = PdfReader(pdf_file.name)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        text = "\n".join(text_parts).strip()
        if not text:
            return (
                "⚠️ I could not extract readable text from this PDF. "
                "Please make sure the PDF contains selectable text."
            )
        return text
    except Exception as e:
        return f"⚠️ Unable to read the PDF: {str(e)}"


# ============================================================
# GEMINI CAREER ANALYSIS (STABLE MODEL FALLBACKS)
# ============================================================

def analyze_career_profile(
    experience,
    career_gap,
    field,
    desired_role,
    background,
    resume_text
):
    resume_section = f"\nRESUME CONTENT:\n----------------\n{resume_text}\n" if resume_text else ""
    background_section = f"\nUSER'S ADDITIONAL BACKGROUND:\n------------------------------\n{background}\n" if background else ""

    prompt = f"""
You are CareerBridge AI, an experienced career advisor.

Your purpose is to help professionals who are returning to work after a career break.
Analyze the candidate's profile realistically and provide practical, encouraging and honest career guidance.
Do NOT give generic motivational advice.

Candidate information:
Total Experience: {experience}
Career Gap: {career_gap}
Current / Previous Field: {field}
Desired Role: {desired_role}
{background_section}
{resume_section}

Please provide your answer using the following structure:
## 1. Career Profile Summary
## 2. Strengths
## 3. Career Gap Impact
## 4. Suitable Job Roles
## 5. Skill Gap
### Already Useful
### Need Improvement
### Optional / Future
## 6. 30-Day Action Plan
## 7. Resume Suggestions
## 8. Interview Preparation
## 9. Job Search Strategy
## 10. Final Recommendation

Use simple, clear English. Be supportive but realistic.
"""

    # Using robust model endpoints across GenAI API specs
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    last_error = ""

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            time.sleep(0.5)

    return (
        "## ⚠️ Connection Issue\n\n"
        f"**API Response:** {last_error}\n\n"
        "Please check your network or try clicking again in a few seconds."
    )


# ============================================================
# MAIN CAREER ADVISOR FUNCTION
# ============================================================

def gradio_career_advisor(
    experience,
    career_gap,
    field,
    desired_role,
    background,
    resume_file
):
    resume_text = ""
    if resume_file is not None:
        resume_text = extract_resume_text(resume_file)
        if resume_text.startswith("⚠️"):
            return resume_text

    if not experience and not field and not desired_role and not resume_text and not background:
        return (
            "## ⚠️ Information Required\n\n"
            "Please provide your profile details or upload a resume to proceed."
        )

    return analyze_career_profile(
        experience=experience,
        career_gap=career_gap,
        field=field,
        desired_role=desired_role,
        background=background,
        resume_text=resume_text
    )


# ============================================================
# COMPLETE STABLE CSS FIX (PREVENTS WHITE FLASH & THEME BUG)
# ============================================================

custom_css = r"""
/* Page Container Alignment */
.gradio-container {
    max-width: 1150px !important;
    margin: 0 auto !important;
    padding: 10px 12px !important;
}

/* Rigid Dark Theme State Overrides */
html.dark, html.dark body, html.dark .gradio-container {
    background-color: #0d1117 !important;
    color: #e6edf3 !important;
}

html.dark .block, 
html.dark .panel, 
html.dark .card-section,
html.dark #output-card,
html.dark .gr-box,
html.dark div[data-testid="block"] {
    background-color: #161b22 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
}

html.dark input, 
html.dark textarea, 
html.dark select,
html.dark .file-preview {
    background-color: #0d1117 !important;
    border-color: #30363d !important;
    color: #f0f6fc !important;
}

/* Lock Output Box to Prevent White Flashing */
html.dark #output-scroll,
html.dark #output-scroll * {
    background-color: transparent !important;
    color: #e6edf3 !important;
}

/* Header Banner & Fixed Theme Toggle */
#header-banner {
    position: relative !important;
    padding: 14px 20px !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
    background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
}

#header-banner h1 {
    font-size: 24px !important;
    margin: 0 !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

#header-banner p {
    font-size: 13px !important;
    margin: 2px 0 0 0 !important;
    opacity: 0.92;
    color: #ffffff !important;
}

#theme-toggle-btn {
    position: absolute !important;
    top: 12px !important;
    right: 16px !important;
    background: rgba(255, 255, 255, 0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    color: #ffffff !important;
    padding: 5px 12px !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
}

#output-scroll {
    max-height: 480px !important;
    overflow-y: auto !important;
    padding: 6px !important;
}

#analyze-button {
    min-height: 42px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-top: 6px !important;
}

#privacy-note, #footer-note {
    font-size: 11px !important;
    text-align: center;
    margin-top: 6px !important;
}
"""

# ============================================================
# GRADIO APPLICATION BUILD
# ============================================================

custom_theme = gr.themes.Soft(
    primary_hue="violet",
    neutral_hue="slate"
)

with gr.Blocks(theme=custom_theme, css=custom_css, title="CareerBridge AI") as demo:

    gr.HTML(
        """
        <div id="header-banner">
            <button id="theme-toggle-btn" onclick="document.documentElement.classList.toggle('dark')">
                🌙 / ☀️ Theme
            </button>
            <h1>CareerBridge AI</h1>
            <p>AI-powered career guidance for professionals returning to work after a career break.</p>
        </div>
        """
    )

    with gr.Row(equal_height=False):
        # LEFT COLUMN: INPUTS
        with gr.Column(scale=3):
            with gr.Group(elem_classes="card-section"):
                gr.Markdown("### 👤 Your Career Profile")
                with gr.Row():
                    experience = gr.Textbox(
                        label="💼 Total Experience",
                        placeholder="e.g. 4 years",
                        lines=1
                    )
                    career_gap = gr.Textbox(
                        label="⏳ Career Gap",
                        placeholder="e.g. 5 years",
                        lines=1
                    )
                with gr.Row():
                    field = gr.Textbox(
                        label="🏢 Field / Industry",
                        placeholder="e.g. Cloud / IT",
                        lines=1
                    )
                    desired_role = gr.Textbox(
                        label="🎯 Desired Role",
                        placeholder="e.g. Cloud Administrator",
                        lines=1
                    )

            with gr.Group(elem_classes="card-section"):
                gr.Markdown("### 📄 Share Your Background")
                with gr.Tabs():
                    with gr.Tab("📎 Upload Resume"):
                        resume_file = gr.File(
                            label="Upload PDF Resume",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                    with gr.Tab("✍️ Type it in"):
                        background = gr.Textbox(
                            label="Skills, certifications, projects or goals",
                            placeholder="GCP certified, Cloud Run project, GenAI...",
                            lines=4
                        )

            analyze_button = gr.Button(
                "🚀 Analyze My Career",
                variant="primary",
                elem_id="analyze-button"
            )

        # RIGHT COLUMN: OUTPUT
        with gr.Column(scale=2):
            with gr.Group(elem_classes="card-section", elem_id="output-card"):
                gr.Markdown("### 💡 CareerBridge AI Analysis")
                output = gr.Markdown(
                    value="Your personalized career analysis will appear here.",
                    elem_id="output-scroll"
                )

    gr.Markdown(
        "🔒 Your resume is used only to generate this career analysis.",
        elem_id="privacy-note"
    )

    analyze_button.click(
        fn=gradio_career_advisor,
        inputs=[
            experience,
            career_gap,
            field,
            desired_role,
            background,
            resume_file
        ],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860))
    )
