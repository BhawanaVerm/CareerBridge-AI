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
# GEMINI CAREER ANALYSIS (STABLE FALLBACK MECHANISM)
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

    # Correct model names for modern GenAI SDK
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = ""

    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = str(e)
                time.sleep(1)

    return (
        "## ⚠️ Unable to process request\n\n"
        f"**Error Details:** {last_error}\n\n"
        "Please try again in a few moments."
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
            "## ⚠️ Please provide some information first\n\n"
            "Please enter your experience, field, desired role, background, or upload your resume."
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
# COMPACT CSS & DARK THEME OVERRIDES
# ============================================================

custom_css = """
/* Global Sizing & Padding Fix */
.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 10px 15px !important;
}

/* Fix Header Height */
#header-banner {
    padding: 12px 20px !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
    background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%) !important;
    color: white !important;
}

#header-banner h1 {
    font-size: 24px !important;
    margin: 0 !important;
    font-weight: 700 !important;
}

#header-banner p {
    font-size: 13px !important;
    margin: 2px 0 0 0 !important;
    opacity: 0.9;
}

/* Compact Group Cards */
.card-section {
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-bottom: 10px !important;
}

/* Output Card Sticky and Height Control */
#output-column {
    position: sticky !important;
    top: 10px !important;
}

#output-scroll {
    max-height: 520px !important;
    overflow-y: auto !important;
    padding: 8px !important;
}

/* Compact Textboxes and Buttons */
.gradio-container input, .gradio-container textarea {
    padding: 6px 10px !important;
    font-size: 13px !important;
}

#analyze-button {
    min-height: 40px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

#privacy-note, #footer-note {
    font-size: 11px !important;
    text-align: center;
    margin-top: 4px !important;
}
"""

# ============================================================
# GRADIO APP BUILD
# ============================================================

custom_theme = gr.themes.Soft(
    primary_hue="violet",
    neutral_hue="slate"
)

with gr.Blocks(theme=custom_theme, css=custom_css, title="CareerBridge AI") as demo:

    gr.HTML(
        """
        <div id="header-banner">
            <h1>CareerBridge AI</h1>
            <p>AI-powered career guidance for professionals returning to work after a career break.</p>
        </div>
        """
    )

    with gr.Row(equal_height=False):
        # LEFT COLUMN
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

        # RIGHT COLUMN (OUTPUT)
        with gr.Column(scale=2, elem_id="output-column"):
            with gr.Group(elem_classes="card-section"):
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
