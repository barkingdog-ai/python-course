import uuid

import requests
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

SUCCESS = 200
TIME_OUT = 20
BACKEND_URL = "http://localhost:8000/chat/stream"

st.title("🤓 LangGraph Chatbot")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Session state to persist thread ID
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
# Session state for language
if "language" not in st.session_state:
    st.session_state.language = "English"  # Default


# Session Language
# Sidebar for language
st.sidebar.title("Settings")
st.sidebar.selectbox(
    "Preferred Language:",
    ["English", "中文", "Español", "Français", "Deutsch"],
    key="language",
)

# Sidebar for new conversation
if st.sidebar.button("Start New Conversation"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

user_input = st.chat_input("Ask anything")

if user_input:
    # Show user message immediately
    st.session_state.messages.append(HumanMessage(content=user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to backend
    payload = {
        "messages": user_input,
        "language": st.session_state.language,
        "thread_id": st.session_state.thread_id,
    }

    response_holder = st.empty()
    response_text = ""
    try:
        with requests.post(
            BACKEND_URL, json=payload, stream=True, timeout=TIME_OUT
        ) as response:
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    chunk = line.removeprefix("data: ").strip()
                    if chunk == "[DONE]":
                        break
                    response_text += chunk
                    response_holder.markdown(response_text)

        ai_msg = AIMessage(content=response_text)
        st.session_state.messages.append(ai_msg)

    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
