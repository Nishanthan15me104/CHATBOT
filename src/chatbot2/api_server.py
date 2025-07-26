# api_server.py - Using In-Memory Chat History (NOT PERSISTENT)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel # Corrected: BaseModel (was Baseodel)
import requests
import json
import os
from datetime import datetime
# No sqlite3 or firebase_admin needed for in-memory

app = FastAPI(title="Ollama Chandler Bing API with In-Memory History")

# --- In-Memory Storage ---
# This dictionary will store chat histories.
# Key: user_id (str)
# Value: list of dicts, e.g., [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
chat_histories = {}

# --- Ollama Configuration ---
OLLAMA_HOST = "http://localhost:11434" # Default Ollama host
OLLAMA_MODEL_NAME = "chandler-bing" # The name you gave your model in Ollama

# Define the chat template and system prompt based on your Modelfile
SYSTEM_PROMPT = "Below are some instructions that describe some tasks. Write responses that appropriately complete each request."
CHAT_TEMPLATE = """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>{{ end }}{{ if .Prompt }}
<|im_start|>user
{{ .Prompt }}<|im_end|>{{ end }}
<|im_start|>assistant
{{ .Response }}<|im_end|>"""

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    user_id: str
    message: str

class Message(BaseModel): # Corrected: BaseModel (was Baseodel)
    """Model for a single chat message."""
    role: str
    content: str
    timestamp: str # ISO format string

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    response: str

class HistoryResponse(BaseModel):
    """Response model for fetching chat history."""
    history: list[Message]

# --- Helper Functions for In-Memory Storage ---
async def load_chat_history_from_memory(user_id: str) -> list[dict]:
    """Loads chat history for a user from in-memory storage."""
    return chat_histories.get(user_id, [])

async def save_message_to_memory(user_id: str, role: str, content: str):
    """Saves a single message to in-memory storage."""
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

async def clear_chat_history_in_memory(user_id: str):
    """Clears the entire chat history for a given user_id in in-memory storage."""
    if user_id in chat_histories:
        del chat_histories[user_id]

# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat_with_ollama(request: ChatRequest):
    """
    Receives a chat message, loads full history from in-memory,
    forwards to Ollama, and saves the new messages to in-memory.
    """
    user_id = request.user_id
    current_user_message = request.message

    try:
        # 1. Load full historical context from in-memory
        full_history = await load_chat_history_from_memory(user_id)

        # 2. Construct messages list for Ollama, including system prompt and full history
        messages_for_ollama = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add all historical messages
        for msg in full_history:
            messages_for_ollama.append({"role": msg["role"], "content": msg["content"]}) # Only role and content needed for LLM

        # Add the current user message to the context for Ollama
        messages_for_ollama.append({"role": "user", "content": current_user_message})

        # Prepare the payload for the Ollama API
        payload = {
            "model": OLLAMA_MODEL_NAME,
            "messages": messages_for_ollama,
            "stream": False, # We want the full response at once
            "options": {
                "temperature": 0.8, # Adjusted for more consistent persona
                "min_p": 0.05,      # Adjusted for slightly more focused responses
                # Add other parameters from your Modelfile's PARAMETER section if needed
            }
        }

        # Make the request to the Ollama API
        ollama_response = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload)
        ollama_response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        response_data = ollama_response.json()

        # Extract the content from the Ollama response
        if response_data and "message" in response_data and "content" in response_data["message"]:
            model_response_content = response_data["message"]["content"]

            # 3. Save both user and assistant messages to in-memory
            await save_message_to_memory(user_id, "user", current_user_message)
            await save_message_to_memory(user_id, "assistant", model_response_content)

            return ChatResponse(response=model_response_content)
        else:
            raise HTTPException(status_code=500, detail="Invalid response format from Ollama.")

    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama at {OLLAMA_HOST}. Is Ollama running?")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/history/{user_id}", response_model=HistoryResponse)
async def get_chat_history(user_id: str):
    """Retrieves the full chat history for a given user_id from in-memory."""
    try:
        history_data = await load_chat_history_from_memory(user_id)
        # Convert to Message Pydantic model for response validation
        formatted_history = [
            Message(role=msg["role"], content=msg["content"], timestamp=msg["timestamp"])
            for msg in history_data
        ]
        return HistoryResponse(history=formatted_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {e}")

@app.post("/clear_history/{user_id}")
async def clear_chat_history(user_id: str):
    """Clears the entire chat history for a given user_id in in-memory storage."""
    try:
        await clear_chat_history_in_memory(user_id)
        return {"message": f"Chat history for user {user_id} cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {e}")

# To run this server:
# 1. Save the code as api_server.py
# 2. Ensure Ollama is running and your 'chandler-bing' model is loaded.
# 3. Ensure you have the required Python packages: pip install fastapi uvicorn requests
# 4. Open your terminal in the same directory as api_server.py
# 5. Run: uvicorn api_server:app --reload --port 8000
