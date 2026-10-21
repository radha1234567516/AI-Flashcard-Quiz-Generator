
import streamlit as st
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pypdf import PdfReader

load_dotenv()

st.set_page_config(
    page_title="AI Flashcard & Quiz Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Flashcard & Quiz Generator")
st.write("Upload your notes and let AI help you study!")

# Get API key securely
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = ""

API_KEY = API_KEY or os.getenv("GEMINI_API_KEY", "")

# Session state
if "study_text" not in st.session_state:
    st.session_state.study_text = ""
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "card_index" not in st.session_state:
    st.session_state.card_index = 0
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = None


def generate_ai(prompt):
    if not API_KEY:
        st.error(
            "Gemini API key is missing. "
            "Add GEMINI_API_KEY in Streamlit Secrets."
        )
        return None

    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
           model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        return json.loads(response.text)

    except Exception as e:
        st.error(
            "AI generation failed. Check your API key, "
            "model availability, quota, and internet connection."
        )
        st.caption(str(e))
        return None


st.sidebar.title("📖 Navigation")
page = st.sidebar.radio(
    "Choose a feature",
    ["Home", "PDF & AI Generator", "Flashcards", "Practice Quiz"]
)

if page == "Home":
    st.header("Welcome to your Study Assistant! 🎓")
    st.write(
        "Upload your study PDF, generate flashcards, "
        "and practise AI-generated multiple-choice questions."
    )
    st.info("Start with PDF & AI Generator in the sidebar.")

elif page == "PDF & AI Generator":
    st.header("📄 Upload Notes")
    pdf_file = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"]
    )

    pasted_notes = st.text_area(
        "Or paste your study notes here",
        height=180
    )

    if st.button("Prepare My Notes", type="primary"):
        text = ""

        try:
            if pdf_file is not None:
                reader = PdfReader(pdf_file)
                text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )
            else:
                text = pasted_notes

            if text.strip():
                st.session_state.study_text = text[:30000]
                st.session_state.flashcards = []
                st.session_state.quiz = []
                st.session_state.quiz_answers = None
                st.success("Notes prepared successfully!")
            else:
                st.warning(
                    "No readable text found. "
                    "Try another PDF or paste your notes."
                )

        except Exception as e:
            st.error("Could not read this PDF.")
            st.caption(str(e))

    if st.session_state.study_text:
        st.subheader("Notes Preview")
        st.text_area(
            "Extracted text",
            st.session_state.study_text[:2500],
            height=160,
            disabled=True
        )

        st.divider()
        st.subheader("🤖 Generate with Gemini AI")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✨ Generate Flashcards"):
                with st.spinner("AI is creating flashcards..."):
                    result = generate_ai(
                        "Use the following study notes to create 8 "
                        "useful question-answer flashcards. "
                        "Return JSON as an object with a 'flashcards' "
                        "array. Each item must have 'question' and "
                        "'answer' strings. Use only the notes.\n\n"
                        "NOTES:\n" + st.session_state.study_text
                    )

                if result and isinstance(
                    result.get("flashcards"), list
                ):
                    st.session_state.flashcards = [
                        c for c in result["flashcards"]
                        if isinstance(c, dict)
                        and c.get("question")
                        and c.get("answer")
                    ]
                    st.session_state.card_index = 0
                    if st.session_state.flashcards:
                        st.success("Flashcards generated!")
                    else:
                        st.warning("AI did not return valid flashcards.")

        with col2:
            if st.button("📝 Generate MCQ Quiz"):
                with st.spinner("AI is creating your quiz..."):
                    result = generate_ai(
                        "Create 5 multiple-choice questions from these "
                        "study notes. Return JSON as an object with a "
                        "'questions' array. Each item must contain: "
                        "'question' (string), 'options' (object with "
                        "keys A, B, C, D and string values), "
                        "'correct_answer' (one letter A/B/C/D), "
                        "and 'explanation' (string). Make exactly one "
                        "correct option per question. Use only the notes.\n\n"
                        "NOTES:\n" + st.session_state.study_text
                    )

                if result and isinstance(
                    result.get("questions"), list
                ):
                    valid_questions = []

                    for q in result["questions"]:
                        if not isinstance(q, dict):
                            continue
                        options = q.get("options", {})
                        correct = q.get("correct_answer", "")

                        if (
                            q.get("question")
                            and all(k in options for k in "ABCD")
                            and correct in "ABCD"
                            and len(correct) == 1
                        ):
                            valid_questions.append(q)

                    st.session_state.quiz = valid_questions
                    st.session_state.quiz_answers = None

                    if valid_questions:
                        st.success("MCQ quiz generated!")
                    else:
                        st.warning("AI did not return a valid quiz.")

elif page == "Flashcards":
    st.header("🗂️ Flashcards")

    cards = st.session_state.flashcards

    if not cards:
        st.info(
            "First upload your PDF and generate flashcards "
            "in PDF & AI Generator."
        )
    else:
        index = st.session_state.card_index
        card = cards[index]

        st.subheader(f"Flashcard {index + 1} of {len(cards)}")
        st.markdown(f"**Question:** {card['question']}")

        if st.button("Show Answer"):
            st.session_state.show_answer = True

        if st.session_state.get("show_answer", False):
            st.success(card["answer"])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Previous", disabled=index == 0):
                st.session_state.card_index -= 1
                st.session_state.show_answer = False
                st.rerun()

        with col2:
            if st.button(
                "Next ➡",
                disabled=index >= len(cards) - 1
            ):
                st.session_state.card_index += 1
                st.session_state.show_answer = False
                st.rerun()

elif page == "Practice Quiz":
    st.header("📝 AI Practice Quiz")

    questions = st.session_state.quiz

    if not questions:
        st.info(
            "First prepare your notes and generate an MCQ quiz "
            "in PDF & AI Generator."
        )
    else:
        with st.form("ai_quiz_form"):
            answers = {}

            for i, q in enumerate(questions):
                st.markdown(f"**Q{i + 1}. {q['question']}**")

                answers[i] = st.radio(
                    "Choose your answer",
                    ["A", "B", "C", "D"],
                    format_func=lambda key, opts=q["options"]:
                        f"{key}. {opts[key]}",
                    key=f"ai_answer_{i}"
                )
                st.divider()

            submitted = st.form_submit_button("Submit Quiz")

        if submitted:
            st.session_state.quiz_answers = answers

        if st.session_state.quiz_answers is not None:
            answers = st.session_state.quiz_answers
            score = 0

            for i, q in enumerate(questions):
                correct = q["correct_answer"]

                if answers[i] == correct:
                    score += 1
                    st.success(f"Q{i + 1}: Correct!")
                else:
                    st.error(
                        f"Q{i + 1}: Incorrect. Correct answer: "
                        f"{correct}. {q['options'][correct]}"
                    )

                st.write(
                    "Explanation: "
                    + q.get("explanation", "No explanation provided.")
                )

            st.subheader(f"Your Score: {score} / {len(questions)}")

            if st.button("Try Quiz Again"):
                st.session_state.quiz_answers = None
                st.rerun()

st.divider()
st.caption("Mini Project | AI Flashcard & Quiz Generator")
