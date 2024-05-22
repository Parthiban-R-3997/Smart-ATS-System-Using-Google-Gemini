## Importing Libraries
import streamlit as st
import os
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv

# Loading the .env keys
load_dotenv()

# Define functions
def get_gemini_response(model_id, prompt, pdf_content, input_text):
    model = genai.GenerativeModel(model_id)
    response = model.generate_content([prompt, pdf_content, input_text])
    return response.text

def get_pdf_text(pdf_docs):
    text = ""
    for doc in pdf_docs:
        if doc.name.endswith(".pdf"):
            pdf_reader = PdfReader(doc)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif doc.name.endswith(".docx"):
            try:
                import docx
                doc_reader = docx.Document(doc)
                for para in doc_reader.paragraphs:
                    text += para.text + "\n"
            except ImportError:
                st.error("Please make sure you have installed the `python-docx` package.")
    return text

# Define input prompts
input_prompts = {
    "evaluate_resume": """
        You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
        Please share your professional evaluation on whether the candidate's profile aligns with the role. 
        Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
    """,
    "improve_skills": """
        You are an Technical Human Resource Manager with expertise in data science, 
        your role is to scrutinize the resume in light of the job description provided. 
        Share your insights on the candidate's suitability for the role from an HR perspective. 
        Additionally, offer advice on enhancing the candidate's skills and identify areas where improvement is needed.
    """,
    "missing_keywords": """
        You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
        your task is to evaluate the resume against the provided job description. As a Human Resource manager,
        assess the compatibility of the resume with the role. Give me what are the keywords that are missing
        Also, provide recommendations for enhancing the candidate's skills and identify which areas require further development.
    """,
    "percentage_match": """
        You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
        your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
        the job description. First the output should come as percentage and then keywords missing and last final thoughts.
    """,
    "answer_query": """
        You are an experienced Technical Human Resource Manager. Please answer the following query based on the resume and job description provided.
    """
}

# Define model options
model_options = [
    "models/gemini-1.0-pro",
    "models/gemini-1.0-pro-001",
    "models/gemini-1.0-pro-latest",
    "models/gemini-1.0-pro-vision-latest",
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-pro-latest",
    "models/gemini-pro",
    "models/gemini-pro-vision"
]

# Streamlit App
st.set_page_config(page_title="Resume Expert System", page_icon=":chart_with_upwards_trend:")
st.title("Smart ATS System 💼🔍")

# Sidebar for API key, model selection, and resume uploader
with st.sidebar:
    st.markdown("[Get your Google API Key](https://aistudio.google.com/app/apikey)")
    api_key = st.text_input("Enter your Google API Key", type="password")
    selected_model = st.selectbox("Select Gemini Model", model_options)
    uploaded_files = st.file_uploader("Upload Your Resume in .PDF or .DOCX format 📂", type=["pdf", "docx"], accept_multiple_files=True)
    if uploaded_files:
        st.success("Files Uploaded Successfully.")

# Set the API key for genai
if api_key:
    genai.configure(api_key=api_key)

input_text = st.text_area("Paste the Job Description 📄")

# Align buttons in one row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    evaluate_resume_btn = st.button("Evaluate Resume")
with col2:
    improve_skills_btn = st.button("Improve Skills")
with col3:
    missing_keywords_btn = st.button("Identify Missing Keywords")
with col4:
    percentage_match_btn = st.button("Calculate Match Percentage")
with col5:
    answer_query_btn = st.button("Answer My Query")

show_error_api_key = False
show_error_uploaded_files = False
show_error_input_text = False

if evaluate_resume_btn or improve_skills_btn or missing_keywords_btn or percentage_match_btn or answer_query_btn:
    if not api_key:
        show_error_api_key = True
    if not uploaded_files:
        show_error_uploaded_files = True
    if not input_text:
        show_error_input_text = True

    if not show_error_api_key and not show_error_uploaded_files and not show_error_input_text:
        pdf_content = get_pdf_text(uploaded_files)

        if evaluate_resume_btn:
            response = get_gemini_response(selected_model, input_prompts["evaluate_resume"], pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
        elif improve_skills_btn:
            response = get_gemini_response(selected_model, input_prompts["improve_skills"], pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
        elif missing_keywords_btn:
            response = get_gemini_response(selected_model, input_prompts["missing_keywords"], pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
        elif percentage_match_btn:
            response = get_gemini_response(selected_model, input_prompts["percentage_match"], pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
        elif answer_query_btn:
            response = get_gemini_response(selected_model, input_prompts["answer_query"], pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)

# Display error messages near respective fields
if show_error_api_key:
    with st.sidebar:
        st.error("Please enter your Google API Key.")
if show_error_input_text:
    st.error("Please paste the job description to proceed.", icon="📄")
