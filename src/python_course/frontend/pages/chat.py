import uuid

import httpx
import requests
import streamlit as st

SUCCESS = 200
TIME_OUT = 30
BACKEND_URL = "http://localhost:8000/chat"

st.title("🤓 LangGraph Chatbot")

# Session state for chat history
if "messages_chat" not in st.session_state:
    st.session_state.messages_chat = []
# Session state to persist thread ID
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
# Session state for language
if "language" not in st.session_state:
    st.session_state.language = "English"  # Default


def update_language() -> None:
    pass


# Session Language
# Sidebar for language
st.sidebar.title("Settings")
st.sidebar.selectbox(
    "Preferred Language:",
    ["English", "中文", "Español", "Français", "Deutsch"],
    key="language",
    on_change=update_language,
)

# Sidebar for new conversation
if st.sidebar.button("Start New Conversation"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.messages = []

# Show full chat history once
for role, message in st.session_state.messages_chat:
    with st.chat_message(role):
        st.markdown(message)

user_input = st.chat_input("Ask anything")

if user_input:
    # Show user message immediately
    st.session_state.messages_chat.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # Send to backend
        payload = {
            "messages": user_input,
            "language": st.session_state.language,
            "thread_id": st.session_state.thread_id,
        }

        assistant_reply = ""
        try:
            response = httpx.post(
                "http://localhost:8000/chat", json=payload, timeout=TIME_OUT
            )
            response.raise_for_status()
            data = response.json()

            assistant_reply = data.get("response", "No response")
            st.session_state.messages_chat.append(("assistant", assistant_reply))

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")

        st.markdown(assistant_reply)
