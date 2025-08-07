# api_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI(title="Ollama Chandler Bing API")

# Configuration for your Ollama model
OLLAMA_HOST = "http://localhost:11434" # Default Ollama host
OLLAMA_MODEL_NAME = "chandler-bing" # The name you gave your model in Ollama

# Define the chat template and system prompt based on your Modelfile
# This is crucial for the model to understand the input format it was finetuned on.
# Ensure this matches your Modelfile's TEMPLATE and SYSTEM parameters exactly.
SYSTEM_PROMPT = "Below are some instructions that describe some tasks. Write responses that appropriately complete each request."
CHAT_TEMPLATE = """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>{{ end }}{{ if .Prompt }}
<|im_start|>user
{{ .Prompt }}<|im_end|>{{ end }}
<|im_start|>assistant
{{ .Response }}<|im_end|>"""

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    message: str
    history: list[dict] = [] # Optional chat history for context

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ollama(request: ChatRequest):
    """
    Receives a chat message and forwards it to the Ollama model,
    applying the specific chat template and system prompt.
    """
    try:
        # Construct the messages list for Ollama, including the system prompt
        # and previous chat history.
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add historical messages from the Streamlit app
        for msg in request.history:
            messages.append(msg)

        # Add the current user message
        messages.append({"role": "user", "content": request.message})

        # Prepare the payload for the Ollama API
        payload = {
            "model": OLLAMA_MODEL_NAME,
            "messages": messages,
            "stream": False, # We want the full response at once
            "options": {
                "temperature": 1.5, # Match your Modelfile's temperature
                "min_p": 0.1,       # Match your Modelfile's min_p
                # Add other parameters from your Modelfile's PARAMETER section if needed
            }
        }

        # Make the request to the Ollama API
        ollama_response = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload)
        ollama_response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        response_data = ollama_response.json()

        # Extract the content from the Ollama response
        if response_data and "message" in response_data and "content" in response_data["message"]:
            model_response = response_data["message"]["content"]
            return ChatResponse(response=model_response)
        else:
            raise HTTPException(status_code=500, detail="Invalid response format from Ollama.")

    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama at {OLLAMA_HOST}. Is Ollama running?")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Ollama: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# To run this server:
# 1. Save the code as api_server.py
# 2. Open your terminal in the same directory
# 3. Run: uvicorn api_server:app --reload --port 8000
#    The --reload flag is useful for development as it restarts the server on code changes.
#    --port 8000 specifies the port.
