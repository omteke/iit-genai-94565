import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv

# ======================
# ENV SETUP
# ======================
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

groq_url = "https://api.groq.com/openai/v1/chat/completions"
lmstudio_url = "http://127.0.0.1:1234/v1/chat/completions"

# ======================
# STREAMLIT UI
# ======================
st.set_page_config(page_title="Multi-LLM ChatBot", layout="centered")
st.title("🤖 MULTI-LLM CHATBOT")

st.sidebar.title("Settings")
model_choice = st.sidebar.radio(
    "Choose LLM:",
    ["Groq (Cloud)", "LM Studio (Local)"]
)

# ======================
# SESSION STATE
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# DISPLAY CHAT HISTORY
# ======================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ======================
# USER INPUT
# ======================
user_input = st.chat_input("Ask Anything:")

if user_input:
    # Save user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # ======================
    # REQUEST PAYLOAD
    # ======================
    req_data = {
        "model": "llama-3.3-70b-versatile"
        if model_choice == "Groq (Cloud)"
        else "google/gemma-3-4b",
        "messages": st.session_state.messages
    }

    # ======================
    # SELECT API
    # ======================
    if model_choice == "Groq (Cloud)":
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        url = groq_url
    else:
        headers = {
            "Authorization": "Bearer dummy-key",
            "Content-Type": "application/json"
        }
        url = lmstudio_url

    # ======================
    # MODEL RESPONSE
    # ======================
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(req_data)
            )
            resp_json = response.json()

            if "choices" in resp_json:
                reply = resp_json["choices"][0]["message"]["content"]
            else:
                reply = f"⚠️ Error:\n{resp_json}"

            st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
