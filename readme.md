#  sarcastic-chandler-bing-chatbot

<p align="center">
        <>
    <h1 align="center">Chandler Bing LLM</h1>
    <h3 align="center">Make Qwen3-0.6B talk in Chandler Bing style</h3>
</p>
## Table of Contents

- [1. Introduction](#introduction)
- [2. Project Design](#project-design)
    - [2.1 Dataset Creation](#dataset-creation)
    - [2.2 Model Fine-tuning](#model-fine-tuning)
    - [2.3 Create Ollama model](#create-ollama-model)
- [3. Configuration](#configuration)
- [4. Running the project](#running-the-project)
    - [4.1 Create the dataset](#create-the-dataset)
    - [4.2 Configure your Lambda Labs account](#configure-your-lambda-labs-account)
    - [4.3 Create an SSH key](#create-an-ssh-key)
    - [4.4 Launching a Lambda Labs instance](#launching-a-lambda-labs-instance)
    - [4.5 Fetching the instance IP](#fetching-the-instance-ip)
    - [4.6 Syncing the local filesystem with the remote one](#syncing-the-local-filesystem-with-the-remote-one)
    - [4.7 Configuring Lambda Labs instance](#configuring-lambda-labs-instance)
    - [4.8 Finetuning the model](#finetuning-the-model)
    - [4.9 Terminate the Lambda Labs instance   ](#terminate-the-lambda-labs-instance)
    - [4.10 Creating the Ollama model](#creating-the-ollama-model)
- [5. Contributing](#contributing)



## Introduction

This project shows you how to make **Llama 3.1 8B** speak like **Rick Sanchez** by:

- Creating a custom dataset from Chandler Bing transcripts in ShareGPT format
- Finetuning the model using [Unsloth](https://unsloth.ai/)'s optimizations on Google Colab
- Converting and deploying the model to [Ollama](https://ollama.com/) for local use



## Project Design 

<p align="center">
        <img alt="logo" src="img/project_design.png" width=600 />
</p>

The project can be divided into three main parts:

1. **Dataset creation**: Creating a custom dataset from Rick and Morty transcripts in ShareGPT format.
2. **Model finetuning**: Finetuning the model using Unsloth's optimizations on Google Colab's T4 GPU.    
3. **Model deployment**: Converting and deploying the model to Ollama for local use.

Let's begin with the dataset creation.

---

### Dataset Creation


To train an AI, we need a special kind of dataset. This dataset will tell the AI how to act. In this case, we want the AI to talk like Chandler Bing from Friends, so we will create a dataset using transcripts from the show in a format that looks like a chat conversation

This dataset will be placed in same location as finetune.py file when finetunging the model in Google Colab.

> You have all the code for this part [here](chatbot/src/data_creation.py).


### Model finetuning

<p align="center">
        <img alt="logo" src="img/unsloth.png" width=400 />
</p>

Now that we have the dataset, we can start the finetuning process. We'll use the [Unsloth](https://unsloth.ai/) library to finetune the model. Unsloth is a library that provides a set of optimizations for finetuning LLMs, making the process faster and more efficient.

We are not going to appply a full finetuning, instead, we'll apply a LoRA finetuning. LoRA is a technique that allows us to finetune the model without retraining all the weights. This is a great way to save time and resources, but it's not as accurate as a full finetuning.

Since you might not have access to a local GPU. i am using google colab free version.

<p align="center">
        <img alt="logo" src="img/lambda.png" width=400 />
</p>

> You have all the finetuning code under the [rick_llm](chatbot\src\chandler_llm) folder.

### Model deployment

<p align="center">
        <img alt="logo" src="img/ollama.png" width=400 />
</p>

Once the model is finetuned, we need to convert it to a format that can be used by Ollama. The two files we need are:

- The model file: `gguf`
- The model file: `Modelfile`


These two files will be located under the `ollama_files` folder.

---


## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

This project the way i proceeded there was no need for APP . if in case we are going to use LLM for data preparation (we might have used OPENAI or GROQ based on requirement)

Instead of placing the data file in same folder . we can upload and load the data from hugging face. In these time we need these key below in '.env'.


```bash
OPENAI_API_KEY="PUT_YOUR_OPENAI_API_KEY_HERE"
HUGGINGFACE_TOKEN="PUT_YOUR_HUGGINGFACE_TOKEN_HERE"

```

## Running the project

### Create the dataset (Optional)

The first thing we need to do is to create the dataset. 

to do so run script file  in terminal data_creation.py.

```bash
python data_creation.py
```

This will create the dataset and push it to Hugging Face.

> Don't forget to change the dataset name in the `src/data_creation.py` file!!

once completed we will get this message : 'Data preparation complete'
<p align="center">
        <img alt="logo" src="chatbot\images\data_creation_completion.png" width=600 />
</p>


### Configure your Lambda Labs account

<p align="center">
        <img alt="logo" src="img/lambda_home.png" width=600 />
</p>

You need to go to [Lambda Labs](https://lambdalabs.com/) and create an account. Once you have an account, you can create a new API key. This key will be used to sync the local filesystem with the remote one.

> Don't forget to add the key to your `.env` file.

### Create an SSH key

You need to create an SSH key to be able to sync the local filesystem with the remote one. You can do this with the following command:

```bash
make generate-ssh-key
```

This will create the key and add it to your Lambda Labs account.


### Finetuning the model

To finetune start finetuning copy all fiels in chandler_llm along with processed dataset chandler_finetune_data.jsnol file to colab . 

Remember to save the file and working connect you google drive with colab.

In colab run the below line to install the dependencies. 

        !pip install -q accelerate==0.21.0 peft==0.4.0 bitsandbytes==0.40.2 transformers==4.31.0 trl==0.4.7
        
select T4 GPU for the process and make sure the screen is alive.

        Run the finetune.py to initiate the finetuning

This will start the finetuning process. You can check the progress of the finetuning by checking the logs. 

<p align="center">
        <img alt="logo" src="chatbot\images\finetune.png" width=600 />
</p>


When the finetuning is finished, save both the GGUF and the Modelfile will be saved in the folder.

we further use the downloaded file to run the model locally using ollama

### Creating the Ollama model

Now that we have the GGUF in Hugging Face, we need to download it locally and save  model file and gguf file in same folder(ollama_files).


Now, you can use the Ollama CLI to create the model.

```bash
ollama create chandler_tinyllama -f ollama_files/Modelfile
```

Once the model is created, you can start chatting with your Rick-speaking AI assistant.

```bash
ollama run chandler_tinyllama:latest
```

<p align="center">
        <img alt="logo" src="img/rick_ollama_chat.png" width=600 />
</p>


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


