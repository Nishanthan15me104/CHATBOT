import os

# import dotenv

from utils import initialize_model, setup_peft_model
from trainer import ModelTrainer

# dotenv.load_dotenv() not needed 


def main():
    # Initialize model
    model, tokenizer = initialize_model()
    model = setup_peft_model(model)

    # Train model
    trainer = ModelTrainer(model, tokenizer)
    trainer_instance = trainer.setup_trainer()
    trainer_instance.train()

    # save the files 
    save_directory = "./fine_tuned_chandler_model"
    os.makedirs(save_directory, exist_ok=True)

   
    gguf_save_directory = "./chandler_gguf_model"
    os.makedirs(gguf_save_directory, exist_ok=True)
    model.save_pretrained_gguf(gguf_save_directory, tokenizer, quantization_method="q4_k_m")
    print(f"GGUF model saved to {gguf_save_directory}")


if __name__ == "__main__":
    main()