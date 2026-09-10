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

Analyze the candidate's profile realistically and provide practical,
encouraging and honest career guidance.

Do NOT give generic motivational advice.

Candidate information:

Total Experience:
{experience}

Career Gap:
{career_gap}

Current / Previous Field:
{field}

Desired Role:
{desired_role}

{background_section}

{resume_section}


Please provide your answer using the following structure:

## 1. Career Profile Summary

Briefly summarize the candidate's current profile.

## 2. Strengths

Mention the candidate's strongest technical, professional,
transferable or domain skills.

## 3. Career Gap Impact

Explain honestly how the career gap may affect job searching
and how the candidate can handle it.

## 4. Suitable Job Roles

Suggest 4 to 6 realistic job roles.

For every role explain:

- Why it fits
- Important skills
- Difficulty level
- What the candidate should learn or revise

## 5. Skill Gap

Clearly separate:

### Already Useful
Skills the candidate already appears to have.

### Need Improvement
Skills that should be strengthened.

### Optional / Future
Skills that are useful but should not be the immediate priority.

## 6. 30-Day Action Plan

Create a practical 30-day plan.

Break it into:

Week 1
Week 2
Week 3
Week 4

Keep the plan realistic for someone returning after a career break.

## 7. Resume Suggestions

Give specific suggestions for improving the resume.

Focus on:

- Career gap explanation
- Skills
- Projects
- Certifications
- ATS keywords
- Professional summary

## 8. Interview Preparation

Suggest the most important interview topics for the target role.

Also give 5 likely interview questions.

## 9. Job Search Strategy

Give practical advice about:

- Job portals
- LinkedIn
- Recruiters
- Referrals
- Returnship programs
- Direct company applications

## 10. Final Recommendation

Give a realistic conclusion.

Mention:

- Best immediate career direction
- Top 3 skills to prioritize
- What the candidate should NOT waste time learning right now

Use simple, clear English.

Be supportive but realistic.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response is None:
            return (
                "⚠️ Gemini did not return a response. "
                "Please try again."
            )

        result = response.text

        if not result:
            return (
                "⚠️ Gemini returned an empty response. "
                "Please try again."
            )

        return result

    except Exception as e:

        return (
            "## ⚠️ Unable to generate career analysis\n\n"
            f"**Error:** {str(e)}\n\n"
            "Please check your Gemini API configuration and try again."
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

    # Read uploaded resume
    if resume_file is not None:

        resume_text = extract_resume_text(resume_file)

        if resume_text.startswith("⚠️"):
            return resume_text

    # Basic validation
    if (
        not experience
        and not field
        and not desired_role
        and not resume_text
    ):

        return (
            "## ⚠️ Please provide some information first\n\n"
            "Please enter your experience, field, desired role, "
            "or upload your resume."
        )

    # Generate analysis
    return analyze_career_profile(
        experience=experience,
        career_gap=career_gap,
        field=field,
        desired_role=desired_role,
        background=background,
        resume_text=resume_text
    )


# ============================================================
# GRADIO THEME
# ============================================================

custom_theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="slate",
    neutral_hue="slate"
)


# ============================================================
# CUSTOM CSS
# ============================================================

custom_css = r"""

/* ============================================================
   GLOBAL LIGHT / DARK CONTROL
   ============================================================ */

html:not(.careerbridge-dark) {
    color-scheme: light !important;
}

html.careerbridge-dark {
    color-scheme: dark !important;
}


/* ============================================================
   LIGHT THEME
   ============================================================ */

.gradio-container {

    --body-background-fill: #f8fafc !important;

    --body-text-color: #1f2937 !important;

    --body-text-color-subdued: #64748b !important;

    --background-fill-primary: #ffffff !important;

    --background-fill-secondary: #f8fafc !important;

    --block-background-fill: #ffffff !important;

    --panel-background-fill: #ffffff !important;

    --input-background-fill: #ffffff !important;

    --input-border-color: #d1d5db !important;

    --border-color-primary: #e5e7eb !important;

    --button-secondary-background-fill: #f8fafc !important;

    max-width: 1180px !important;

    margin: 0 auto !important;

    padding: 10px 14px 14px 14px !important;
}


/* ============================================================
   DARK THEME
   ============================================================ */

html.careerbridge-dark .gradio-container {

    --body-background-fill: #080d18 !important;

    --body-text-color: #f8fafc !important;

    --body-text-color-subdued: #cbd5e1 !important;

    --background-fill-primary: #0f172a !important;

    --background-fill-secondary: #111827 !important;

    --block-background-fill: #111827 !important;

    --panel-background-fill: #0f172a !important;

    --input-background-fill: #1e293b !important;

    --input-border-color: #475569 !important;

    --border-color-primary: #334155 !important;

    --button-secondary-background-fill: #1e293b !important;
}


/* ============================================================
   PAGE BACKGROUND
   ============================================================ */

html:not(.careerbridge-dark) body,
html:not(.careerbridge-dark) .gradio-container {

    background: #f8fafc !important;

    color: #1f2937 !important;
}


html.careerbridge-dark body,
html.careerbridge-dark .gradio-container {

    background: #080d18 !important;

    color: #f8fafc !important;
}


/* ============================================================
   HEADER
   ============================================================ */

#header-banner {

    position: relative !important;

    padding: 14px 24px 16px 24px !important;

    border-radius: 18px !important;

    margin-bottom: 10px !important;

    background:
        linear-gradient(
            135deg,
            #6d28d9 0%,
            #7c3aed 45%,
            #9333ea 100%
        ) !important;

    color: white !important;

    box-shadow:
        0 8px 22px rgba(76, 29, 149, 0.18) !important;
}


#header-banner h1 {

    margin: 0 !important;

    font-size: 30px !important;

    line-height: 1.15 !important;

    font-weight: 800 !important;

    color: white !important;
}


#header-banner p {

    margin: 4px 0 0 0 !important;

    font-size: 14px !important;

    line-height: 1.35 !important;

    color: rgba(255,255,255,0.92) !important;
}


/* ============================================================
   THEME BUTTON
   ============================================================ */

#theme-toggle-wrap {

    position: absolute !important;

    top: 10px !important;

    right: 12px !important;

    z-index: 100 !important;
}


#theme-toggle-wrap button {

    border: 1px solid rgba(255,255,255,0.35) !important;

    border-radius: 999px !important;

    background: rgba(255,255,255,0.16) !important;

    color: white !important;

    padding: 7px 13px !important;

    font-size: 12px !important;

    font-weight: 600 !important;

    cursor: pointer !important;

    backdrop-filter: blur(8px) !important;

    transition:
        background 0.2s ease,
        transform 0.2s ease !important;
}


#theme-toggle-wrap button:hover {

    background: rgba(255,255,255,0.26) !important;

    transform: translateY(-1px) !important;
}


/* ============================================================
   CARDS
   ============================================================ */

.card-section {

    background: #ffffff !important;

    border: 1px solid #e5e7eb !important;

    border-radius: 14px !important;

    padding: 10px 12px !important;

    margin-bottom: 9px !important;

    box-shadow:
        0 2px 8px rgba(15, 23, 42, 0.04) !important;
}


html.careerbridge-dark .card-section {

    background: #111827 !important;

    border-color: #334155 !important;

    box-shadow:
        0 3px 12px rgba(0,0,0,0.22) !important;
}


/* ============================================================
   SECTION TITLES
   ============================================================ */

.section-title {

    font-size: 16px !important;

    font-weight: 750 !important;

    margin: 0 0 6px 0 !important;

    color: #1f2937 !important;
}


html.careerbridge-dark .section-title {

    color: #f8fafc !important;
}


/* ============================================================
   LABELS
   ============================================================ */

.gradio-container label {

    font-size: 12px !important;

    font-weight: 650 !important;
}


/* ============================================================
   LIGHT INPUTS
   ============================================================ */

html:not(.careerbridge-dark)
.gradio-container input,
html:not(.careerbridge-dark)
.gradio-container textarea {

    background: #ffffff !important;

    color: #1f2937 !important;

    border-color: #d1d5db !important;
}


/* ============================================================
   DARK INPUTS
   ============================================================ */

html.careerbridge-dark
.gradio-container input,
html.careerbridge-dark
.gradio-container textarea {

    background: #1e293b !important;

    color: #f8fafc !important;

    border-color: #475569 !important;
}


html.careerbridge-dark
.gradio-container input::placeholder,
html.careerbridge-dark
.gradio-container textarea::placeholder {

    color: #94a3b8 !important;
}


/* ============================================================
   DARK DROPDOWNS
   ============================================================ */

html.careerbridge-dark
.gradio-container select {

    background: #1e293b !important;

    color: #f8fafc !important;

    border-color: #475569 !important;
}


/* ============================================================
   RESUME UPLOAD
   ============================================================ */

#compact-upload {

    background: #ffffff !important;

    border-radius: 12px !important;

    border: 1px dashed #cbd5e1 !important;

    min-height: 76px !important;
}


html.careerbridge-dark #compact-upload {

    background: #111827 !important;

    border-color: #475569 !important;

    color: #f8fafc !important;
}


/* ============================================================
   TABS
   ============================================================ */

.gradio-container [role="tab"] {

    font-size: 13px !important;

    font-weight: 650 !important;
}


html.careerbridge-dark
.gradio-container [role="tab"] {

    color: #cbd5e1 !important;
}


html.careerbridge-dark
.gradio-container [role="tab"][aria-selected="true"] {

    color: #c4b5fd !important;
}


/* ============================================================
   OUTPUT CARD
   ============================================================ */

#output-card {

    background: #ffffff !important;

    border: 1px solid #e5e7eb !important;

    border-radius: 14px !important;

    padding: 10px 14px !important;

    min-height: 250px !important;

    box-shadow:
        0 2px 8px rgba(15, 23, 42, 0.04) !important;
}


html.careerbridge-dark #output-card {

    background: #111827 !important;

    border-color: #334155 !important;

    color: #f8fafc !important;
}


/* ============================================================
   OUTPUT AREA
   ============================================================ */

#output-scroll {

    max-height: 570px !important;

    overflow-y: auto !important;

    padding-right: 5px !important;
}


#output-scroll h1,
#output-scroll h2,
#output-scroll h3 {

    margin-top: 8px !important;

    margin-bottom: 5px !important;
}


html.careerbridge-dark #output-scroll,
html.careerbridge-dark #output-scroll p,
html.careerbridge-dark #output-scroll li {

    color: #e5e7eb !important;
}


html.careerbridge-dark #output-scroll strong {

    color: #ffffff !important;
}


/* ============================================================
   ANALYZE BUTTON
   ============================================================ */

#analyze-button {

    min-height: 42px !important;

    border-radius: 10px !important;

    font-size: 14px !important;

    font-weight: 700 !important;
}


/* ============================================================
   PRIVACY NOTE
   ============================================================ */

#privacy-note {

    text-align: center !important;

    font-size: 10px !important;

    color: #64748b !important;

    margin-top: 3px !important;
}


html.careerbridge-dark #privacy-note {

    color: #94a3b8 !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

#footer-note {

    text-align: center !important;

    font-size: 10px !important;

    color: #64748b !important;

    padding: 3px 0 !important;
}


html.careerbridge-dark #footer-note {

    color: #94a3b8 !important;
}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 768px) {

    .gradio-container {

        padding:
            7px
            9px
            10px
            9px !important;

        max-width: 100% !important;
    }


    /* Reduced from 64px to 44px.
       This removes the extra blank space above the title. */

    #header-banner {

        padding:
            44px
            16px
            17px
            16px !important;

        border-radius: 15px !important;

        margin-bottom: 8px !important;
    }


    #header-banner h1 {

        font-size: 25px !important;

        line-height: 1.15 !important;
    }


    #header-banner p {

        font-size: 12px !important;

        line-height: 1.35 !important;

        margin-top: 4px !important;
    }


    #theme-toggle-wrap {

        top: 9px !important;

        right: 9px !important;
    }


    #theme-toggle-wrap button {

        padding:
            7px
            11px !important;

        font-size: 11px !important;
    }


    .card-section {

        padding:
            9px
            9px !important;

        margin-bottom: 7px !important;

        border-radius: 12px !important;
    }


    .section-title {

        font-size: 15px !important;

        margin-bottom: 5px !important;
    }


    .gradio-container label {

        font-size: 11px !important;
    }


    #compact-upload {

        min-height: 68px !important;
    }


    #output-card {

        padding:
            9px
            10px !important;

        min-height: 220px !important;
    }


    #output-scroll {

        max-height: 520px !important;
    }


    #analyze-button {

        min-height: 44px !important;

        font-size: 14px !important;
    }


    #privacy-note {

        font-size: 9px !important;
    }
}


/* ============================================================
   VERY SMALL MOBILE
   ============================================================ */

@media (max-width: 420px) {

    #header-banner {

        padding:
            42px
            13px
            15px
            13px !important;
    }


    #header-banner h1 {

        font-size: 23px !important;
    }


    #header-banner p {

        font-size: 11px !important;
    }


    #theme-toggle-wrap button {

        padding:
            6px
            9px !important;

        font-size: 10px !important;
    }
}

"""


# ============================================================
# GRADIO APP
# ============================================================

with gr.Blocks(
    theme=custom_theme,
    css=custom_css,
    title="CareerBridge AI"
) as demo:


    # ========================================================
    # HEADER
    # ========================================================

    gr.HTML(
        """
        <div id="header-banner">

            <div id="theme-toggle-wrap">

                <button
                    type="button"
                    aria-label="Toggle light and dark theme"
                    onclick="
                        const root = document.documentElement;

                        const dark =
                            !root.classList.contains(
                                'careerbridge-dark'
                            );

                        root.classList.toggle(
                            'careerbridge-dark',
                            dark
                        );

                        try {
                            localStorage.setItem(
                                'careerbridge-theme',
                                dark ? 'dark' : 'light'
                            );
                        } catch(e) {}
                    "
                >
                    🌙 / ☀️ Theme
                </button>

            </div>

            <h1>CareerBridge AI</h1>

            <p>
                AI-powered career guidance for professionals
                returning to work after a career break.
            </p>

        </div>
        """
    )


    # ========================================================
    # CAREER PROFILE
    # ========================================================

    with gr.Group(elem_classes="card-section"):

        gr.HTML(
            """
            <div class="section-title">
                👤 Your Career Profile
            </div>
            """
        )

        with gr.Row():

            with gr.Column(scale=1):

                experience = gr.Textbox(
                    label="Total Experience",
                    placeholder="Example: 4 years",
                    lines=1
                )

            with gr.Column(scale=1):

                career_gap = gr.Textbox(
                    label="Career Gap",
                    placeholder="Example: 5 years",
                    lines=1
                )


        with gr.Row():

            with gr.Column(scale=1):

                field = gr.Textbox(
                    label="Current / Previous Field",
                    placeholder="Example: Cloud / IT",
                    lines=1
                )

            with gr.Column(scale=1):

                desired_role = gr.Textbox(
                    label="Desired Role",
                    placeholder="Example: Cloud Engineer",
                    lines=1
                )


    # ========================================================
    # BACKGROUND
    # ========================================================

    with gr.Group(elem_classes="card-section"):

        gr.HTML(
            """
            <div class="section-title">
                📝 Your Background
            </div>
            """
        )

        background = gr.Textbox(
            label="Tell us about your skills, certifications, projects or career goals",
            placeholder=(
                "Example: GCP certified, Cloud Run project, "
                "GenAI project, Terraform learning..."
            ),
            lines=3
        )


    # ========================================================
    # RESUME UPLOAD
    # ========================================================

    with gr.Group(elem_classes="card-section"):

        gr.HTML(
            """
            <div class="section-title">
                📄 Upload Your Resume
            </div>
            """
        )

        resume_file = gr.File(
            label="Upload PDF Resume",
            file_types=[".pdf"],
            type="filepath",
            elem_id="compact-upload"
        )


    # ========================================================
    # ANALYZE BUTTON
    # ========================================================

    analyze_button = gr.Button(
        "🚀 Analyze My Career",
        variant="primary",
        elem_id="analyze-button"
    )


    # ========================================================
    # OUTPUT
    # ========================================================

    with gr.Group(elem_id="output-card"):

        gr.HTML(
            """
            <div class="section-title">
                💡 CareerBridge AI Analysis
            </div>
            """
        )

        output = gr.Markdown(
            value=(
                "Your personalized career analysis "
                "will appear here."
            ),
            elem_id="output-scroll"
        )


    # ========================================================
    # PRIVACY NOTE
    # ========================================================

    gr.Markdown(
        "🔒 Your resume is used only to generate this career analysis.",
        elem_id="privacy-note"
    )


    # ========================================================
    # FOOTER
    # ========================================================

    gr.Markdown(
        "CareerBridge AI • Built to support career comeback journeys",
        elem_id="footer-note"
    )


    # ========================================================
    # ANALYZE BUTTON ACTION
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
            os.environ.get("PORT", 7860)
        )
    )
