# streamlit_app.py

import streamlit as st
import requests
import json

# Configuration for the FastAPI server
API_SERVER_URL = "http://localhost:8000" # Match the port you run api_server.py on

st.set_page_config(page_title="Could I BE any more sarcastic?", layout="centered")

# Custom CSS for a Friends-like theme and better UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    .main {
        background-color: #f0f2f6; /* Light grey background */
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 10px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .stButton > button {
        background-color: #FFD700; /* Gold/Yellow color, like the frame on Monica's door */
        color: #333;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #FFC107;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .chat-message-user {
        background-color: #e0f7fa; /* Light blue for user */
        padding: 12px 18px;
        border-radius: 15px;
        margin-bottom: 10px;
        align-self: flex-end;
        text-align: right;
        border: 1px solid #b3e5fc;
    }
    .chat-message-assistant {
        background-color: #ffe0b2; /* Light orange for assistant */
        padding: 12px 18px;
        border-radius: 15px;
        margin-bottom: 10px;
        align-self: flex-start;
        text-align: left;
        border: 1px solid #ffcc80;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding-right: 10px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #fff;
        padding: 15px;
    }
    .stAlert {
        border-radius: 10px;
    }
    .stSpinner > div > div {
        color: #FFD700 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("👨‍💻 Chandler Bing Chatbot")
st.markdown("### Could I BE any more sarcastic?")

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
chat_display_area = st.container()
with chat_display_area:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message-user"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-assistant"><b>Chandler:</b> {message["content"]}</div>', unsafe_allow_html=True)

# Input field for user message
user_input = st.text_input("Say something to Chandler...", key="user_input")

# Send button
col1, col2 = st.columns([1, 4])
with col1:
    send_button = st.button("Send")
with col2:
    clear_button = st.button("Clear Chat")

# Handle sending message
if send_button and user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare history for the API call (excluding system prompt)
    api_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages if msg["role"] != "system"]

    try:
        with st.spinner("Chandler's thinking..."):
            # Make request to FastAPI server
            response = requests.post(
                f"{API_SERVER_URL}/chat",
                json={"message": user_input, "history": api_history}
            )
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            chandler_response = response.json()["response"]

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": chandler_response})

    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API server at {API_SERVER_URL}. Is it running?")
    except requests.exceptions.RequestException as e:
        st.error(f"Error from API server: {e}. Check server logs for details.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    # Clear the input box after sending
    st.rerun() # Changed from st.experimental_rerun()

# Handle clearing chat
if clear_button:
    st.session_state.messages = []
    st.rerun() # Changed from st.experimental_rerun()

# Initial prompt/message when the app starts
if not st.session_state.messages:
    st.markdown(f'<div class="chat-message-assistant"><b>Chandler:</b> Could I *be* any more ready to chat?</div>', unsafe_allow_html=True)
