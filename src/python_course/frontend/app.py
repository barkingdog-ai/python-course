import uuid

import requests
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

SUCCESS = 200
TIME_OUT = 20

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
        "message": user_input,
        "language": st.session_state.language,
        "thread_id": st.session_state.thread_id,
    }

    try:
        response = requests.post(
            "http://localhost:8000/chat", json=payload, timeout=TIME_OUT
        )
        if response.status_code == SUCCESS:
            result = response.json()

            # c. Update thread ID if new
            st.session_state.thread_id = result.get(
                "thread_id", st.session_state.thread_id
            )

            # d. Show assistant response
            ai_msg = AIMessage(content=result["response"])
            st.session_state.messages.append(ai_msg)

            with st.chat_message("assistant"):
                st.markdown(ai_msg.content)
        else:
            st.error("API Error: " + response.text)

    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {e}")
