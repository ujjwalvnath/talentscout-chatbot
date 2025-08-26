import streamlit as st
from google import genai

# Load Gemini API key from Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("TalentScout Hiring Assistant 🤖")

if "state" not in st.session_state:
    st.session_state.state = "greeting"
    st.session_state.candidate = {}
    st.session_state.chat_history = []

def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def append_and_display(role, text):
    st.session_state.chat_history.append((role, text))
    st.markdown(f"**{role.capitalize()}**: {text}")

# Chatbot flow
if st.session_state.state == "greeting":
    msg = "Hello! I'm TalentScout Assistant. I'll gather some basic details " \
          "and then ask technical questions based on your tech skills."
    append_and_display("assistant", msg)
    st.session_state.state = "ask_name"

elif st.session_state.state == "ask_name":
    name = st.text_input("Your Name:")
    if st.button("Next", key="name"):
        st.session_state.candidate["name"] = name
        append_and_display("user", name)
        st.session_state.state = "ask_email"

elif st.session_state.state == "ask_email":
    email = st.text_input("Your Email:")
    if st.button("Next", key="email"):
        st.session_state.candidate["email"] = email
        append_and_display("user", email)
        st.session_state.state = "ask_tech"

elif st.session_state.state == "ask_tech":
    tech = st.text_input("Tech Stack (e.g., Python, React):")
    if st.button("Next", key="tech"):
        st.session_state.candidate["tech_stack"] = tech
        append_and_display("user", tech)
        st.session_state.state = "ask_questions"

elif st.session_state.state == "ask_questions":
    tech = st.session_state.candidate["tech_stack"]
    prompt = f"Generate 3–5 beginner to intermediate interview questions for: {tech}"
    Qs = ask_gemini(prompt)
    append_and_display("assistant", Qs)
    st.session_state.state = "end"

elif st.session_state.state == "end":
    msg = "✅ Thank you! Your responses have been recorded. We'll be in touch soon."
    append_and_display("assistant", msg)
    st.stop()
