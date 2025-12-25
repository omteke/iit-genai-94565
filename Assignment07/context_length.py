from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
import streamlit as st
load_dotenv()


llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider = "openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_API_KEY")
)
st.title("CHAT BOT")

MAX_MESSAGES = st.sidebar.slider(
    "Context length (last N messages sent to LLM)",
    min_value=1,
    max_value=10,
    value=4
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


user_input = st.chat_input("Ask Anything: ")
if user_input:
    user_msg = {"role": "user", "content": user_input}
    st.session_state .messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(user_input)

    context = (
        st.session_state.messages[:1] +    
        st.session_state.messages[-MAX_MESSAGES:]
    )

    llm_output = llm.invoke(context)
    with st.chat_message("assistant"):
        st.markdown(llm_output.content)
    llm_msg = {"role": "assistant", "content": llm_output.content}
    st.session_state .messages.append(llm_msg)

# Use slider value to decide how many last messages to be sent to LLM
# instead of full conversation. This will limit the "context length".