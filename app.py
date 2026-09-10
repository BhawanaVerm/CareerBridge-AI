import os
import gradio as gr
from google import genai
from pypdf import PdfReader


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable is not configured."
    )

client = genai.Client(api_key=api_key)


# ============================================================
# RESUME TEXT EXTRACTION
# ============================================================

def extract_resume_text(pdf_file):
    """
    Extract text from uploaded PDF resume.
    Returns extracted text or an error message.
    """

    if pdf_file is None:
        return ""

    try:
        reader = PdfReader(pdf_file.name)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        text = text.strip()

        if not text:
            return (
                "⚠️ The uploaded PDF does not contain readable text. "
                "Please upload a text-based PDF resume."
            )

        return text

    except Exception as e:
        return f"⚠️ There was an issue reading the resume: {str(e)}"


# ============================================================
# GEMINI CAREER ANALYSIS
# ============================================================

def analyze_career_profile(user_background_text):

    prompt = f"""
You are an expert career advisor helping professionals,
especially women returning to work after a career break.

Analyze the person's career background carefully.

Here is the person's information:

{user_background_text}

Provide practical, realistic and encouraging career guidance.

Use the following structure:

## 💪 Key Strengths
Give 2-3 strengths based specifically on the person's experience,
skills, certifications and background.

## 📚 Skill Gaps
Give 2-3 important skill gaps that matter for today's job market.
Do not recommend unnecessary skills.

## 🎯 Recommended Job Roles
Recommend 3 realistic job roles.

For each role include:
- Role name
- Why it fits the person's background
- Important skills needed

## 🚀 Recommended Next Steps
Give 3 practical steps the person should take next.

## 📝 Resume / Profile Suggestions
Give 2-3 suggestions for improving their resume or professional profile.

Important:
- Be realistic.
- Do not discourage the person because of the career gap.
- Do not assume skills that are not mentioned.
- Prefer roles that match their existing experience.
- Keep the language simple and easy to understand.
- Avoid unnecessary technical jargon.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ============================================================
# MAIN CAREER ADVISOR FUNCTION
# ============================================================

def gradio_career_advisor(
    experience,
    career_gap,
    field,
    desired_role,
    skills_background,
    pdf_file
):

    # --------------------------------------------------------
    # Read uploaded resume
    # --------------------------------------------------------

    resume_text = extract_resume_text(pdf_file)

    # --------------------------------------------------------
    # Decide whether to use Resume or Manual Background
    # --------------------------------------------------------

    if resume_text.startswith("⚠️"):

        # If resume has an error but manual background exists,
        # use the manual background instead.
        if skills_background and skills_background.strip():
            final_background = skills_background.strip()
        else:
            yield resume_text
            return

    else:

        if resume_text.strip():
            final_background = resume_text.strip()

        elif skills_background and skills_background.strip():
            final_background = skills_background.strip()

        else:
            yield (
                "⚠️ **Please upload your resume PDF, "
                "or enter your skills/background manually.**"
            )
            return

    # --------------------------------------------------------
    # Loading message
    # --------------------------------------------------------

    yield (
        "⏳ **Preparing your personalized career advice...**\n\n"
        "Please wait a few seconds."
    )

    # --------------------------------------------------------
    # Combine all information
    # --------------------------------------------------------

    combined_input = f"""
Years of Experience: {experience if experience else "Not specified"}

Career Gap Duration: {career_gap if career_gap else "Not specified"}

Field / Industry: {field if field else "Not specified"}

Desired Role: {desired_role if desired_role else "Not specified"}

--------------------------------------------------
BACKGROUND / SKILLS / RESUME DETAILS
--------------------------------------------------

{final_background}
"""

    # --------------------------------------------------------
    # Call Gemini safely
    # --------------------------------------------------------

    try:

        result = analyze_career_profile(combined_input)

        if not result or not result.strip():
            yield (
                "⚠️ **No career advice was generated.**\n\n"
                "Please try again."
            )
            return

        yield result

    except Exception as e:

        yield f"""
### ⚠️ Something went wrong

I couldn't generate your career advice right now.

Please try again in a few seconds.

**Possible reasons:**
- Temporary Gemini API issue
- API quota limit
- Network problem

Please try again later.
"""


# ============================================================
# CUSTOM THEME
# ============================================================

custom_theme = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="pink",
    font=[
        gr.themes.GoogleFont("Poppins"),
        "ui-sans-serif",
        "sans-serif"
    ],
)


# ============================================================
# CUSTOM CSS
# ============================================================

custom_css = """

/* =========================================================
   GLOBAL DESKTOP LAYOUT
   ========================================================= */

.gradio-container {
    max-width: 1180px !important;
    margin: auto !important;
    padding-top: 12px !important;
    padding-bottom: 10px !important;
}


/* =========================================================
   HEADER
   ========================================================= */

#header-banner {

    position: relative;

    background: linear-gradient(
        135deg,
        #7c3aed 0%,
        #db2777 100%
    );

    border-radius: 16px;

    padding: 16px 24px 17px 24px;

    margin-bottom: 12px;

    box-shadow:
        0 6px 20px rgba(124, 58, 237, 0.22);
}


#header-banner h1,
#header-banner h3,
#header-banner p {

    color: #ffffff !important;
}


#header-banner h1 {

    margin-top: 0 !important;
    margin-bottom: 2px !important;

    font-size: 1.85rem !important;
    line-height: 1.2 !important;
}


#header-banner h3 {

    font-weight: 500 !important;

    opacity: 0.95;

    margin-top: 0 !important;
    margin-bottom: 5px !important;

    font-size: 1rem !important;

    line-height: 1.3 !important;
}


#header-banner p {

    opacity: 0.9;

    margin: 0 !important;

    font-size: 0.88rem !important;

    line-height: 1.4 !important;
}


/* =========================================================
   THEME BUTTON
   ========================================================= */

#theme-toggle-wrap {

    position: absolute !important;

    top: 12px;
    right: 14px;

    z-index: 50 !important;
}


#theme-toggle-wrap button {

    background: rgba(255,255,255,0.15) !important;

    border: 1px solid rgba(255,255,255,0.4) !important;

    color: #ffffff !important;

    border-radius: 20px !important;

    padding: 7px 14px !important;

    font-size: 0.78em !important;

    font-family: inherit;

    cursor: pointer !important;

    touch-action: manipulation;

    white-space: nowrap;
}


#theme-toggle-wrap button:hover {

    background: rgba(255,255,255,0.28) !important;
}


/* =========================================================
   CARDS
   ========================================================= */

.card-section {

    background: var(--background-fill-primary);

    color: var(--body-text-color);

    border-radius: 14px;

    padding: 10px 16px !important;

    margin-bottom: 10px;

    box-shadow:
        0 2px 8px rgba(0,0,0,0.05);

    border: 1px solid var(--border-color-primary);
}


.card-section h4 {

    margin-top: 0 !important;
    margin-bottom: 6px !important;

    font-size: 0.98rem !important;
}


.card-section p,
.card-section span {

    color: var(--body-text-color) !important;
}


.section-title {

    font-weight: 600 !important;

    margin-bottom: 3px !important;
}


/* =========================================================
   INPUT BOXES
   ========================================================= */

.card-section input,
.card-section textarea {

    min-height: 40px !important;
}


.card-section label {

    font-size: 0.82rem !important;
}


/* =========================================================
   RESUME UPLOAD
   ========================================================= */

#compact-upload {

    min-height: 78px !important;
}


#compact-upload .wrap {

    min-height: 78px !important;

    padding: 6px !important;
}


#compact-upload .file-preview {

    min-height: 50px !important;
}


/* =========================================================
   SUBMIT BUTTON
   ========================================================= */

#submit-btn {

    border-radius: 11px !important;

    font-weight: 600 !important;

    letter-spacing: 0.2px;

    box-shadow:
        0 4px 12px rgba(147, 51, 234, 0.28);

    min-height: 44px !important;
}


/* =========================================================
   OUTPUT COLUMN
   ========================================================= */

#output-column {

    position: sticky;

    top: 12px;

    align-self: flex-start;

    max-height: calc(100vh - 24px);
}


#output-card {

    background: var(--background-fill-primary);

    color: var(--body-text-color);

    border-radius: 14px;

    padding: 15px 17px 6px 17px;

    box-shadow:
        0 2px 12px rgba(0,0,0,0.07);

    border: 1px solid var(--border-color-primary);

    display: flex;

    flex-direction: column;

    max-height: calc(100vh - 24px);

    overflow: hidden;
}


#output-heading {

    flex-shrink: 0;

    margin-bottom: 3px;
}


#output-heading h4 {

    margin: 0 !important;

    color: #a855f7;
}


#output-scroll {

    overflow-y: auto;

    min-height: 160px;

    padding-bottom: 10px;
}


/* =========================================================
   OUTPUT MARKDOWN
   ========================================================= */

#output-scroll h2,
#output-scroll h3 {

    margin-top: 10px !important;
    margin-bottom: 5px !important;
}


#output-scroll p {

    margin-top: 4px !important;
    margin-bottom: 6px !important;

    line-height: 1.45 !important;
}


#output-scroll ul {

    margin-top: 4px !important;
    margin-bottom: 7px !important;
}


/* =========================================================
   PRIVACY NOTE
   ========================================================= */

#privacy-note {

    font-size: 0.72rem !important;

    opacity: 0.68;

    margin-top: 2px !important;

    margin-bottom: 8px !important;
}


/* =========================================================
   FOOTER
   ========================================================= */

#footer-note {

    text-align: center;

    margin-top: 8px;

    opacity: 0.6;

    font-size: 0.72em;
}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 768px) {

    .gradio-container {

        max-width: 100% !important;

        padding:
            8px 8px 12px 8px !important;
    }


    /* Header */

    #header-banner {

        padding:
            64px 16px 18px 16px !important;

        border-radius: 15px;

        margin-bottom: 10px;
    }


    #header-banner h1 {

        font-size: 1.65rem !important;

        line-height: 1.2 !important;

        margin-bottom: 4px !important;
    }


    #header-banner h3 {

        font-size: 0.95rem !important;

        line-height: 1.35 !important;

        margin-bottom: 7px !important;
    }


    #header-banner p {

        font-size: 0.82rem !important;

        line-height: 1.45 !important;
    }


    /* Theme button */

    #theme-toggle-wrap {

        top: 11px;

        right: 11px;
    }


    #theme-toggle-wrap button {

        padding:
            8px 13px !important;

        font-size: 0.76em !important;
    }


    /* Cards */

    .card-section {

        padding:
            11px 12px !important;

        margin-bottom: 9px;

        border-radius: 13px;
    }


    /* Inputs */

    .card-section input,
    .card-section textarea {

        min-height: 42px !important;
    }


    /* Resume */

    #compact-upload {

        min-height: 95px !important;
    }


    #compact-upload .wrap {

        min-height: 95px !important;

        padding: 6px !important;
    }


    /* Submit */

    #submit-btn {

        min-height: 46px !important;

        margin-top: 2px !important;
    }


    /* Output */

    #output-column {

        position: static !important;

        max-height: none !important;

        margin-top: 10px !important;
    }


    #output-card {

        max-height: none !important;

        overflow: visible !important;

        padding:
            14px 14px 6px 14px !important;
    }


    #output-scroll {

        max-height: none !important;

        overflow-y: visible !important;

        min-height: 160px;
    }


    #footer-note {

        margin-top: 8px;

        font-size: 0.7em;
    }
}


/* =========================================================
   VERY SMALL MOBILE
   ========================================================= */

@media (max-width: 420px) {

    #header-banner h1 {

        font-size: 1.48rem !important;
    }


    #header-banner h3 {

        font-size: 0.88rem !important;
    }


    #header-banner p {

        font-size: 0.78rem !important;
    }


    #theme-toggle-wrap button {

        padding:
            7px 11px !important;

        font-size: 0.72em !important;
    }
}

"""


# ============================================================
# GRADIO APP
# ============================================================

with gr.Blocks(
    title="CareerBridge AI",
    theme=custom_theme,
    css=custom_css
) as demo:

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    with gr.Column(elem_id="header-banner"):

        gr.HTML(
            """
            <div id="theme-toggle-wrap">

                <button onclick="toggleCareerTheme()">
                    🌙 / ☀️ Theme
                </button>

            </div>

            <script>

            function toggleCareerTheme() {

                const url = new URL(window.location.href);

                let currentTheme =
                    url.searchParams.get("__theme");

                if (!currentTheme) {

                    currentTheme =
                        window.matchMedia(
                            "(prefers-color-scheme: dark)"
                        ).matches
                        ? "dark"
                        : "light";
                }

                const nextTheme =
                    currentTheme === "dark"
                    ? "light"
                    : "dark";

                url.searchParams.set(
                    "__theme",
                    nextTheme
                );

                window.location.href =
                    url.toString();
            }


            /*
             * If no theme is explicitly selected,
             * start with LIGHT mode.
             *
             * This prevents mobile devices using
             * system dark mode from forcing the
             * application into dark mode.
             */

            (function () {

                const url =
                    new URL(window.location.href);

                if (
                    !url.searchParams.get("__theme")
                ) {

                    url.searchParams.set(
                        "__theme",
                        "light"
                    );

                    window.history.replaceState(
                        {},
                        "",
                        url.toString()
                    );
                }

            })();

            </script>
            """
        )

        gr.Markdown(
            """
            # 🌉 CareerBridge AI

            ### Your personal guide back to the workforce, powered by Google Gemini

            Returning to work after a break can feel overwhelming.
            Share a bit about yourself and get instant, personalized
            career guidance — your strengths, skill gaps, and best-fit roles.
            """
        )


    # --------------------------------------------------------
    # MAIN ROW
    # --------------------------------------------------------

    with gr.Row(equal_height=False):


        # ====================================================
        # LEFT SIDE
        # ====================================================

        with gr.Column(scale=3):


            # ------------------------------------------------
            # CAREER DETAILS
            # ------------------------------------------------

            with gr.Column(
                elem_classes="card-section"
            ):

                gr.Markdown(
                    "#### 👤 Tell us about your career so far",
                    elem_classes="section-title"
                )

                with gr.Row():

                    experience = gr.Textbox(
                        label="💼 Experience (years)",
                        placeholder="e.g. 4 years"
                    )

                    career_gap = gr.Textbox(
                        label="⏳ Career Gap Duration",
                        placeholder="e.g. 5 years"
                    )


                with gr.Row():

                    field = gr.Textbox(
                        label="🏢 Field / Industry",
                        placeholder="e.g. IT, Cloud, AI"
                    )

                    desired_role = gr.Textbox(
                        label="🎯 Desired Role (optional)",
                        placeholder="e.g. Cloud Engineer"
                    )


            # ------------------------------------------------
            # BACKGROUND / RESUME
            # ------------------------------------------------

            with gr.Column(
                elem_classes="card-section"
            ):

                gr.Markdown(
                    "#### 📄 Share your background",
                    elem_classes="section-title"
                )


                with gr.Tabs():

                    # ----------------------------------------
                    # UPLOAD RESUME
                    # ----------------------------------------

                    with gr.Tab("📎 Upload Resume"):

                        pdf_input = gr.File(
                            label="Resume Upload (PDF only)",
                            file_types=[".pdf"],
                            elem_id="compact-upload"
                        )


                    # ----------------------------------------
                    # MANUAL INPUT
                    # ----------------------------------------

                    with gr.Tab("✍️ Type it in"):

                        skills_background = gr.Textbox(
                            label="Describe your skills and background",

                            placeholder=(
                                "Certifications, key skills, "
                                "previous responsibilities, "
                                "achievements..."
                            ),

                            lines=4
                        )


                gr.Markdown(
                    """
                    🔒 **Privacy Note:** Your resume is used only to
                    generate personalized career guidance.
                    Please avoid uploading unnecessary sensitive information.
                    """,
                    elem_id="privacy-note"
                )


            # ------------------------------------------------
            # BUTTON
            # ------------------------------------------------

            submit_btn = gr.Button(
                "✨ Get My Career Advice",
                variant="primary",
                size="lg",
                elem_id="submit-btn"
            )


        # ====================================================
        # RIGHT SIDE
        # ====================================================

        with gr.Column(
            scale=2,
            elem_id="output-column"
        ):

            with gr.Column(
                elem_id="output-card"
            ):

                gr.Markdown(
                    "#### 💡 Your Career Advice",
                    elem_id="output-heading"
                )


                with gr.Column(
                    elem_id="output-scroll"
                ):

                    output = gr.Markdown(
                        """
                        Fill in your details on the left and click
                        **Get My Career Advice** — your personalized
                        guidance will appear here.
                        """
                    )


    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    gr.Markdown(
        "Built with ❤️ for career returners · Powered by Google Gemini",
        elem_id="footer-note"
    )


    # ========================================================
    # BUTTON ACTION
    # ========================================================

    submit_btn.click(

        fn=gradio_career_advisor,

        inputs=[
            experience,
            career_gap,
            field,
            desired_role,
            skills_background,
            pdf_input
        ],

        outputs=output,

        scroll_to_output=False
    )


# ============================================================
# QUEUE
# ============================================================

demo.queue()


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )
