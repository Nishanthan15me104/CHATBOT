# streamlit_app.py

import streamlit as st
import requests
import json
import uuid # For generating unique user IDs

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

# --- User ID Management ---
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4()) # Generate a unique ID for the session
st.sidebar.write(f"Your User ID: **`{st.session_state.user_id}`**")
st.sidebar.markdown("*(This ID helps remember your chat history across sessions. Share it if you want to resume on another device, or clear it to start fresh.)*")

# Initialize chat history in session state if not already present
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Load history from API server on app start ---
# Only load if messages are empty (first run or after clear)
if not st.session_state.messages:
    try:
        response = requests.get(f"{API_SERVER_URL}/history/{st.session_state.user_id}")
        response.raise_for_status()
        history_data = response.json()["history"]
        # Convert history data to Streamlit's message format
        st.session_state.messages = [{"role": msg["role"], "content": msg["content"]} for msg in history_data]
        if not st.session_state.messages: # If no history, add initial Chandler message
            st.session_state.messages.append({"role": "assistant", "content": "Could I *be* any more ready to chat?"})
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API server at {API_SERVER_URL} to load history. Is it running?")
        st.session_state.messages.append({"role": "assistant", "content": "Could I *be* any more ready to chat? (P.S. I can't load past conversations right now.)"})
    except Exception as e:
        st.error(f"Error loading history: {e}")
        st.session_state.messages.append({"role": "assistant", "content": "Could I *be* any more ready to chat? (P.S. Had a little trouble loading past conversations.)"})


# Display chat messages from history
chat_display_area = st.container()
with chat_display_area:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message-user"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-assistant"><b>Chandler:</b> {message["content"]}</div>', unsafe_allow_html=True)

# --- Input field for user message (managed with session state for explicit clearing) ---
if "current_input" not in st.session_state:
    st.session_state.current_input = ""

user_input_value = st.text_input(
    "Say something to Chandler...",
    key="user_input_key", # Use a unique key for the widget
    value=st.session_state.current_input # Bind its value to session state
)

# Send button
col1, col2 = st.columns([1, 4])
with col1:
    send_button = st.button("Send")
with col2:
    clear_button = st.button("Clear Chat")

# Handle sending message
if send_button and user_input_value:
    # Add user message to history (temporarily for display)
    st.session_state.messages.append({"role": "user", "content": user_input_value})

    # Prepare payload for the API call - send user_id and current message only
    try:
        with st.spinner("Chandler's thinking..."):
            response = requests.post(
                f"{API_SERVER_URL}/chat",
                json={"user_id": st.session_state.user_id, "message": user_input_value}
            )
            response.raise_for_status()
            chandler_response = response.json()["response"]

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": chandler_response})

    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API server at {API_SERVER_URL}. Is it running?")
    except requests.exceptions.RequestException as e:
        st.error(f"Error from API server: {e}. Check server logs for details.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    # Explicitly clear the input box value in session state
    st.session_state.current_input = ""
    st.rerun() # Rerun to update chat display and clear input

# Handle clearing chat
if clear_button:
    try:
        response = requests.post(f"{API_SERVER_URL}/clear_history/{st.session_state.user_id}")
        response.raise_for_status()
        st.success(response.json()["message"])
        st.session_state.messages = [] # Clear local history
        st.session_state.current_input = "" # Clear input box on clear chat
        st.rerun() # Rerun to update display
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the API server at {API_SERVER_URL} to clear history. Is it running?")
    except requests.exceptions.RequestException as e:
        st.error(f"Error from API server while clearing history: {e}. Check server logs for details.")
    except Exception as e:
        st.error(f"An unexpected error occurred while clearing history: {e}")
