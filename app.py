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
        model="gemini-2.5-flash",
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


custom_theme = gr.themes.Soft(primary_hue="purple", secondary_hue="pink")

with gr.Blocks(title="CareerBridge AI", theme=custom_theme) as demo:
    gr.Markdown(
        """
        # 🌉 CareerBridge AI
        ### Your personal guide back to the workforce, powered by Google Gemini
        Returning to work after a break can feel overwhelming. Upload your resume, or tell us about
        yourself, and get instant, personalized career guidance — your strengths, skill gaps, and best-fit roles.
        """
    )

    with gr.Row():
        experience = gr.Textbox(label="💼 Experience (years)", placeholder="e.g. 5 years")
        career_gap = gr.Textbox(label="⏳ Career Gap Duration", placeholder="e.g. 2 years")

    with gr.Row():
        field = gr.Textbox(label="🏢 Field / Industry", placeholder="e.g. IT, Cloud, AI")
        desired_role = gr.Textbox(label="🎯 Desired Role (optional)", placeholder="e.g. Cloud Administrator")

    gr.Markdown("### 📄 Upload your resume (PDF) — or write it in below")

    pdf_input = gr.File(label="Resume Upload (PDF only)", file_types=[".pdf"])

    skills_background = gr.Textbox(
        label="📝 Or describe your skills and background in detail here",
        placeholder="Certifications, key skills, previous responsibilities, achievements...",
        lines=5
    )

    submit_btn = gr.Button("✨ Get My Career Advice", variant="primary", size="lg")

    output = gr.Markdown(label="Career Advice")

    submit_btn.click(
        fn=gradio_career_advisor,
        inputs=[experience, career_gap, field, desired_role, skills_background, pdf_input],
        outputs=output
    )

demo.queue()

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
