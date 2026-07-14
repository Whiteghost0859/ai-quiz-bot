import streamlit as st
import os
import json
import time
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="AI Quiz Bot", page_icon="🎓")
st.title("🎓 Smart Educational Quiz Generator")
st.write("Upload your lecture text file below to build a quiz.")

# Key Check
api_key = os.environ.get("GROQ_API_KEY", "").strip()
if not api_key:
    st.error("⚠️ GROQ_API_KEY environment variable is missing! Please set it in your terminal before running.")
    st.stop()

# 3. Groq Logic
def generate_quiz_question_json(text):
    client = Groq(api_key=api_key)
    system_prompt = "You are a quiz bot. Respond strictly with a single JSON object."
    user_prompt = f"Generate a multiple-choice question from this text with 'question', 'options' (A,B,C,D), and 'answer' keys. Text:\n{text}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return json.loads(response.choices[0].message.content)

# 4. Simple UI Components
uploaded_file = st.file_uploader("Choose a text file (.txt)", type=["txt"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    st.success("File uploaded successfully!")
    
    if st.button("Generate Question Test"):
        with st.spinner("Generating..."):
            try:
                result = generate_quiz_question_json(content[:500]) # test with first 500 chars
                st.write("### Generated Data:")
                st.json(result)
            except Exception as e:
                # The Groq SDK's top-level message is often just "Connection error".
                # Show its underlying cause so network, TLS, proxy, and API errors can
                # be distinguished while debugging.
                st.error(f"Groq request failed ({type(e).__name__}): {e}")
                if e.__cause__:
                    st.code(
                        f"Underlying cause: {type(e.__cause__).__name__}: {e.__cause__}"
                    )
                st.exception(e)
