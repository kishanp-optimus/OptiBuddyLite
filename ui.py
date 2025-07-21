import streamlit as st
import httpx

API_URL = "http://localhost:8000"  # FastAPI should run on this

st.set_page_config(page_title="OptiBuddyLite Chat", page_icon="🤖")

st.title("🤖 OptiBuddyLite - HR Chatbot")

# Session state to store chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    role = "user" if msg["type"] == "human" else "bot"
    with st.chat_message(role):
        st.markdown(msg["content"])

# User input
prompt = st.chat_input("Ask something about HR policy...")

if prompt:
    # Add user message to session state
    st.session_state.messages.append({"type": "human", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send to FastAPI
    with st.chat_message("bot"):
        bot_placeholder = st.empty()
        try:
            with httpx.Client(timeout=20) as client:
                res = client.post(f"{API_URL}/chat", json={"question": prompt})
                res.raise_for_status()
                answer = res.json()["answer"]
        except Exception as e:
            answer = f"❌ Error: {e}"

        bot_placeholder.markdown(answer)
        st.session_state.messages.append({"type": "ai", "content": answer})

# Show full history (optional)
with st.sidebar:
    st.header("📜 Chat History")
    if st.button("Refresh"):
        try:
            with httpx.Client(timeout=10) as client:
                res = client.get(f"{API_URL}/history")
                res.raise_for_status()
                history = res.json()["history"]
            for m in history:
                st.text(f"{m['type'].upper()}: {m['content']}")
        except Exception as e:
            st.error(f"Failed to load history: {e}")
