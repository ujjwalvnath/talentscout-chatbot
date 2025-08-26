import streamlit as st
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("TalentScout Hiring Assistant 🤖")

# Initialize state
if "step" not in st.session_state:
    st.session_state.step = "greeting"
    st.session_state.candidate = {}
    st.session_state.questions = []
    st.session_state.current_q = 0
    st.session_state.answers = []

def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-1.5-flash",  # or gemini-2.0-flash
        contents=prompt
    )
    return response.text.strip()

def bot_say(text):
    st.markdown(f"**Assistant:** {text}")

def user_say(text):
    st.markdown(f"**You:** {text}")

# Greeting
if st.session_state.step == "greeting":
    bot_say("Hello! I'm TalentScout Assistant. I’ll gather some details from you, "
            "then ask technical questions based on your skills. "
            "Type 'exit' anytime to end.")
    st.session_state.step = "ask_name"

# Info gathering sequence
elif st.session_state.step == "ask_name":
    name = st.text_input("Please enter your Full Name:", key="name")
    if name:
        if name.lower() in ["exit", "quit", "bye"]:
            st.session_state.step = "end"
            st.experimental_rerun()
        st.session_state.candidate["name"] = name
        user_say(name)
        st.session_state.step = "ask_email"
        st.experimental_rerun()

elif st.session_state.step == "ask_email":
    email = st.text_input("Please enter your Email:", key="email")
    if email:
        if email.lower() in ["exit", "quit", "bye"]:
            st.session_state.step = "end"
            st.experimental_rerun()
        st.session_state.candidate["email"] = email
        user_say(email)
        st.session_state.step = "ask_phone"
        st.experimental_rerun()

elif st.session_state.step == "ask_phone":
    phone = st.text_input("Please enter your Phone Number:", key="phone")
    if phone:
        if phone.lower() in ["exit", "quit", "bye"]:
            st.session_state.step = "end"
            st.experimental_rerun()
        st.session_state.candidate["phone"] = phone
        user_say(phone)
        st.session_state.step = "ask_exp"
        st.experimental_rerun()

elif st.session_state.step == "ask_exp":
    exp = st.text_input("Years of Experience:", key="exp")
    if exp:
        if exp.lower() in ["exit", "quit", "bye"]:
            st.session_state.step = "end"
            st.experimental_rerun()
        st.session_state.candidate["experience"] = exp
        user_say(exp)
        st.session_state.step = "ask_position"
        st.experimental_rerun()

elif st.session_state.step == "ask_position":
    pos = st.text_input("Desired Position(s):", key="pos")
    if pos:
        if pos.lower() in ["exit", "quit", "bye"]:
            st.session_state.step = "end"
            st.experimental_rerun()
        st.session_state.candidate["position"] = pos
        user_say(pos)
        st.session_state.step = "ask_location"
        st.experimental_rerun()

elif st.session_state.step == "ask_location":
    loc = st.text_input("Current Location:", key="loc")
    if loc:
        if loc.lower() in ["exit", "quit", "bye"]:
            st.session_state.step = "end"
            st.experimental_rerun()
        st.session_state.candidate["location"] = loc
        user_say(loc)
        st.session_state.step = "ask_tech"
        st.experimental_rerun()

elif st.session_state.step == "ask_tech":
    tech = st.text_input("Tech Stack (e.g., Python, Django, React):", key="tech")
    if tech:
        if tech.lower() in ["exit", "quit", "bye"]:
            st.session_state.step = "end"
            st.experimental_rerun()
        st.session_state.candidate["tech_stack"] = tech
        user_say(tech)
        # Generate questions with Gemini
        prompt = f"Generate 3–5 clear and concise technical interview QUESTIONS only (no answers, no explanations) for: {tech}."
        q_text = ask_gemini(prompt)
        st.session_state.questions = [q.strip("- ").strip() for q in q_text.split("\n") if q.strip()]
        st.session_state.step = "ask_question"
        st.experimental_rerun()

# Interactive Q&A
elif st.session_state.step == "ask_question":
    q_idx = st.session_state.current_q
    if q_idx < len(st.session_state.questions):
        question = st.session_state.questions[q_idx]
        bot_say(f"Q{q_idx+1}: {question}")
        ans = st.text_area("Your Answer:", key=f"ans_{q_idx}")
        if st.button("Submit Answer", key=f"submit_{q_idx}") and ans:
            if ans.lower() in ["exit", "quit", "bye"]:
                st.session_state.step = "end"
                st.experimental_rerun()
            user_say(ans)
            st.session_state.answers.append({"question": question, "answer": ans})
            bot_say("Thanks for your response! Let's move to the next question.")
            st.session_state.current_q += 1
            st.experimental_rerun()
    else:
        st.session_state.step = "end"
        st.experimental_rerun()

# End
elif st.session_state.step == "end":
    bot_say("✅ Thank you for your time! Your responses have been recorded. "
            "Our team will review and reach out to you with next steps.")
    st.stop()
