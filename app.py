
import streamlit as st
import random
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(
    page_title="AI Flashcard & Quiz Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Flashcard & Quiz Generator")
st.write("Learn smarter with flashcards and practice quizzes!")

st.sidebar.title("📖 Navigation")
page = st.sidebar.radio(
    "Choose a feature",
    ["Home", "Flashcards", "Practice Quiz"]
)

if page == "Home":
    st.header("Welcome to your Study Assistant! 🎓")
    st.write(
        "This application helps students revise topics "
        "using flashcards and multiple-choice quizzes."
    )
    st.info("Choose Flashcards or Practice Quiz from the sidebar.")

elif page == "Flashcards":
    st.header("🗂️ Flashcard Generator")
    st.write("Enter your study notes to create flashcards.")

    notes = st.text_area(
        "Enter notes (one question and answer per line):",
        placeholder="What is Python? | Python is a programming language.\nWhat is AI? | AI means Artificial Intelligence."
    )

    if st.button("Create Flashcards"):
        cards = []

        for line in notes.splitlines():
            if "|" in line:
                question, answer = line.split("|", 1)
                if question.strip() and answer.strip():
                    cards.append((question.strip(), answer.strip()))

        if cards:
            st.session_state.cards = cards
            st.session_state.card_index = 0
        else:
            st.warning("Enter notes using Question | Answer format.")

    if st.session_state.get("cards"):
        cards = st.session_state.cards
        index = st.session_state.card_index

        st.subheader(f"Flashcard {index + 1} of {len(cards)}")
        st.markdown(f"**Question:** {cards[index][0]}")

        if st.button("Show Answer"):
            st.session_state.show_answer = True

        if st.session_state.get("show_answer", False):
            st.success(cards[index][1])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Previous") and index > 0:
                st.session_state.card_index -= 1
                st.session_state.show_answer = False
                st.rerun()

        with col2:
            if st.button("Next ➡") and index < len(cards) - 1:
                st.session_state.card_index += 1
                st.session_state.show_answer = False
                st.rerun()

elif page == "Practice Quiz":
    st.header("📝 Practice Quiz")
    st.write("Create a simple multiple-choice quiz.")

    with st.form("quiz_form"):
        question = st.text_input("Enter your question")
        option_a = st.text_input("Option A")
        option_b = st.text_input("Option B")
        option_c = st.text_input("Option C")
        option_d = st.text_input("Option D")
        correct = st.selectbox(
            "Choose the correct option",
            ["A", "B", "C", "D"]
        )
        submitted = st.form_submit_button("Create Quiz")

    if submitted:
        if all([question.strip(), option_a.strip(),
                option_b.strip(), option_c.strip(), option_d.strip()]):
            st.session_state.quiz = {
                "question": question,
                "options": {
                    "A": option_a,
                    "B": option_b,
                    "C": option_c,
                    "D": option_d
                },
                "correct": correct
            }
            st.session_state.pop("quiz_answer", None)
        else:
            st.warning("Please fill in all fields.")

    quiz = st.session_state.get("quiz")

    if quiz:
        st.subheader(quiz["question"])
        answer = st.radio(
            "Select your answer",
            list(quiz["options"].keys()),
            format_func=lambda key: f"{key}. {quiz['options'][key]}",
            key="quiz_choice"
        )

        if st.button("Submit Answer"):
            st.session_state.quiz_answer = answer

        if "quiz_answer" in st.session_state:
            if st.session_state.quiz_answer == quiz["correct"]:
                st.success("Correct answer! 🎉")
            else:
                st.error(
                    f"Not quite. Correct answer: "
                    f"{quiz['correct']}. "
                    f"{quiz['options'][quiz['correct']]}"
                )

st.divider()
st.caption("Mini Project | AI Flashcard & Quiz Generator")
