import os

import streamlit as st

from quiz_engine import generate_quiz

st.set_page_config(page_title="AI Quiz Bot", page_icon="🎓", layout="centered")


def get_api_key() -> str:
    """Read the key from a local environment variable or Streamlit secrets."""
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    try:
        return str(st.secrets.get("GROQ_API_KEY", "")).strip()
    except FileNotFoundError:
        return ""


def reset_quiz() -> None:
    for key in list(st.session_state):
        if key.startswith("answer_"):
            del st.session_state[key]
    st.session_state.pop("quiz", None)
    st.session_state.pop("submitted", None)


def render_quiz(quiz: list[dict]) -> None:
    st.subheader("Your quiz")
    st.caption("Choose an answer for every question, then submit to see your score.")

    for index, item in enumerate(quiz, start=1):
        st.markdown(f"**Question {index}. {item['question']}**")
        st.radio(
            "Select an answer",
            options=list(item["options"]),
            format_func=lambda label, options=item["options"]: f"{label}. {options[label]}",
            index=None,
            key=f"answer_{index}",
            label_visibility="collapsed",
        )

    if not st.session_state.get("submitted"):
        if st.button("Submit answers", type="primary", use_container_width=True):
            unanswered = [
                number
                for number in range(1, len(quiz) + 1)
                if not st.session_state.get(f"answer_{number}")
            ]
            if unanswered:
                st.warning(f"Please answer question{'s' if len(unanswered) > 1 else ''} " + ", ".join(map(str, unanswered)) + ".")
            else:
                st.session_state.submitted = True
                st.rerun()
        return

    score = sum(
        st.session_state.get(f"answer_{index}") == item["answer"]
        for index, item in enumerate(quiz, start=1)
    )
    st.success(f"You scored {score} out of {len(quiz)}.")

    for index, item in enumerate(quiz, start=1):
        selected = st.session_state.get(f"answer_{index}")
        correct = item["answer"]
        if selected == correct:
            st.success(f"Question {index}: Correct — {correct}. {item['options'][correct]}")
        else:
            st.error(
                f"Question {index}: Your answer was {selected}. "
                f"Correct answer: {correct}. {item['options'][correct]}"
            )

    if st.button("Create a new quiz", use_container_width=True):
        reset_quiz()
        st.rerun()


st.title("🎓 Smart Educational Quiz Generator")
st.write("Upload lecture notes and turn them into a self-marking multiple-choice quiz.")

api_key = get_api_key()
if not api_key:
    st.error("GROQ_API_KEY is missing. Add it to your environment or Streamlit secrets before generating a quiz.")
    st.stop()

uploaded_file = st.file_uploader("Choose a text file (.txt)", type=["txt"])

if uploaded_file:
    try:
        content = uploaded_file.getvalue().decode("utf-8")
    except UnicodeDecodeError:
        st.error("This file is not UTF-8 text. Please upload a UTF-8 encoded .txt file.")
        st.stop()

    if not content.strip():
        st.warning("This file is empty. Upload a text file with lecture content to create a quiz.")
        st.stop()

    st.success(f"{uploaded_file.name} uploaded successfully.")
    question_count = st.slider("How many questions?", min_value=1, max_value=10, value=5)

    if st.button("Generate quiz", type="primary", use_container_width=True):
        reset_quiz()
        with st.spinner("Creating questions from different parts of your notes..."):
            try:
                st.session_state.quiz = generate_quiz(content, question_count, api_key)
                st.session_state.submitted = False
            except Exception:
                st.error("Quiz generation failed. Check your Groq API key and connection, then try again.")

if st.session_state.get("quiz"):
    render_quiz(st.session_state.quiz)
