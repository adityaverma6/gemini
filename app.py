import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from pdf_reader import extract_text_from_pdf

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

st.title("📚 AI Study Assistant")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)

    question = st.text_input("Ask a question from the document")

    if question:
        prompt = f"""
        Answer the question using the following study material.

        Material:
        {text}

        Question:
        {question}
        """

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        st.write("### Answer")
        st.write(response.text)