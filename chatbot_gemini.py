import streamlit as st
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="TalentScout Chatbot", page_icon="🤖")
st.title("TalentScout Hiring Assistant 🤖")

# -------------------- STATE --------------------
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
if "last_question" not in st.session_state:
    st.session_state.last_question = None

# -------------------- HELPERS --------------------
def add_message(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})

def show_history():
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def validate_with_gemini(question, answer):
    context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history])
    prompt = f"""
    You are TalentScout Assistant, conducting a structured candidate screening.

    Conversation so far:
    {context}

    Current question: "{question}"
    Candidate's answer: "{answer}"

    Task:
    1. If the answer is valid and relevant → respond ONLY with "VALID".
    2. If the answer is not valid → respond with a short, polite correction,
       telling the candidate what to re-enter and why.
    """
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return response.text.strip()

def generate_questions(tech_stack):
    prompt = f"""
    Generate 3–5 concise technical interview QUESTIONS only (no answers, no explanations)
    for the following technologies: {tech_stack}.
    """
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return [q.strip("- ").strip() for q in response.text.split("\n") if q.strip()]

# -------------------- SHOW HISTORY --------------------
show_history()

# -------------------- INITIAL GREETING --------------------
if st.session_state.step == "greeting" and not st.session_state.chat_history:
    add_message("assistant", "Hello! I'm TalentScout Assistant. "
               "I'll gather some details from you step by step. "
               "Type 'exit' anytime to quit. Let's begin — what is your **Full Name**?")
    st.session_state.step = "ask_name"
    st.rerun()

# -------------------- CHAT INPUT --------------------
if user_input := st.chat_input("Type your response..."):
    # Exit condition
    if user_input.lower() in ["exit", "quit", "bye"]:
        add_message("user", user_input)
        add_message("assistant", "✅ Thank you for your time! Your responses have been recorded. Goodbye.")
        st.session_state.step = "end"
        st.rerun()

    add_message("user", user_input)

    # -------------------- INFO GATHERING --------------------
    if st.session_state.step == "ask_name":
        validation = validate_with_gemini("Full Name", user_input)
        if validation == "VALID":
            st.session_state.candidate["name"] = user_input
            add_message("assistant", "Got it! Please provide your **Email Address**.")
            st.session_state.step = "ask_email"
        else:
            add_message("assistant", validation)

    elif st.session_state.step == "ask_email":
        validation = validate_with_gemini("Email Address", user_input)
        if validation == "VALID":
            st.session_state.candidate["email"] = user_input
            add_message("assistant", "Thanks! Now share your **Phone Number**.")
            st.session_state.step = "ask_phone"
        else:
            add_message("assistant", validation)

    elif st.session_state.step == "ask_phone":
        validation = validate_with_gemini("Phone Number", user_input)
        if validation == "VALID":
            st.session_state.candidate["phone"] = user_input
            add_message("assistant", "Noted. How many **Years of Experience** do you have?")
            st.session_state.step = "ask_exp"
        else:
            add_message("assistant", validation)

    elif st.session_state.step == "ask_exp":
        validation = validate_with_gemini("Years of Experience", user_input)
        if validation == "VALID":
            st.session_state.candidate["experience"] = user_input
            add_message("assistant", "Great! What **Position(s)** are you applying for?")
            st.session_state.step = "ask_position"
        else:
            add_message("assistant", validation)

    elif st.session_state.step == "ask_position":
        validation = validate_with_gemini("Desired Position(s)", user_input)
        if validation == "VALID":
            st.session_state.candidate["position"] = user_input
            add_message("assistant", "Got it. Where is your **Current Location**?")
            st.session_state.step = "ask_location"
        else:
            add_message("assistant", validation)

    elif st.session_state.step == "ask_location":
        validation = validate_with_gemini("Current Location", user_input)
        if validation == "VALID":
            st.session_state.candidate["location"] = user_input
            add_message("assistant", "Perfect. Finally, tell me your **Tech Stack** (comma-separated, e.g., Python, Django, React).")
            st.session_state.step = "ask_tech"
        else:
            add_message("assistant", validation)

    elif st.session_state.step == "ask_tech":
        validation = validate_with_gemini("Tech Stack", user_input)
        if validation == "VALID":
            st.session_state.candidate["tech_stack"] = user_input
            add_message("assistant", "Thanks! Generating some technical questions for you...")
            st.session_state.questions = generate_questions(user_input)
            st.session_state.step = "ask_question"
            st.session_state.current_q = 0
            # Ask the first question immediately
            if st.session_state.questions:
                first_q = st.session_state.questions[0]
                st.session_state.last_question = first_q
                add_message("assistant", f"Q1: {first_q}")
                st.session_state.current_q = 1
        else:
            add_message("assistant", validation)

    # -------------------- TECHNICAL Q&A --------------------
    elif st.session_state.step == "ask_question":
        q_idx = st.session_state.current_q
        last_q = st.session_state.last_question
        validation = validate_with_gemini(last_q, user_input)
        if validation == "VALID":
            st.session_state.answers.append({"question": last_q, "answer": user_input})
            if q_idx < len(st.session_state.questions):
                next_q = st.session_state.questions[q_idx]
                st.session_state.last_question = next_q
                add_message("assistant", f"Q{q_idx+1}: {next_q}")
                st.session_state.current_q += 1
            else:
                add_message("assistant", "✅ That’s all the questions I had. Thank you for your responses! "
                            "Our team will review and reach out to you soon.")
                st.session_state.step = "end"
        else:
            add_message("assistant", validation)

    st.rerun()
