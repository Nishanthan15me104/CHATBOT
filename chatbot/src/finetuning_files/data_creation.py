import os
import json
from datasets import load_dataset
from tqdm import tqdm
import traceback

# Define the system message for Chandler Bing
CHANDLER_SYSTEM_PROMPT = """You are Chandler Bing from the TV show Friends. You are notoriously sarcastic, witty, and often use humor as a defense mechanism to cope with awkwardness or insecurity. You excel at one-liners, dry wit, and rhetorical questions. Don't shy away from self-deprecating jokes or pointing out the obvious with an ironic twist. You mean well, even if your humor sometimes lands awkwardly."""


def load_chandler_dataset():
    """
    Loads the Friends Chandler Bing sarcasm dataset from Hugging Face Hub.

    Returns:
        datasets.Dataset: The 'train' split of the dataset containing
                          Chandler's quotes and context.
    """
    print("Loading Chandler Bing dataset...", flush=True)
    try:
        # Assuming 'instruct' config is the correct one based on previous successful loads
        dataset_dict = load_dataset("yl2342/friends_chandler_bing_sarcasm", "default")
        train_ds = dataset_dict['train']
        print(f"Number of rows in raw dataset: {len(train_ds)}", flush=True)
        return train_ds
    except Exception as e:
        print(f"Error loading dataset: {e}", flush=True)
        traceback.print_exc()
        return None # Return None if loading fails


def prepare_chandler_data_for_finetuning(dataset):
    """
    Prepares the raw Chandler Bing dataset into a list of conversation turns
    suitable for fine-tuning.

    Args:
        dataset (datasets.Dataset): The input dataset containing 'Context'
                                    and 'Chandler_quote' columns.

    Returns:
        list: A list of dictionaries, where each dictionary represents a
              conversation turn in the format:
              [
                  {"from": "system", "value": system_prompt},
                  {"from": "human", "value": context},
                  {"from": "gpt", "value": chandler_quote}
              ]
              Returns None if input dataset is invalid.
    """
    if dataset is None:
        return None

    print("Preparing fine-tuning conversation pairs...", flush=True)
    formatted_conversations = []
    try:
        for row in tqdm(dataset):
            human_message = {
                "from": "human",
                "value": row['Context'].strip()
            }
            gpt_message = {
                "from": "gpt",
                "value": row['Chandler_quote'].strip()
            }
            conversation_turn = [
                {"from": "system", "value": CHANDLER_SYSTEM_PROMPT},
                human_message,
                gpt_message
            ]
            formatted_conversations.append(conversation_turn)
        print(f"Number of formatted conversation pairs: {len(formatted_conversations)}", flush=True)
        return formatted_conversations
    except KeyError as e:
        print(f"KeyError: Missing expected column in dataset. Please check column names. Error: {e}", flush=True)
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"Error preparing data: {e}", flush=True)
        traceback.print_exc()
        return None


def save_formatted_data_to_jsonl(data_list, output_file_path="chandler_finetune_data1.jsonl"):
    """
    Saves a list of formatted conversation turns to a JSON Lines (.jsonl) file.

    Args:
        data_list (list): The list of conversation turns to save.
        output_file_path (str): The path to the output JSONL file.

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    if data_list is None:
        print("No data to save.", flush=True)
        return False


    print(f"Saving formatted data to {output_file_path}...", flush=True)
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for entry in tqdm(data_list, desc="Writing JSONL"):
                json.dump({"messages": entry}, f, ensure_ascii=False)
                f.write('\n')
        print(f"Formatted data saved to {output_file_path}", flush=True)
        print(f"Total entries written: {len(data_list)}", flush=True)
        return True
    except Exception as e:
        print(f"Error saving data to JSONL: {e}", flush=True)
        traceback.print_exc()
        return False


def main():
    print(f"Current working directory: {os.getcwd()}", flush=True)

    # Step 1: Load the dataset
    raw_dataset = load_chandler_dataset()
    if raw_dataset is None:
        print("Exiting due to dataset loading failure.", flush=True)
        return

    # Step 2: Prepare the data for fine-tuning
    formatted_data = prepare_chandler_data_for_finetuning(raw_dataset)
    if formatted_data is None:
        print("Exiting due to data preparation failure.", flush=True)
        return
    
    # Optional: Print first few formatted entries for verification
    print("\n--- First 3 formatted data entries (for verification) ---", flush=True)
    for i in range(min(3, len(formatted_data))):
        print(json.dumps(formatted_data[i], indent=2), flush=True)
        print("-" * 40, flush=True)


    # Step 3: Save the formatted data to a JSONL file
    success = save_formatted_data_to_jsonl(formatted_data, "chandler_finetune_data.jsonl")
    
    if success:
        print("Data preparation complete!", flush=True)
    else:
        print("Data preparation failed.", flush=True)


if __name__ == "__main__":
    main()