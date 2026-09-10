import os
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
        # gr.File(type="filepath") returns a filepath string
        pdf_path = (
            pdf_file
            if isinstance(pdf_file, str)
            else pdf_file.name
        )

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

        return (
            f"⚠️ Unable to read the PDF: {str(e)}"
        )


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

    resume_section = ""

    if resume_text:
        resume_section = f"""
RESUME CONTENT:
----------------
{resume_text}
"""


    background_section = ""

    if background:
        background_section = f"""
USER'S ADDITIONAL BACKGROUND:
------------------------------
{background}
"""


    prompt = f"""
You are CareerBridge AI, an experienced career advisor.

Your purpose is to help professionals who are returning to work
after a career break.

Analyze the candidate's profile realistically and provide
practical, encouraging and honest career guidance.

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

Use simple, clear English.

Be supportive but realistic.
"""


    try:

        # ====================================================
        # CURRENT GEMINI MODEL
        # ====================================================
        #
        # gemini-2.5-flash:
        # Not available to many new users
        #
        # gemini-2.5-flash-lite:
        # Can return 503 during high demand
        #
        # Using current stable Gemini 3.6 Flash
        # ====================================================

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        response_text = getattr(
            interaction,
            "output_text",
            None
        )

        if response_text and response_text.strip():
            return response_text


        return (
            "## ⚠️ Gemini Response Error\n\n"
            "Gemini returned an empty response. "
            "Please click **Analyze My Career** again."
        )


    except Exception as e:

        return (
            "## ⚠️ API Connection Error\n\n"
            "Gemini could not generate the career analysis.\n\n"
            f"**Error Details:** {str(e)}\n\n"
            "Please check the Gemini API configuration "
            "and try again."
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


    # ========================================================
    # EXTRACT RESUME TEXT
    # ========================================================

    if resume_file:

        resume_text = extract_resume_text(resume_file)

        if resume_text.startswith("⚠️"):
            return resume_text


    # ========================================================
    # CHECK PROFILE INFORMATION
    # ========================================================

    if (
        not experience
        and not field
        and not desired_role
        and not resume_text
        and not background
    ):

        return (
            "## ⚠️ Profile Information Missing\n\n"
            "Please enter your career details or "
            "upload a PDF resume first."
        )


    # ========================================================
    # ANALYZE PROFILE
    # ========================================================

    return analyze_career_profile(
        experience=experience,
        career_gap=career_gap,
        field=field,
        desired_role=desired_role,
        background=background,
        resume_text=resume_text
    )


# ============================================================
# CLEAN LIGHT + DARK THEME CSS
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
   LIGHT MODE
   PURE WHITE BACKGROUND + BLACK TEXT
   ============================================================ */

html,
body {
    background: #ffffff !important;
}

.gradio-container {
    background: #ffffff !important;
    color: #000000 !important;
}


/* Main cards */

.gr-group,
.gr-box,
.block,
form {
    background: #ffffff !important;
    color: #000000 !important;
}


/* All text */

.gradio-container h1,
.gradio-container h2,
.gradio-container h3,
.gradio-container h4,
.gradio-container p,
.gradio-container span,
.gradio-container label,
.gradio-container .prose,
.gradio-container .gr-markdown {
    color: #000000 !important;
}


/* Inputs */

.gradio-container input,
.gradio-container textarea {
    background: #ffffff !important;
    color: #000000 !important;
    border-color: #d1d5db !important;
}


/* Placeholder */

.gradio-container input::placeholder,
.gradio-container textarea::placeholder {
    color: #6b7280 !important;
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
    color: white !important;
}


/* ============================================================
   THEME BUTTON
   ============================================================ */

#theme-toggle-btn {
    background: rgba(255, 255, 255, 0.20) !important;

    border: 1px solid rgba(
        255,
        255,
        255,
        0.50
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
   OUTPUT BOX
   ============================================================ */

#output-box {
    min-height: 460px !important;

    max-height: 560px !important;

    overflow-y: auto !important;

    padding: 12px !important;

    background: #ffffff !important;

    color: #000000 !important;
}


/* ============================================================
   ANALYZE BUTTON
   ============================================================ */

#analyze-button {
    min-height: 44px !important;

    font-size: 15px !important;

    font-weight: 700 !important;

    margin-top: 8px !important;
}


/* ============================================================
   PRIVACY NOTE
   ============================================================ */

#privacy-note {
    font-size: 11px !important;

    text-align: center !important;

    margin-top: 8px !important;

    color: #000000 !important;
}


/* ============================================================
   DARK MODE
   PURE BLACK BACKGROUND + WHITE TEXT
   ============================================================ */

html.cb-dark,
html.cb-dark body {
    background: #000000 !important;
}


html.cb-dark .gradio-container {
    background: #000000 !important;
    color: #ffffff !important;
}


/* Main cards */

html.cb-dark .gr-group,
html.cb-dark .gr-box,
html.cb-dark .block,
html.cb-dark form {
    background: #000000 !important;
    color: #ffffff !important;

    border-color: #ffffff !important;
}


/* All text */

html.cb-dark .gradio-container h1,
html.cb-dark .gradio-container h2,
html.cb-dark .gradio-container h3,
html.cb-dark .gradio-container h4,
html.cb-dark .gradio-container p,
html.cb-dark .gradio-container span,
html.cb-dark .gradio-container label,
html.cb-dark .gradio-container .prose,
html.cb-dark .gradio-container .gr-markdown {
    color: #ffffff !important;
}


/* Inputs */

html.cb-dark .gradio-container input,
html.cb-dark .gradio-container textarea {
    background: #000000 !important;

    color: #ffffff !important;

    border-color: #ffffff !important;
}


/* Placeholder */

html.cb-dark .gradio-container input::placeholder,
html.cb-dark .gradio-container textarea::placeholder {
    color: #bdbdbd !important;
}


/* Output */

html.cb-dark #output-box {
    background: #000000 !important;

    color: #ffffff !important;
}


/* Privacy note */

html.cb-dark #privacy-note,
html.cb-dark #privacy-note * {
    color: #ffffff !important;
}


/* Header remains purple */

html.cb-dark #header-banner {
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


/* ============================================================
   MOBILE RESPONSIVE
   ============================================================ */

@media (max-width: 768px) {

    .gradio-container {
        padding: 8px !important;
    }

    #header-banner {
        padding: 12px !important;
    }

    #header-text h1 {
        font-size: 20px !important;
    }

    #header-text p {
        font-size: 10px !important;
    }

    #output-box {
        min-height: 400px !important;
        max-height: none !important;
    }
}

"""


# ============================================================
# GRADIO THEME
# ============================================================

custom_theme = gr.themes.Soft(
    primary_hue="violet"
)


# ============================================================
# CREATE APP
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
        fn=None,
        inputs=None,
        outputs=None,

        js="""
        () => {

            document.documentElement.classList.toggle(
                "cb-dark"
            );

        }
        """
    )


    # ========================================================
    # MAIN CONTENT
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
    # ANALYZE BUTTON EVENT
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
# RUN APP
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
