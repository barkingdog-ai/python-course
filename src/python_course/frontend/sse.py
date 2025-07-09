# streamlit_sse_client.py
import httpx
import streamlit as st

st.title("💌 Gemini_Clown")
# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Gemini something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_text = ""
        placeholder = st.empty()

        try:
            with httpx.stream(
                "POST",
                "http://localhost:8000/chat/stream/",
                json={"message": user_input},
                timeout=30,
            ) as response:
                for line in response.iter_lines():
                    if line.startswith("data:"):
                        chunk = line.removeprefix("data: ").strip()
                        if chunk == "[DONE]":
                            break
                        response_text += chunk
                        placeholder.markdown(response_text)
        except httpx.RequestError as e:
            st.error(f"Error: {e}")
            response_text = "[Error]"

        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )
