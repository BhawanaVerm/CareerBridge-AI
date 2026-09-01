import os
import gradio as gr
from google import genai
from pypdf import PdfReader

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def extract_text_from_pdf(pdf_file):
    if pdf_file is None:
        return ""
    reader = PdfReader(pdf_file.name)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() or ""
    return extracted_text

def analyze_career_profile(user_skills_text):
    prompt = f"""
    You are a career advisor helping women professionals returning to work after a career break.
    Here is the person's background and skills:
    {user_skills_text}

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

def gradio_career_advisor(experience, career_gap, field, desired_role, pdf_file):
    pdf_text = extract_text_from_pdf(pdf_file)
    
    if not pdf_text.strip():
        return "⚠️ Kripya apna Resume PDF upload karein."

    combined_input = f"""
    Years of Experience: {experience}
    Career Gap Duration: {career_gap}
    Field/Industry: {field}
    Desired Role: {desired_role if desired_role else 'Not specified'}
    
    --- RESUME DETAILS ---
    {pdf_text}
    """
    
    return analyze_career_profile(combined_input)

custom_theme = gr.themes.Soft(primary_hue="purple", secondary_hue="pink")

with gr.Blocks(title="CareerBridge AI", theme=custom_theme) as demo:
    gr.Markdown("# 🧳 CareerBridge AI\n### Your personal guide back to the workforce")
    
    with gr.Row():
        experience = gr.Textbox(label="💼 Experience (years)", placeholder="5 years")
        career_gap = gr.Textbox(label="⏳ Career Gap Duration", placeholder="2 years")
        
    with gr.Row():
        field = gr.Textbox(label="🏢 Field / Industry", placeholder="IT, Cloud, AI")
        desired_role = gr.Textbox(label="🎯 Desired Role", placeholder="Cloud Administrator")
        
    pdf_input = gr.File(label="📄 Resume Upload (PDF only)", file_types=[".pdf"])
    submit_btn = gr.Button("✨ Get My Career Advice", variant="primary")
    
    output = gr.Markdown(label="Career Advice")
    
    # Event trigger with built-in loading animation
    submit_btn.click(
        fn=gradio_career_advisor,
        inputs=[experience, career_gap, field, desired_role, pdf_input],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
