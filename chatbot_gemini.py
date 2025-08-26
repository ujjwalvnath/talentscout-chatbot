import streamlit as st
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("TalentScout Hiring Assistant 🤖")

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = "greeting"
    st.session_state.candidate = {}
    st.session_state.chat_history = []

def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-1.5-flash",  # You can use gemini-2.0-flash if enabled
        contents=prompt
    )
    return response.text

def append_and_display(role, text):
    st.session_state.chat_history.append((role, text))
    st.markdown(f"**{role.capitalize()}**: {text}")

# Show chat history
for role, text in st.session_state.chat_history:
    st.markdown(f"**{role.capitalize()}**: {text}")

# Chatbot flow
if st.session_state.state == "greeting":
    msg = "Hello! I'm TalentScout Assistant. I'll gather some basic details " \
          "and then ask technical questions based on your tech skills."
    if not any(r == "assistant" and "TalentScout" in t for r, t in st.session_state.chat_history):
        append_and_display("assistant", msg)
    st.session_state.state = "ask_name"

elif st.session_state.state == "ask_name":
    name = st.text_input("Enter your Name:", key="name_input")
    if st.button("Next", key="name_btn") and name:
        st.session_state.candidate["name"] = name
        append_and_display("user", name)
        st.session_state.state = "ask_email"
        st.experimental_rerun()

elif st.session_state.state == "ask_email":
    email = st.text_input("Enter your Email:", key="email_input")
    if st.button("Next", key="email_btn") and email:
        st.session_state.candidate["email"] = email
        append_and_display("user", email)
        st.session_state.state = "ask_tech"
        st.experimental_rerun()

elif st.session_state.state == "ask_tech":
    tech = st.text_input("Enter your Tech Stack (e.g., Python, React):", key="tech_input")
    if st.button("Next", key="tech_btn") and tech:
        st.session_state.candidate["tech_stack"] = tech
        append_and_display("user", tech)
        st.session_state.state = "ask_questions"
        st.experimental_rerun()

elif st.session_state.state == "ask_questions":
    tech = st.session_state.candidate["tech_stack"]
    prompt = f"Generate 3–5 beginner to intermediate interview questions for: {tech}"
    Qs = ask_gemini(prompt)
    append_and_display("assistant", Qs)
    st.session_state.state = "end"
    st.experimental_rerun()

elif st.session_state.state == "end":
    msg = "✅ Thank you! Your responses have been recorded. We'll be in touch soon."
    if not any(r == "assistant" and "✅ Thank you!" in t for r, t in st.session_state.chat_history):
        append_and_display("assistant", msg)
