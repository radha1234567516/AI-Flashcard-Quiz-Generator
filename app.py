
import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="AI Flashcard & Quiz Generator",
    page_icon="📚"
)

st.title("📚 AI Flashcard & Quiz Generator")
st.write("Create flashcards and quizzes from your study notes using AI.")

notes = st.text_area(
    "Paste your study notes here",
    height=220,
    placeholder="Paste your study notes here..."
)

if st.button("✨ Generate with AI"):
    if not notes.strip():
        st.warning("Please paste your study notes first.")

    elif not os.getenv("GEMINI_API_KEY"):
        st.error("API key not found. Check your .env file.")

    else:
        try:
            with st.spinner("AI is preparing your study material..."):
                client = genai.Client(
                    api_key=os.getenv("GEMINI_API_KEY")
                )

                prompt = f"""
Create 5 flashcards and 5 multiple-choice quiz questions
from the following study notes.

Return ONLY valid JSON in this format:
{{
  "flashcards": [
    {{"question": "Question", "answer": "Answer"}}
  ],
  "quiz": [
    {{
      "question": "Question",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Correct option text",
      "explanation": "Short explanation"
    }}
  ]
}}

Study notes:
{notes[:12000]}
"""

                response = client.models.generate_content(
                   model="gemini-omni-1.1-flash",
                    contents=prompt
                )

                result_text = response.text.strip()
                result_text = result_text.replace(
                    "```json", ""
                ).replace("```", "").strip()

                data = json.loads(result_text)

            st.session_state["ai_material"] = data
            st.success("Study material generated successfully!")

        except Exception as e:
            st.error("AI generation failed.")
            st.write("Error details:", str(e))

if "ai_material" in st.session_state:
    data = st.session_state["ai_material"]

    st.header("📚 Flashcards")

    for i, card in enumerate(
        data.get("flashcards", []), start=1
    ):
        with st.expander(
            f"Flashcard {i}: {card.get('question', '')}"
        ):
            st.write(card.get("answer", ""))

    st.header("📝 Practice Quiz")

    quiz = data.get("quiz", [])

    if quiz:
        with st.form("quiz_form"):
            answers = {}

            for i, question in enumerate(quiz):
                answers[i] = st.radio(
                    f"{i + 1}. {question.get('question', '')}",
                    question.get("options", []),
                    key=f"quiz_{i}"
                )

            submitted = st.form_submit_button("Check Answers")

        if submitted:
            score = 0

            for i, question in enumerate(quiz):
                correct = question.get("answer", "")

                if answers[i] == correct:
                    score += 1
                    st.success(f"Question {i + 1}: Correct!")
                else:
                    st.error(
                        f"Question {i + 1}: Correct answer: {correct}"
                    )

                st.info(question.get("explanation", ""))

            st.subheader(f"Your Score: {score}/{len(quiz)}")
