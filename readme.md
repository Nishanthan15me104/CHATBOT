#  sarcastic-chandler-bing-chatbot

## Could I BE any more sarcastic?

This project aims to create a chatbot fine-tuned on the personality and sarcasm of Chandler Bing from the TV show *Friends*. It leverages a custom dataset, efficient fine-tuning techniques (Unsloth, LoRA), and a multi-component architecture for interaction.

---

### Project Components

This repository contains several interconnected components that work together to bring the Chandler Bing chatbot to life:

1.  **`data_creation.py`**: Handles the initial data preparation for fine-tuning.
2.  **`constants.py`**: Stores configuration parameters for the model, PEFT (LoRA), and training process.
3.  **`utils.py`**: Contains helper functions for model initialization and PEFT setup.
4.  **`trainer.py`**: Orchestrates the fine-tuning process using the `unsloth` library and Hugging Face `trl`'s `SFTTrainer`.
5.  **`finetune.py`**: The main script to execute the model initialization, training, and saving of the fine-tuned model (including GGUF format for local deployment with Ollama).
6.  **`api_server.py`**: A FastAPI application that acts as a bridge between the Streamlit UI and the local Ollama instance running the Chandler Bing model.
7.  **`streamlit_app.py`**: The interactive web-based chat interface built with Streamlit.

---


