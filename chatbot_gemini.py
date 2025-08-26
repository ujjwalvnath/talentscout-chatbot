import streamlit as st
from google import genai
import pandas as pd
import io

# Initialize Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="TalentScout Chatbot", page_icon="🤖")
st.title("TalentScout Hiring Assistant 🤖")

# -------------------- STATE --------------------
ss = st.session_state
if "chat_history" not in ss:
    ss.chat_history = []
if "step" not in ss:
    ss.step = "greeting"
if "candidate" not in ss:
    ss.candidate = {}
if "questions" not in ss:
    ss.questions = []
if "current_q" not in ss:
    ss.current_q = 0
if "last_question" not in ss:
    ss.last_question = None
if "answers" not in ss:
    ss.answers = []

# -------------------- HELPERS --------------------
def add_message(role, content):
    ss.chat_history.append({"role": role, "content": content})

def show_history():
    for msg in ss.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def is_valid_label(text: str) -> bool:
    return text.strip().upper().startswith("VALID")

def validate_with_gemini(question, answer, q_type="interview"):
    """
    q_type: "info" or "interview"
    Returns the raw model response (either "VALID" or a short polite retry sentence).
    """
    context = "\n".join([f"{m['role']}: {m['content']}" for m in ss.chat_history])

    prompt = f"""
You are TalentScout Assistant, validating a candidate's answer.

Conversation so far:
{context}

Question Type: {q_type}
Question: "{question}"
Candidate's answer: "{answer}"

OUTPUT RULES (important):
- You must output exactly ONE line and nothing else.
- If the answer is acceptable, output the single word: VALID
  - No punctuation, no extra text, no explanation.
- If the answer is not acceptable, output one short polite sentence asking the candidate to retry,
  for example: "This field is required, please provide your full name."
  - Use only one sentence and one line.

VALIDATION LOGIC:

If Question Type is "info" (required fields: Full Name, Email Address, Phone Number,
Years of Experience, Desired Position(s), Current Location, Tech Stack):
- Accept as VALID:
  - Name: accept any non-empty alphabetic string, including single-word names (e.g. "john").
      Also accept common filler/hedging forms like:
      "my name is X", "I am X", "I'm X", "I think my name is X", "my full name is X".
      Treat these as definitive enough and return VALID.
  - Email: contains "@" and at least one dot after the "@" (example: "a@b.com").
  - Phone: contains at least 7 digits (digits may have spaces, +, -).
  - Years of Experience: contains at least one numeric digit OR a short word number ("five").
  - Position / Location / Tech Stack: any non-empty meaningful text; tech stack preferably comma-separated or contains known tech keywords (python, react, django, java, etc.)
- Reject (not valid) if answer is: empty, purely off-topic, gibberish, or one of the skip phrases: "i don't know", "idk", "dont know", "not sure".
- If rejected, reply with a single polite retry sentence (see Output Rules).

If Question Type is "interview":
- If the candidate answers with "I don't know", "idk", "dont know", or "not sure":
  -> Always output exactly: VALID
- Otherwise, accept as VALID if the answer is at least somewhat relevant to the question,
  even if technically wrong or incomplete.
- Reject only if the answer is completely off-topic or nonsense.
- IMPORTANT: Do NOT provide corrections, hints, or explanations for interview answers.
- For relevant but incorrect answers, you must still output exactly: VALID


IMPORTANT:
- Do NOT echo or repeat the candidate's input.
- Do NOT output anything other than what is specified in OUTPUT RULES above.
    """.strip()

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return response.text.strip()



def normalize_field(field_name, raw_answer):
    """Use Gemini to clean and normalize user input for saving."""
    context = f"""
You are a data cleaning assistant for a candidate screening bot.

Extract and return ONLY the core value for the given field.

Field: {field_name}
User input: "{raw_answer}"

Rules:
- For Name: return just the full name (e.g., "Ujjwal V Nath").
- For Email: return only the email address (e.g., "abc@xyz.com").
- For Phone: return digits only, no words (e.g., "9876543210").
- For Years of Experience: return a number only (e.g., "5").
- For Position: return only the job title (e.g., "Software Engineer").
- For Location: return only the location name (e.g., "Bangalore, India").
- For Tech Stack: return a comma-separated list of technologies (e.g., "Python, React, Django").
- Do not include filler phrases like "my name is", "I think", etc.
- Respond with only the cleaned value, no explanations.
    """.strip()

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=context
    )
    return response.text.strip()

def generate_questions(tech_stack,experience):
    techs = [t.strip() for t in tech_stack.split(",") if t.strip()]
    prompt = f"""
You are an interview assistant.

Generate exactly {len(techs)} concise technical interview questions,
one per technology, for the following list: {', '.join(techs)}, considering the experience of {experience} years

Guidelines:
- Each question must directly test knowledge of the technology.
- Each question should stand alone (no colons, no tech name labels only).
- Do NOT output answers, explanations, or just tech names.
Example:
- "What are React hooks and how are they used?"
- "How does FastAPI handle asynchronous requests?"
    """.strip()

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    lines = [q.strip("-•0123456789. ").strip() for q in response.text.split("\n")]
    return [q for q in lines if q and not q.lower().endswith(":")]

# -------------------- SHOW HISTORY --------------------
show_history()

# -------------------- INITIAL GREETING --------------------
if ss.step == "greeting" and not ss.chat_history:
    add_message("assistant",
                "Hello! I'm TalentScout Assistant. I’ll gather some details from you step by step. "
                "Type **exit** anytime to quit.\n\nFirst, what is your **Name**?")
    ss.step = "ask_name"
    st.rerun()

# -------------------- CHAT INPUT --------------------
if user_input := st.chat_input("Type your response..."):
    # Exit condition
    if user_input.lower().strip() in {"exit", "quit", "bye"}:
        add_message("user", user_input)
        add_message("assistant", "✅ Thank you for your time! Your responses have been recorded. Goodbye.")
        ss.step = "end"
        st.rerun()

    add_message("user", user_input)

    # -------------------- INFO GATHERING --------------------
    if ss.step == "ask_name":
        verdict = validate_with_gemini("Full Name", user_input, q_type="info")
        if is_valid_label(verdict):
            ss.candidate["name"] = normalize_field("Full Name", user_input)
            add_message("assistant", "Got it! Please provide your **Email Address**.")
            ss.step = "ask_email"
        else:
            add_message("assistant", verdict)

    elif ss.step == "ask_email":
        verdict = validate_with_gemini("Email Address", user_input, q_type="info")
        if is_valid_label(verdict):
            ss.candidate["email"] = normalize_field("Email Address", user_input)
            add_message("assistant", "Thanks! Now share your **Phone Number**.")
            ss.step = "ask_phone"
        else:
            add_message("assistant", verdict)

    elif ss.step == "ask_phone":
        verdict = validate_with_gemini("Phone Number", user_input, q_type="info")
        if is_valid_label(verdict):
            ss.candidate["phone"] = normalize_field("Phone Number", user_input)
            add_message("assistant", "Noted. How many **Years of Experience** do you have?")
            ss.step = "ask_exp"
        else:
            add_message("assistant", verdict)

    elif ss.step == "ask_exp":
        verdict = validate_with_gemini("Years of Experience", user_input, q_type="info")
        if is_valid_label(verdict):
            ss.candidate["experience"] = normalize_field("Years of Experience", user_input)
            add_message("assistant", "Great! What **Position(s)** are you applying for?")
            ss.step = "ask_position"
        else:
            add_message("assistant", verdict)

    elif ss.step == "ask_position":
        verdict = validate_with_gemini("Desired Position(s)", user_input, q_type="info")
        if is_valid_label(verdict):
            ss.candidate["position"] = normalize_field("Desired Position(s)", user_input)
            add_message("assistant", "Got it. Where is your **Current Location**?")
            ss.step = "ask_location"
        else:
            add_message("assistant", verdict)

    elif ss.step == "ask_location":
        verdict = validate_with_gemini("Current Location", user_input, q_type="info")
        if is_valid_label(verdict):
            ss.candidate["location"] = normalize_field("Current Location", user_input)
            add_message("assistant",
                        "Perfect. Finally, tell me your **Tech Stack** (comma-separated, e.g., Python, Django, React).")
            ss.step = "ask_tech"
        else:
            add_message("assistant", verdict)

    elif ss.step == "ask_tech":
        verdict = validate_with_gemini("Tech Stack", user_input, q_type="info")
        if is_valid_label(verdict):
            ss.candidate["tech_stack"] = normalize_field("Tech Stack", user_input)
            add_message("assistant", "Thanks! Generating some technical questions for you...")
            ss.questions = generate_questions(ss.candidate["tech_stack"],ss.candidate["experience"])
            ss.step = "ask_question"
            ss.current_q = 0
            if ss.questions:
                first_q = ss.questions[0]
                ss.last_question = first_q
                add_message("assistant", f"Q1: {first_q}")
                ss.current_q = 1
            else:
                add_message("assistant", "I couldn't generate questions for that stack. Could you rephrase your tech stack?")
                ss.step = "ask_tech"
        else:
            add_message("assistant", verdict)

    # -------------------- TECHNICAL Q&A --------------------
    elif ss.step == "ask_question":
        verdict = validate_with_gemini(ss.last_question, user_input)
        if is_valid_label(verdict):
            ss.answers.append({"question": ss.last_question, "answer": user_input})
            if ss.current_q < len(ss.questions):
                next_q = ss.questions[ss.current_q]
                ss.last_question = next_q
                add_message("assistant", "Thanks for your response! Here's the next one:")
                add_message("assistant", f"Q{ss.current_q + 1}: {next_q}")
                ss.current_q += 1
            else:
                add_message("assistant", "✅ That’s all the questions I had. Thank you for your responses! "
                                         "Our team will review and reach out to you soon.")
                ss.step = "end"
        else:
            add_message("assistant", verdict)

    st.rerun()


# -------------------- END --------------------
if ss.step == "end" and ss.candidate:
    st.subheader("📋 Interview Summary")

    # Show candidate profile
    st.write("**Candidate Details:**")
    st.json(ss.candidate)

    # Show Q&A
    if ss.answers:
        st.write("**Technical Q&A:**")
        for qa in ss.answers:
            st.markdown(f"- **Q:** {qa['question']}\n  - **A:** {qa['answer']}")

    # Prepare export
    data = {
        "Name": [ss.candidate.get("name", "")],
        "Email": [ss.candidate.get("email", "")],
        "Phone": [ss.candidate.get("phone", "")],
        "Experience (Years)": [ss.candidate.get("experience", "")],
        "Position": [ss.candidate.get("position", "")],
        "Location": [ss.candidate.get("location", "")],
        "Tech Stack": [ss.candidate.get("tech_stack", "")],
        "Q&A": ["; ".join([f"Q: {qa['question']} | A: {qa['answer']}" for qa in ss.answers])]
    }

    df = pd.DataFrame(data)

    # Save to CSV in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    # Download button
    st.download_button(
        label="📥 Download Interview CSV",
        data=csv_bytes,
        file_name=f"{ss.candidate.get('name','candidate')}_interview.csv",
        mime="text/csv"
    )
