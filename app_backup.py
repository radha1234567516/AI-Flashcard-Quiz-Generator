

import streamlit as st
import random
import re

from pypdf import PdfReader

st.set_page_config(
    page_title="AI Flashcard & Quiz Generator",
    page_icon="📚"
)

st.title("📚 AI Flashcard & Quiz Generator")
st.write("Create flashcards and MCQ quizzes from your study notes.")

uploaded_file = st.file_uploader(
    "Upload your notes (PDF or TXT)",
    type=["pdf", "txt"]
)

st.subheader("Or paste your notes")
pasted_notes = st.text_area(
    "Enter your study notes here",
    height=180
)

if "notes" not in st.session_state:
    st.session_state.notes = ""

if st.button("Prepare My Notes"):
    notes = pasted_notes.strip()

    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".pdf"):
            reader = PdfReader(uploaded_file)
            notes = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )
        else:
            notes = uploaded_file.getvalue().decode(
                "utf-8", errors="ignore"
            )

    if notes.strip():
        st.session_state.notes = notes
        st.success("Your notes are ready!")
    else:
        st.warning("Please upload a file or paste your notes.")

notes = st.session_state.notes

if notes:
    st.subheader("Notes Preview")
    st.write(notes[:3000])

    sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+|\n+", notes)
        if len(s.strip().split()) >= 5
    ]

    st.divider()
    st.header("🗂️ Flashcards")

    if sentences:
        for i, sentence in enumerate(sentences[:10]):
            with st.expander(f"Flashcard {i + 1}"):
                st.write("**Study point:**")
                st.write(sentence)
                st.write("**Remember:** Explain this point in your own words.")
    else:
        st.info("Add a little more text to create flashcards.")

    st.divider()
    st.header("📝 Practice Quiz")

    if len(sentences) >= 2:
        quiz_sentences = sentences[:5]

        for i, sentence in enumerate(quiz_sentences):
            words = sentence.split()
            answer = " ".join(words[:min(4, len(words))])
            question = sentence

            st.write(f"**Q{i + 1}. Which statement appears in your notes?**")

            options = [sentence]

            for other in sentences:
                if other != sentence and other not in options:
                    options.append(other)
                if len(options) == 4:
                    break

            random.Random(i).shuffle(options)

            selected = st.radio(
                f"Choose your answer for question {i + 1}",
                options,
                key=f"quiz_{i}",
                index=None
            )

            if st.button("Check Answer", key=f"check_{i}"):
                if selected == sentence:
                    st.success("Correct! 🎉")
                else:
                    st.error("Not quite. Review your notes and try again.")
    else:
        st.info("Add at least two sentences to create a practice quiz.")


