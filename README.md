# TalentScout Hiring Assistant 🤖

An AI-powered hiring assistant built with Streamlit and Gemini API.  
It collects candidate details and generates technical questions based on their tech stack.

---

## 🚀 Features
- Collects candidate info (Name, Email, Tech Stack, etc.)
- Generates 3–5 interview questions for declared technologies
- Clean, step-by-step Streamlit UI
- Powered by Google Gemini API

---

## 🛠️ Setup & Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/talentscout-chatbot.git
   cd talentscout-chatbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Export your Gemini API key:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

4. Run the chatbot:
   ```bash
   streamlit run chatbot_gemini.py
   ```

---

## 🌐 Deployment (Streamlit Cloud)

1. Push repo to GitHub.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect the repo and deploy.
4. Add your API key in **App → Settings → Secrets**:
   ```toml
   GEMINI_API_KEY="your_api_key_here"
   ```

---

## 📸 Demo
- Record a Loom video walkthrough showing:
  1. Opening the chatbot.
  2. Entering candidate details (Name, Email, Tech Stack).
  3. Displaying the generated technical questions.
  4. Graceful exit message.

(Add Loom video link or screenshots here.)
