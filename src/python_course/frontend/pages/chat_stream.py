import uuid

import httpx
import streamlit as st
from httpx_sse import connect_sse

EVENT_TYPE = "chunk"
FINISH = "end"
TIMEOUT = 30

st.title("Streaming Chatbot")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
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

# Display chat history
for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(message)

user_input = st.chat_input("Ask anything")

if user_input:
    # Show user message immediately
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send to backend
    payload = {
        "messages": user_input,
        "language": st.session_state.language,
        "thread_id": st.session_state.thread_id,
    }

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

    with httpx.Client(timeout=TIMEOUT) as client:
        with connect_sse(
            client, "POST", "http://localhost:8000/chat/stream", json=payload
        ) as event_source:
            for sse in event_source.iter_sse():
                if sse.event == EVENT_TYPE:
                    token = sse.data
                    full_response += token
                    message_placeholder.markdown(full_response)
                elif sse.event == FINISH:
                    break
    # After streaming finishes, save full assistant reply to session
    st.session_state.messages.append(("assistant", full_response))
