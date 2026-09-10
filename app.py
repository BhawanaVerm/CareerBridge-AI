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
    if not pdf_file:
        return ""

    try:
        # gr.File(type="filepath") returns a string filepath.
        # This also supports file-like objects safely.
        pdf_path = pdf_file if isinstance(pdf_file, str) else pdf_file.name

        reader = PdfReader(pdf_path)

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
# GEMINI CAREER ANALYSIS
# ============================================================

def analyze_career_profile(
    experience,
    career_gap,
    field,
    desired_role,
    background,
    resume_text
):

    resume_section = (
        f"\nRESUME CONTENT:\n----------------\n{resume_text}\n"
        if resume_text
        else ""
    )

    background_section = (
        f"\nUSER'S ADDITIONAL BACKGROUND:\n------------------------------\n"
        f"{background}\n"
        if background
        else ""
    )

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

    # ========================================================
    # CURRENT STABLE GEMINI MODELS
    # ========================================================
    #
    # gemini-2.0-flash is no longer available.
    #
    # Primary:
    # gemini-2.5-flash
    #
    # Fallback:
    # gemini-2.5-flash-lite
    #
    # ========================================================

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    errors = []

    for model_name in models_to_try:

        try:

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if response and response.text:
                return response.text

            errors.append(
                f"{model_name}: Empty response from Gemini."
            )

        except Exception as e:

            errors.append(
                f"{model_name}: {str(e)}"
            )

            time.sleep(0.5)

    # ========================================================
    # SHOW ALL MODEL ERRORS
    # ========================================================

    return (
        "## ⚠️ API Connection Error\n\n"
        "Gemini could not generate the career analysis.\n\n"
        "**Model/API details:**\n\n"
        + "\n\n".join(
            f"- {error}" for error in errors
        )
        + "\n\n"
        "Please check that GEMINI_API_KEY is valid and that "
        "the Gemini API is enabled for this key/project."
    )


# ============================================================
# MAIN CAREER ADVISOR ROUTINE
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

    if resume_file:

        resume_text = extract_resume_text(resume_file)

        if resume_text.startswith("⚠️"):
            return resume_text

    if (
        not experience
        and not field
        and not desired_role
        and not resume_text
        and not background
    ):

        return (
            "## ⚠️ Profile Information Missing\n\n"
            "Please enter your career details or upload a PDF resume first."
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
# STABLE CSS & RESPONSIVE LAYOUT
# ============================================================

custom_css = """

/* ============================================================
   MAIN CONTAINER
   ============================================================ */

.gradio-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 10px !important;
}


/* ============================================================
   HEADER
   ============================================================ */

#header-banner {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 14px 20px !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;

    background: linear-gradient(
        135deg,
        #6d28d9 0%,
        #7c3aed 100%
    ) !important;

    color: white !important;
}


#header-text h1 {
    font-size: 24px !important;
    margin: 0 !important;
    font-weight: 700 !important;
    color: white !important;
}


#header-text p {
    font-size: 12px !important;
    margin: 2px 0 0 0 !important;
    color: rgba(255, 255, 255, 0.9) !important;
}


/* ============================================================
   THEME BUTTON
   ============================================================ */

#theme-toggle-btn {
    background: rgba(255, 255, 255, 0.2) !important;

    border: 1px solid rgba(
        255,
        255,
        255,
        0.4
    ) !important;

    color: white !important;

    padding: 6px 14px !important;

    border-radius: 20px !important;

    font-size: 12px !important;

    font-weight: 600 !important;

    cursor: pointer !important;

    white-space: nowrap !important;
}


/* ============================================================
   OUTPUT
   ============================================================ */

#output-box {
    min-height: 460px !important;

    max-height: 560px !important;

    overflow-y: auto !important;

    padding: 12px !important;
}


#analyze-button {
    min-height: 44px !important;

    font-size: 15px !important;

    font-weight: 700 !important;

    margin-top: 8px !important;
}


#privacy-note {
    font-size: 11px !important;

    text-align: center !important;

    margin-top: 8px !important;
}


/* ============================================================
   CUSTOM DARK THEME
   ============================================================ */

/*
   IMPORTANT:

   The old code only added a class called "dark".

   Gradio does not automatically change its components
   just because body has a "dark" class.

   Therefore we use our own "cb-dark" class and explicitly
   style the Gradio components.
*/


html.cb-dark,
body.cb-dark {
    background: #111827 !important;
}


html.cb-dark .gradio-container,
body.cb-dark .gradio-container {
    background: #111827 !important;
}


/* Main groups / panels */

html.cb-dark .gr-group,
html.cb-dark .gr-box,
html.cb-dark .gr-panel,
html.cb-dark .gradio-group,
html.cb-dark .gradio-tabs,
html.cb-dark .gradio-tabitem,
html.cb-dark .gradio-container .block {
    background: #1f2937 !important;

    color: #f3f4f6 !important;

    border-color: #374151 !important;
}


/* Text */

html.cb-dark label,
html.cb-dark .label-wrap,
html.cb-dark .gradio-markdown,
html.cb-dark .prose,
html.cb-dark p,
html.cb-dark h1,
html.cb-dark h2,
html.cb-dark h3,
html.cb-dark h4,
html.cb-dark h5,
html.cb-dark h6,
html.cb-dark span {
    color: #f3f4f6 !important;
}


/* Textboxes / inputs */

html.cb-dark input,
html.cb-dark textarea,
html.cb-dark select,
html.cb-dark .wrap,
html.cb-dark .file-preview,
html.cb-dark .file-upload {
    background: #111827 !important;

    color: #f9fafb !important;

    border-color: #4b5563 !important;
}


/* Placeholder */

html.cb-dark input::placeholder,
html.cb-dark textarea::placeholder {
    color: #9ca3af !important;
}


/* Buttons */

html.cb-dark button:not(#theme-toggle-btn),
html.cb-dark .tab-nav button {
    color: #f9fafb !important;
}


/* Selected tab */

html.cb-dark .tab-nav button.selected {
    color: #c4b5fd !important;
}


/* Privacy text */

html.cb-dark #privacy-note,
html.cb-dark #privacy-note * {
    color: #d1d5db !important;
}


/* Keep purple header unchanged */

html.cb-dark #header-banner,
body.cb-dark #header-banner {

    background: linear-gradient(
        135deg,
        #6d28d9 0%,
        #7c3aed 100%
    ) !important;
}


html.cb-dark #header-text h1,
html.cb-dark #header-text p,
html.cb-dark #theme-toggle-btn {
    color: white !important;
}

"""


# ============================================================
# GRADIO THEME
# ============================================================

custom_theme = gr.themes.Soft(
    primary_hue="violet",
    neutral_hue="slate"
)


# ============================================================
# MAIN APP
# ============================================================

with gr.Blocks(
    theme=custom_theme,
    css=custom_css,
    title="CareerBridge AI"
) as demo:


    # ========================================================
    # HEADER
    # ========================================================

    with gr.Row(elem_id="header-banner"):

        with gr.Column(
            scale=8,
            min_width=200,
            elem_id="header-text"
        ):

            gr.HTML(
                "<h1>CareerBridge AI</h1>"
                "<p>"
                "AI-powered career guidance for professionals "
                "returning to work after a career break."
                "</p>"
            )


        with gr.Column(
            scale=2,
            min_width=100
        ):

            theme_btn = gr.Button(
                "🌙 / ☀️ Theme",
                elem_id="theme-toggle-btn"
            )


    # ========================================================
    # THEME TOGGLE
    # ========================================================

    theme_btn.click(
        None,
        inputs=None,
        outputs=None,

        js="""
        () => {

            const html = document.documentElement;
            const body = document.body;

            const isDark =
                !html.classList.contains("cb-dark");

            html.classList.toggle(
                "cb-dark",
                isDark
            );

            body.classList.toggle(
                "cb-dark",
                isDark
            );

        }
        """
    )


    # ========================================================
    # MAIN LAYOUT
    # ========================================================

    with gr.Row(equal_height=False):


        # ====================================================
        # LEFT SIDE
        # ====================================================

        with gr.Column(scale=3):


            # =================================================
            # CAREER PROFILE
            # =================================================

            with gr.Group():

                gr.Markdown(
                    "### 👤 Your Career Profile"
                )


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


            # =================================================
            # BACKGROUND
            # =================================================

            with gr.Group():

                gr.Markdown(
                    "### 📄 Share Your Background"
                )


                with gr.Tabs():


                    # =========================================
                    # UPLOAD RESUME
                    # =========================================

                    with gr.Tab("📎 Upload Resume"):

                        resume_file = gr.File(
                            label="Upload PDF Resume",
                            file_types=[".pdf"],
                            type="filepath"
                        )


                    # =========================================
                    # TYPE BACKGROUND
                    # =========================================

                    with gr.Tab("✍️ Type it in"):

                        background = gr.Textbox(
                            label=(
                                "Skills, certifications, "
                                "projects or goals"
                            ),

                            placeholder=(
                                "GCP certified, Cloud Run project, "
                                "GenAI..."
                            ),

                            lines=4
                        )


            # =================================================
            # ANALYZE BUTTON
            # =================================================

            analyze_button = gr.Button(
                "🚀 Analyze My Career",
                variant="primary",
                elem_id="analyze-button"
            )


        # ====================================================
        # RIGHT SIDE
        # ====================================================

        with gr.Column(scale=2):

            with gr.Group():

                gr.Markdown(
                    "### 💡 CareerBridge AI Analysis"
                )


                output = gr.Markdown(
                    value=(
                        "Your personalized career analysis "
                        "will appear here."
                    ),

                    elem_id="output-box"
                )


    # ========================================================
    # PRIVACY NOTE
    # ========================================================

    gr.Markdown(
        "🔒 Your resume is used only to generate this career analysis.",
        elem_id="privacy-note"
    )


    # ========================================================
    # ANALYZE EVENT
    # ========================================================

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


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",

        server_port=int(
            os.environ.get(
                "PORT",
                7860
            )
        )
    )
