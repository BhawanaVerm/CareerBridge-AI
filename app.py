import os
import gradio as gr
from google import genai
from pypdf import PdfReader

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def extract_resume_text(pdf_file):
    """Extracts text from the PDF. Returns an empty or error string if the file is missing or unreadable."""
    if pdf_file is None:
        return ""
    try:
        reader = PdfReader(pdf_file.name)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"⚠️ There was an issue reading the resume: {str(e)}"


def analyze_career_profile(user_background_text):
    prompt = f"""
    You are a career advisor helping women professionals returning to work after a career break.
    Here is the person's background and skills:
    {user_background_text}

    Please provide:
    1. Their key strengths (2-3 points)
    2. Skill gaps they should address for today's job market (2-3 points)
    3. Three relevant job roles they could target

    Keep the response clear, encouraging, and structured with headings.
    """
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text


def gradio_career_advisor(experience, career_gap, field, desired_role, skills_background, pdf_file):
    resume_text = extract_resume_text(pdf_file)

    # Resume takes priority if uploaded, otherwise fall back to the manual text box
    final_background = resume_text if resume_text.strip() else skills_background

    if not final_background or not final_background.strip():
        yield "⚠️ Please upload your resume PDF, or enter your skills/background below."
        return

    yield "⏳ **Preparing your personalized career advice... please wait a few seconds.**"

    combined_input = f"""
    Years of Experience: {experience}
    Career Gap Duration: {career_gap}
    Field/Industry: {field}
    Desired Role: {desired_role if desired_role else 'Not specified'}

    --- BACKGROUND / SKILLS / RESUME DETAILS ---
    {final_background}
    """

    result = analyze_career_profile(combined_input)
    yield result


custom_theme = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="pink",
    font=[gr.themes.GoogleFont("Poppins"), "ui-sans-serif", "sans-serif"],
)

custom_css = """
.gradio-container {
    max-width: 1150px !important;
    margin: auto !important;
}

#header-banner {
    position: relative;
    background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.25);
}

#theme-toggle-btn {
    position: absolute !important;
    top: 16px;
    right: 16px;
    width: auto !important;
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    color: #ffffff !important;
    border-radius: 20px !important;
    padding: 6px 16px !important;
    font-size: 0.85em !important;
    box-shadow: none !important;
}
#theme-toggle-btn:hover {
    background: rgba(255,255,255,0.28) !important;
}
#header-banner h1, #header-banner h3, #header-banner p {
    color: #ffffff !important;
}
#header-banner h1 { margin-bottom: 4px !important; }
#header-banner h3 {
    font-weight: 500 !important;
    opacity: 0.95;
    margin-bottom: 10px !important;
}
#header-banner p { opacity: 0.9; margin: 0 !important; }

.card-section {
    background: var(--background-fill-primary);
    color: var(--body-text-color);
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    border: 1px solid var(--border-color-primary);
}
.card-section h4, .card-section p, .card-section span {
    color: var(--body-text-color) !important;
}

.section-title { font-weight: 600 !important; margin-bottom: 4px !important; }

/* Compact the resume upload dropzone */
#compact-upload {
    min-height: 110px !important;
}
#compact-upload .wrap {
    min-height: 110px !important;
    padding: 10px !important;
}

#submit-btn {
    border-radius: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px;
    box-shadow: 0 4px 14px rgba(147, 51, 234, 0.35);
}

/* Right-side sticky output card */
#output-column {
    position: sticky;
    top: 18px;
    align-self: flex-start;
    max-height: calc(100vh - 36px);
}
#output-card {
    background: var(--background-fill-primary);
    color: var(--body-text-color);
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: 0 2px 14px rgba(0,0,0,0.08);
    border: 1px solid var(--border-color-primary);
    min-height: 320px;
    max-height: calc(100vh - 36px);
    overflow-y: auto;
}
#output-card h4 {
    margin-top: 0 !important;
    color: #a855f7;
}

#footer-note {
    text-align: center;
    margin-top: 18px;
    opacity: 0.65;
    font-size: 0.85em;
}
"""

with gr.Blocks(title="CareerBridge AI", theme=custom_theme, css=custom_css) as demo:

    with gr.Column(elem_id="header-banner"):
        theme_toggle_btn = gr.Button("🌙 / ☀️ Theme", elem_id="theme-toggle-btn", size="sm")
        gr.Markdown(
            """
            # 🌉 CareerBridge AI
            ### Your personal guide back to the workforce, powered by Google Gemini
            Returning to work after a break can feel overwhelming. Share a bit about yourself and get instant,
            personalized career guidance — your strengths, skill gaps, and best-fit roles.
            """
        )

    with gr.Row(equal_height=False):

        # ---------------- LEFT: inputs ----------------
        with gr.Column(scale=3):

            with gr.Column(elem_classes="card-section"):
                gr.Markdown("#### 👤 Tell us about your career so far", elem_classes="section-title")
                with gr.Row():
                    experience = gr.Textbox(label="💼 Experience (years)", placeholder="e.g. 5 years")
                    career_gap = gr.Textbox(label="⏳ Career Gap Duration", placeholder="e.g. 2 years")
                with gr.Row():
                    field = gr.Textbox(label="🏢 Field / Industry", placeholder="e.g. IT, Cloud, AI")
                    desired_role = gr.Textbox(label="🎯 Desired Role (optional)", placeholder="e.g. Cloud Administrator")

            with gr.Column(elem_classes="card-section"):
                gr.Markdown("#### 📄 Share your background", elem_classes="section-title")
                with gr.Tabs():
                    with gr.Tab("📎 Upload Resume"):
                        pdf_input = gr.File(
                            label="Resume Upload (PDF only)",
                            file_types=[".pdf"],
                            elem_id="compact-upload"
                        )
                    with gr.Tab("✍️ Type it in"):
                        skills_background = gr.Textbox(
                            label="Describe your skills and background",
                            placeholder="Certifications, key skills, previous responsibilities, achievements...",
                            lines=6
                        )

            submit_btn = gr.Button("✨ Get My Career Advice", variant="primary", size="lg", elem_id="submit-btn")

        # ---------------- RIGHT: output ----------------
        with gr.Column(scale=2, elem_id="output-column"):
            with gr.Column(elem_id="output-card"):
                gr.Markdown("#### 💡 Your Career Advice")
                output = gr.Markdown("Fill in your details on the left and click **Get My Career Advice** — your personalized guidance will appear here.")

    gr.Markdown("Built with ❤️ for career returners · Powered by Google Gemini", elem_id="footer-note")

    submit_btn.click(
        fn=gradio_career_advisor,
        inputs=[experience, career_gap, field, desired_role, skills_background, pdf_input],
        outputs=output
    )

    theme_toggle_btn.click(
        fn=None,
        inputs=None,
        outputs=None,
        js="""
        () => {
            document.documentElement.classList.toggle('dark');
        }
        """
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
