import streamlit as st
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="TalentScout Chatbot", page_icon="🤖")
st.title("TalentScout Hiring Assistant 🤖")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "step" not in st.session_state:
    st.session_state.step = "greeting"
if "candidate" not in st.session_state:
    st.session_state.candidate = {}
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

# Helper: add a message to history
def add_message(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})

# Helper: show chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Helper: generate questions from Gemini
def generate_questions(tech_stack):
    prompt = f"Generate 3–5 concise technical interview QUESTIONS only (no answers, no explanations) for: {tech_stack}."
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return [q.strip("- ").strip() for q in response.text.split("\n") if q.strip()]

# Start conversation
if st.session_state.step == "greeting" and not st.session_state.chat_history:
    add_message("assistant", "Hello! I'm TalentScout Assistant. "
               "I'll gather some details from you step by step. "
               "Type 'exit' anytime to quit. Let's begin — what is your **Full Name**?")
    st.session_state.step = "ask_name"
    st.rerun()

# User input field
if user_input := st.chat_input("Type your response..."):
    # Exit condition
    if user_input.lower() in ["exit", "quit", "bye"]:
        add_message("user", user_input)
        add_message("assistant", "✅ Thank you for your time! Your responses have been recorded. Goodbye.")
        st.session_state.step = "end"
        st.rerun()

    add_message("user", user_input)

    # Conversation flow
    if st.session_state.step == "ask_name":
        st.session_state.candidate["name"] = user_input
        add_message("assistant", "Got it! Please provide your **Email Address**.")
        st.session_state.step = "ask_email"

    elif st.session_state.step == "ask_email":
        if "@" not in user_input:  # simple fallback
            add_message("assistant", "That doesn’t look like a valid email. Could you re-enter your **Email Address**?")
        else:
            st.session_state.candidate["email"] = user_input
            add_message("assistant", "Thanks! Now share your **Phone Number**.")
            st.session_state.step = "ask_phone"

    elif st.session_state.step == "ask_phone":
        if not user_input.isdigit():
            add_message("assistant", "Hmm, phone numbers should be digits only. Please re-enter your **Phone Number**.")
        else:
            st.session_state.candidate["phone"] = user_input
            add_message("assistant", "Noted. How many **Years of Experience** do you have?")
            st.session_state.step = "ask_exp"

    elif st.session_state.step == "ask_exp":
        if not user_input.isdigit():
            add_message("assistant", "Please enter a number for your **Years of Experience**.")
        else:
            st.session_state.candidate["experience"] = user_input
            add_message("assistant", "Great! What **Position(s)** are you applying for?")
            st.session_state.step = "ask_position"

    elif st.session_state.step == "ask_position":
        st.session_state.candidate["position"] = user_input
        add_message("assistant", "Got it. Where is your **Current Location**?")
        st.session_state.step = "ask_location"

    elif st.session_state.step == "ask_location":
        st.session_state.candidate["location"] = user_input
        add_message("assistant", "Perfect. Finally, tell me your **Tech Stack** (comma-separated, e.g., Python, Django, React).")
        st.session_state.step = "ask_tech"

    elif st.session_state.step == "ask_tech":
        st.session_state.candidate["tech_stack"] = user_input
        add_message("assistant", "Thanks! Generating some technical questions for you...")
        st.session_state.questions = generate_questions(user_input)
        st.session_state.step = "ask_question"
        st.rerun()

    elif st.session_state.step == "ask_question":
        q_idx = st.session_state.current_q
        if q_idx < len(st.session_state.questions):
            question = st.session_state.questions[q_idx]
            add_message("assistant", f"Q{q_idx+1}: {question}")
            st.session_state.current_q += 1
        else:
            add_message("assistant", "✅ That’s all the questions I had. Thank you for your responses! "
                        "Our team will review and reach out to you soon.")
            st.session_state.step = "end"

    st.rerun()
